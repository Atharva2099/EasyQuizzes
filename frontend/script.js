let allFlashcards = [];
let currentCardIndex = 0;

document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('upload-btn');
    const flashcardForm = document.getElementById('flashcard-form');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    uploadBtn.addEventListener('click', uploadFile);
    flashcardForm.addEventListener('submit', handleGenerateFlashcards);
    prevBtn.addEventListener('click', showPreviousCard);
    nextBtn.addEventListener('click', showNextCard);
});

async function uploadFile() {
    console.log('Upload function called');
    const fileUpload = document.getElementById('file-upload');
    const file = fileUpload.files[0];
    if (!file) {
        console.log('No file selected');
        alert('Please select a file first.');
        return;
    }

    console.log('File selected:', file.name);

    const formData = new FormData();
    formData.append('file', file);

    try {
        console.log('Sending request to /upload');
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.message && data.message.includes("File upload started")) {
            console.log('File upload successful');
            alert('File uploaded successfully and processing started!');
            document.getElementById('generate-section').style.display = 'block';
            checkProgress(data.file_id);
        } else {
            console.error('Unexpected server response:', data);
            throw new Error(data.error || 'Unknown server error');
        }
    } catch (error) {
        console.error('Error during file upload:', error);
        alert('An error occurred while uploading the file: ' + error.message);
    }
}

async function checkProgress(fileId) {
    const progressBar = document.getElementById('progress-bar');
    const uploadProgress = document.getElementById('upload-progress');
    progressBar.style.display = 'block';

    try {
        while (true) {
            const response = await fetch(`/progress/${fileId}`);
            const data = await response.json();
            console.log('Progress:', data.progress);
            
            uploadProgress.value = data.progress;
            
            if (data.progress >= 100) {
                progressBar.style.display = 'none';
                alert('File processing complete!');
                break;
            }
            
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for 1 second before checking again
        }
    } catch (error) {
        console.error('Error checking progress:', error);
        progressBar.style.display = 'none';
    }
}

async function handleGenerateFlashcards(event) {
    event.preventDefault();
    
    const topic = document.getElementById('topics').value.trim();
    const numCards = parseInt(document.getElementById('num-cards').value);
    
    if (!topic || isNaN(numCards) || numCards <= 0) {
        alert('Please enter a valid topic and number of cards.');
        return;
    }
    
    try {
        allFlashcards = await generateFlashcards(topic, numCards);
        
        if (allFlashcards.length > 0) {
            currentCardIndex = 0;
            displayFlashcard();
            document.getElementById('flashcards-container').style.display = 'block';
        } else {
            alert('No flashcards were generated. Please try again.');
        }
    } catch (error) {
        console.error('Error generating flashcards:', error);
        alert('An error occurred while generating flashcards. Please try again.');
    }
}

async function generateFlashcards(topic, numCards) {
    console.log(`Generating ${numCards} flashcards for topic: ${topic}`);
    const response = await fetch('/generate_flashcards', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, num_cards: numCards })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Response data:', data);
    
    if (data.error) {
        throw new Error(data.error);
    }
    
    return data.flashcards;
}

function displayFlashcard() {
    const flashcardDisplay = document.getElementById('flashcard-display');
    const cardIndexSpan = document.getElementById('card-index');
    
    if (allFlashcards.length === 0) {
        flashcardDisplay.innerHTML = '<p>No flashcards available.</p>';
        cardIndexSpan.textContent = '';
        return;
    }
    
    const card = allFlashcards[currentCardIndex];
    const [question, ...options] = card.question.split('\n');
    
    flashcardDisplay.innerHTML = `
        <div class="flashcard">
            <div class="question">
                <h3>Question:</h3>
                <p>${question}</p>
                ${options.map(option => `<p>${option}</p>`).join('')}
            </div>
            <div class="answer" style="display: none;">
                <h3>Answer:</h3>
                <p>${card.answer}</p>
            </div>
        </div>
    `;
    
    flashcardDisplay.querySelector('.flashcard').addEventListener('click', toggleAnswer);
    cardIndexSpan.textContent = `Card ${currentCardIndex + 1} of ${allFlashcards.length}`;
}

function toggleAnswer() {
    const answerElement = this.querySelector('.answer');
    answerElement.style.display = answerElement.style.display === 'none' ? 'block' : 'none';
}

function showPreviousCard() {
    if (currentCardIndex > 0) {
        currentCardIndex--;
        displayFlashcard();
    }
}

function showNextCard() {
    if (currentCardIndex < allFlashcards.length - 1) {
        currentCardIndex++;
        displayFlashcard();
    }
}