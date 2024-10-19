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


@app.post("/generate_flashcards")
async def generate_flashcards(num_cards: int = 5):
    contexts = retrieve_diverse_contexts(num_cards)
    flashcards = []
    used_questions = set()

    for context in contexts:
        for _ in range(3):  # Try up to 3 times to get a unique question
            qa_pair = generate_qa_pair(context)
            if qa_pair is None:
                continue
            question, answer = qa_pair
            if question and answer and question not in used_questions:
                flashcards.append(Flashcard(question=question, answer=answer))
                used_questions.add(question)
                break

    if not flashcards:
        return {"error": "No flashcards could be generated. Please try again or upload more diverse content."}

    return {"flashcards": flashcards}