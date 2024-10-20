from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from .models import Flashcard
from .VectorDB import store_text, retrieve_diverse_contexts
from .llm import generate_qa_pair
from .ocr import extract_text_from_pdf
import os
import logging
import asyncio

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the directory of the current file
current_dir = os.path.dirname(os.path.realpath(__file__))
# Go up two levels to reach the project root, then into the public directory
frontend_dir = os.path.join(current_dir, "..", "..", "frontend")

# Mount the static files directory
app.mount("/", StaticFiles(directory=frontend_dir), name="static")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Progress tracking
progress = {}

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

CHROMA_DB_PATH = "./chroma_db"

def initialize_chroma_db():
    if not os.path.exists(CHROMA_DB_PATH):
        os.makedirs(CHROMA_DB_PATH)
    
    client = Client(Settings(persist_directory=CHROMA_DB_PATH))
    
    # Check if the collection exists, if not, create it
    if "flashcards" not in client.list_collections():
        client.create_collection("flashcards")
    
    return client

chroma_client = initialize_chroma_db()

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    logger.info(f"Received file upload request: {file.filename}")
    try:
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        logger.info(f"File saved to {file_path}")
        
        file_id = os.path.basename(file_path)
        progress[file_id] = 0
        background_tasks.add_task(process_pdf, file_path, file_id)
        logger.info(f"Background task added for file: {file_id}")
        return JSONResponse(content={"message": "File upload started. Processing in background.", "file_id": file_id})
    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": f"An error occurred during file upload: {str(e)}"}, status_code=500)

async def process_pdf(file_path: str, file_id: str):
    try:
        logger.info(f"Starting to process PDF: {file_path}")
        chunks = extract_text_from_pdf(file_path)
        logger.info(f"Extracted {len(chunks)} chunks from PDF")
        if not chunks:
            logger.warning(f"No text extracted from PDF: {file_path}")
            return
        
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Only process non-empty chunks
                store_text(chunk, {"filename": f"{file_path}_chunk_{i}"})
            progress[file_id] = (i + 1) / total_chunks * 100
            logger.info(f"Processed chunk {i+1}/{total_chunks} for file {file_id}")
        os.remove(file_path)
        logger.info(f"Finished processing PDF: {file_path}")
    except Exception as e:
        logger.error(f"Error processing PDF {file_path}: {str(e)}", exc_info=True)
    finally:
        progress[file_id] = 100

@app.get("/progress/{file_id}")
async def get_progress(file_id: str):
    if file_id not in progress:
        raise HTTPException(status_code=404, detail="File not found")
    return JSONResponse(content={"progress": progress[file_id]})

class FlashcardRequest(BaseModel):
    topic: str
    num_cards: int = 5
    page: Optional[int] = 1

@app.post("/generate_flashcards")
async def generate_flashcards(request: FlashcardRequest):
    logger.debug(f"Received request: {request}")
    try:
        contexts = retrieve_diverse_contexts(request.topic, request.num_cards * 2)
        logger.debug(f"Retrieved {len(contexts)} contexts")
        
        if not contexts:
            logger.warning("No contexts found for the given topic")
            return JSONResponse(content={"error": "No relevant content found for the given topic."}, status_code=404)

        flashcards = []
        used_questions = set()
        cards_per_page = 10
        start_index = (request.page - 1) * cards_per_page
        end_index = start_index + cards_per_page

        for context in contexts[start_index:end_index]:
            qa_pair = generate_qa_pair(context)
            logger.debug(f"Generated QA pair: {qa_pair}")
            if qa_pair is not None:
                question, answer = qa_pair
                if question and answer and question not in used_questions:
                    flashcards.append({"question": question, "answer": answer})
                    used_questions.add(question)
            
            if len(flashcards) >= request.num_cards:
                break

        if not flashcards:
            logger.warning("Failed to generate any flashcards")
            return JSONResponse(content={"error": "Failed to generate any flashcards. The AI model might be having difficulties. Please try again with a different topic or upload more diverse content."}, status_code=500)

        total_pages = -(-len(contexts) // cards_per_page)  # Ceiling division
        logger.info(f"Generated {len(flashcards)} flashcards")
        return JSONResponse(content={
            "flashcards": flashcards,
            "current_page": request.page,
            "total_pages": total_pages
        })

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": f"An error occurred while generating flashcards: {str(e)}"}, status_code=500)
