from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .models import Flashcard
from .VectorDB import store_text, retrieve_context, retrieve_diverse_contexts
from .llm import generate_qa_pair
from .ocr import extract_text_from_pdf
import os

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

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_path = f"/tmp/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(contents)
        
        text = extract_text_from_pdf(file_path)
        store_text(text, {"filename": file.filename})
        
        os.remove(file_path)  # Clean up the temporary file
        return {"message": "File processed successfully"}
    except Exception as e:
        return {"error": str(e)}


from fastapi import HTTPException
from pydantic import BaseModel
from typing import List

class FlashcardRequest(BaseModel):
    topic: str
    num_cards: int = 5

class Flashcard(BaseModel):
    question: str
    answer: str

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/generate_flashcards", response_model=dict)
async def generate_flashcards(request: FlashcardRequest):
    logger.debug(f"Received request: {request}")
    try:
        contexts = retrieve_diverse_contexts(request.topic, request.num_cards)
        logger.debug(f"Retrieved {len(contexts)} contexts")
        
        if not contexts:
            logger.warning("No contexts found for the given topic")
            raise HTTPException(status_code=404, detail="No relevant content found for the given topic.")

        flashcards = []
        used_questions = set()

        # Attempt to generate up to request.num_cards flashcards
        attempts = 0
        max_attempts = request.num_cards * 3  # Allow for multiple attempts per desired card

        while len(flashcards) < request.num_cards and attempts < max_attempts:
            context = contexts[attempts % len(contexts)]  # Cycle through available contexts
            logger.debug(f"Processing context: {context[:100]}...")  # Log first 100 chars of context
            
            qa_pair = generate_qa_pair(context)
            logger.debug(f"Generated QA pair: {qa_pair}")
            
            if qa_pair is not None:
                question, answer = qa_pair
                if question and answer and question not in used_questions:
                    flashcards.append(Flashcard(question=question, answer=answer))
                    used_questions.add(question)
            
            attempts += 1

        if not flashcards:
            logger.warning("Failed to generate any flashcards")
            raise HTTPException(status_code=500, detail="Failed to generate any flashcards. Please try again or upload more diverse content.")

        logger.info(f"Generated {len(flashcards)} flashcards")
        return {"flashcards": flashcards}

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")