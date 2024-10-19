# backend/app/vector_db.py
import chromadb

client = chromadb.Client()
collection = client.create_collection("flashcards")

def store_text(text: str, metadata: dict = None):
    collection.add(
        documents=[text],
        metadatas=[metadata] if metadata else None,
        ids=[str(collection.count() + 1)]
    )

def retrieve_context(query: str, n_results: int = 1):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results['documents'][0] if results['documents'] else []

# Add this new function
import logging
from chromadb.errors import NotEnoughElementsException

logger = logging.getLogger(__name__)

def retrieve_diverse_contexts(topic: str, n_contexts: int = 5):
    logger.debug(f"Retrieving contexts for topic: {topic}, n_contexts: {n_contexts}")
    try:
        results = collection.query(
            query_texts=[topic],
            n_results=n_contexts
        )
        contexts = results['documents'][0] if results['documents'] else []
    except NotEnoughElementsException:
        # If not enough elements, retrieve all available contexts
        logger.warning(f"Not enough contexts available. Retrieving all available contexts.")
        results = collection.query(
            query_texts=[topic],
            n_results=1  # Retrieve at least one context
        )
        contexts = results['documents'][0] if results['documents'] else []
    
    logger.debug(f"Retrieved {len(contexts)} contexts")
    return contexts