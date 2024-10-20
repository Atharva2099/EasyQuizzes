# backend/app/models.py
from pydantic import BaseModel

class Flashcard(BaseModel):
    question: str
    answer: str