from PyPDF2 import PdfReader
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str, chunk_size: int = 5) -> list[str]:
    chunks = []
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            total_pages = len(reader.pages)
            
            for i in range(0, total_pages, chunk_size):
                chunk = ""
                for j in range(i, min(i + chunk_size, total_pages)):
                    chunk += reader.pages[j].extract_text()
                chunks.append(chunk)
        
        return chunks
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}", exc_info=True)
        return []