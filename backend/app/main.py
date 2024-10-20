from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import logging
import asyncio
import traceback

# Assuming these modules exist in your project
# If they don't, you'll need to implement or mock them
from .models import Flashcard
from .VectorDB import store_text, retrieve_diverse_contexts
from .llm import generate_qa_pair
from .ocr import extract_text_from_pdf

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
# Go up two levels to reach the project root, then into the frontend directory
frontend_dir = os.path.join(current_dir, "..", "..", "frontend")

# Mount the static files directory
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Progress tracking
progress = {}

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.post("/api/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    logger.info(f"Received file upload request: {file.filename}")
    try:
        # Instead of saving the file, let's just read its content
        content = await file.read()
        file_size = len(content)
        logger.info(f"File size: {file_size} bytes")

        if file_size > 4 * 1024 * 1024:  # 4MB limit
            raise ValueError("File size exceeds 4MB limit")

        # Generate a unique file ID without actually saving the file
        file_id = f"{file.filename}_{os.urandom(8).hex()}"
        progress[file_id] = 0

        # Add background task without actually processing the file for now
        background_tasks.add_task(dummy_process, file_id)
        logger.info(f"Background task added for file: {file_id}")
        
        response_data = {"message": "File upload started. Processing in background.", "file_id": file_id}
        logger.info(f"Sending response: {response_data}")
        return JSONResponse(content=response_data)
    except ValueError as ve:
        logger.error(f"Value error: {str(ve)}")
        return JSONResponse(status_code=400, content={"error": str(ve)})
    except Exception as e:
        logger.error(f"Error during file upload: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500, content={"error": f"An error occurred during file upload: {str(e)}"})

async def dummy_process(file_id: str):
    # Simulate processing without actually doing anything
    for i in range(10):
        progress[file_id] = i * 10
        await asyncio.sleep(1)
    progress[file_id] = 100

@app.get("/api/progress/{file_id}")
async def get_progress(file_id: str):
    if file_id not in progress:
        raise HTTPException(status_code=404, detail="File not found")
    return {"progress": progress[file_id]}

class FlashcardRequest(BaseModel):
    topic: str
    num_cards: int = 5
    page: Optional[int] = 1

@app.post("/api/generate_flashcards", response_model=dict)
async def generate_flashcards(request: FlashcardRequest):
    logger.debug(f"Received request: {request}")
    try:
        contexts = retrieve_diverse_contexts(request.topic, request.num_cards * 2)
        logger.debug(f"Retrieved {len(contexts)} contexts")
        
        if not contexts:
            logger.warning("No contexts found for the given topic")
            raise HTTPException(status_code=404, detail="No relevant content found for the given topic.")

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
                    flashcards.append(Flashcard(question=question, answer=answer))
                    used_questions.add(question)
            
            if len(flashcards) >= request.num_cards:
                break

        if not flashcards:
            logger.warning("Failed to generate any flashcards")
            raise HTTPException(status_code=500, detail="Failed to generate any flashcards. The AI model might be having difficulties. Please try again with a different topic or upload more diverse content.")

        total_pages = -(-len(contexts) // cards_per_page)  # Ceiling division
        logger.info(f"Generated {len(flashcards)} flashcards")
        return {
            "flashcards": flashcards,
            "current_page": request.page,
            "total_pages": total_pages
        }

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred while generating flashcards: {str(e)}")

@app.get("/api/test")
async def test_endpoint():
    return {"message": "API is working"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
