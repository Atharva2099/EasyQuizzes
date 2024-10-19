async function generateFlashcards() {
    console.log('Generating flashcards...');
    try {
        const response = await fetch('/generate_flashcards', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ num_cards: 5 })
        });
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);
        if (data.error) {
            alert(data.error);
        } else if (data.flashcards && data.flashcards.length > 0) {
            displayFlashcards(data.flashcards);
        } else {
            alert('No flashcards were generated. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while generating flashcards.');
    }
}

function displayFlashcards(flashcards) {
    console.log('Displaying flashcards:', flashcards);
    const flashcardsContainer = document.getElementById('flashcards-container');
    flashcardsContainer.innerHTML = '';
    if (flashcards.length === 0) {
        flashcardsContainer.innerHTML = '<p>No flashcards generated. Please try again.</p>';
        return;
    }
    flashcards.forEach((card, index) => {
        const cardElement = document.createElement('div');
        cardElement.className = 'flashcard';
        
        // Split the question and options
        const [question, ...options] = card.question.split('\n');
        
        cardElement.innerHTML = `
            <div class="question">
                <h3>Question ${index + 1}:</h3>
                <p>${question}</p>
                ${options.map(option => `<p>${option}</p>`).join('')}
            </div>
            <div class="answer" style="display: none;">
                <h3>Answer:</h3>
                <p>${card.answer}</p>
            </div>
        `;
        cardElement.addEventListener('click', () => {
            const answer = cardElement.querySelector('.answer');
            answer.style.display = answer.style.display === 'none' ? 'block' : 'none';
        });
        flashcardsContainer.appendChild(cardElement);
    });
}

// Make sure these event listeners are set up
document.addEventListener('DOMContentLoaded', () => {
    const uploadBtn = document.getElementById('upload-btn');
    const generateBtn = document.getElementById('generate-btn');
    
    if (uploadBtn) {
        uploadBtn.addEventListener('click', uploadFile);
    } else {
        console.error('Upload button not found');
    }
    
    if (generateBtn) {
        generateBtn.addEventListener('click', generateFlashcards);
    } else {
        console.error('Generate button not found');
    }
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
        if (data.message === 'File processed successfully') {
            alert('File uploaded and processed successfully!');
            document.getElementById('generate-section').style.display = 'block';
        } else {
            alert('Error: ' + (data.error || 'Unknown error occurred'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while uploading the file.');
    }
}