from groq import Groq
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_qa_pair(context: str):
    prompt = f"""Given the following context, generate a unique and specific multiple-choice question-answer pair suitable for a flashcard. The question should test understanding of key concepts.

Context: {context}

Generate a question-answer pair in the following format:
Question: [Your specific, unique multiple-choice question with 4 options labeled A, B, C, and D]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Answer: [The correct option letter followed by a brief explanation]

Ensure the question is not generic and is specifically related to the given context."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.2-3b-preview",
            max_tokens=1000,  # Increased to accommodate longer response
            temperature=0.7,
        )

        response = chat_completion.choices[0].message.content
        logger.info(f"Generated response: {response}")

        # Split the response into question and answer
        parts = response.split("Answer:")
        if len(parts) != 2:
            logger.error("Response format is incorrect")
            return None

        question_part = parts[0].strip()
        answer_part = parts[1].strip()

        # Further process the question to include options
        question_lines = question_part.split("\n")
        question = question_lines[0].replace("Question:", "").strip()
        options = "\n".join(question_lines[1:])

        return f"{question}\n{options}", answer_part

    except Exception as e:
        logger.error(f"Error generating QA pair: {e}")
        return None