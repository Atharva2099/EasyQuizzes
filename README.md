# ByteBuilder Flashcard Generator - Cal Hacks 11.0

ByteBuilder presents a Flashcard Generator, developed for Cal Hacks 11.0. This web application allows users to upload PDF documents and generate AI-powered flashcards, creating an excellent tool for study and revision.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Working](#Working)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Troubleshooting](#troubleshooting)
- [Future Improvements](#future-improvements)

[Rest of your README content here]


# Flashcard Generator

Flashcard Generator is a web application that allows users to upload PDF documents and generate flashcards based on the content. It uses AI to create multiple-choice questions and answers, making it an excellent tool for study and revision.

## Features

- PDF upload and processing
- AI-powered flashcard generation
- Multiple-choice question format
- Topic-specific flashcard creation
- Interactive flashcard interface

## Prerequisites

- Python 3.8 or higher
- Groq API key (sign up at https://www.groq.com)

## Installation

1. Clone the repository:
   
2. Create a virtual environment:
   - python -m venv venv
   - source venv/bin/activate  # On Windows: venv\Scripts\activate
   
3. Install dependencies:

   - pip install -r requirements.txt

   or
   
2. Create and activate the Conda environment:
     
     - conda env create -f environment.yml
     - conda activate flashcard-env
   
4. Set up environment variables:

- Open `.env` and replace `your_api_key_here` with your actual Groq API key

## Running the Application

1. Start the FastAPI server:
   
   python -m uvicorn backend.app.main:app --reload


2. Open a web browser and navigate to `http://Localhost:8000` or whichever is provided by CLI

## Usage

1. Upload a PDF file using the "Upload PDF" button.
2. Enter a topic and the number of flashcards you want to generate.
3. Click "Generate Flashcards" to create your flashcards.
4. Navigate through the flashcards using the "Previous" and "Next" buttons.
5. Click on a flashcard to reveal the answer.

## Working


Crash course in Python Book Link:[ https://ehmatthes.github.io/pcc/](https://khwarizmi.org/wp-content/uploads/2021/04/Eric_Matthes_Python_Crash_Course_A_Hands.pdf) <br /><br />

[<img width="856" alt="image" src="https://github.com/user-attachments/assets/1dff4ab9-1c72-453a-a162-aeb68c7ddedc">]([https://www.youtube.com/watch?v=YOUTUBE_VIDEO_ID_HERE](https://www.youtube.com/watch?v=QGkC77hOxns))






## Project Structure

This structure represents the main directories and files in the project:
- `backend/`: Contains the backend logic.
  - `app/`: Contains Python scripts for backend functionality.
    - `__init__.py`: Initializes the Python package.
    - `main.py`: The entry point of the backend application.
    - `models.py`: Defines database or data models.
    - `ocr.py`: Script for Optical Character Recognition (OCR).
    - `VectorDB.py`: Vector database management.
    - `llm.py`: Logic for Large Language Model (LLM) interactions.
- `frontend/`: Contains frontend files.
  - `index.html`: The main HTML file.
  - `styles.css`: The CSS file for styling.
  - `script.js`: The JavaScript file for frontend functionality.
- `.env.example`: Example of environment variables.
- `.gitignore`: Files and directories to be ignored by Git.
- `requirements.txt`: List of dependencies for the backend.
- `README.md`: Project documentation.


## Technologies Used

- Backend: FastAPI, ChromaDB, Groq API
- Frontend: HTML, CSS, JavaScript
- PDF Processing: PyPDF2
- Environment Management: python-dotenv

## Troubleshooting

If you encounter any issues:
- Ensure you're using Python 3.8 or higher
- Verify that all dependencies are correctly installed
- Check that your `.env` file contains the correct Groq API key
- Make sure you have an active internet connection for API calls

## Future Improvements

- Implement user accounts for saving and managing flashcard sets
- Add support for more file formats beyond PDF
- Enhance the AI model for even more accurate and diverse question generation
- Develop a mobile app version for on-the-go studying

