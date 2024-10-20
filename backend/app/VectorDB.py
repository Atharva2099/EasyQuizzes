# backend/app/vector_db.py
import chromadb
from chromadb.config import Settings
import uuid
import logging
from chromadb.errors import NotEnoughElementsException

logger = logging.getLogger(__name__)

# Use a persistent storage for ChromaDB
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_db"
))

# Create the collection if it doesn't exist
collection = client.get_or_create_collection("flashcards")

def store_text(text: str, metadata: dict = None):
    try:
        collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else None,
            ids=[str(uuid.uuid4())]
        )
        client.persist()
    except Exception as e:
        logger.error(f"Error storing text in VectorDB: {str(e)}", exc_info=True)

def retrieve_context(query: str, n_results: int = 1):
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []
    except NotEnoughElementsException:
        logger.warning(f"Not enough elements for query: {query}. Returning all available.")
        return collection.get()['documents']

def retrieve_diverse_contexts(topic: str, n_contexts: int = 5):
    logger.debug(f"Retrieving contexts for topic: {topic}, n_contexts: {n_contexts}")
    try:
        results = collection.query(
            query_texts=[topic],
            n_results=n_contexts
        )
        contexts = results['documents'][0] if results['documents'] else []
    except NotEnoughElementsException:
        logger.warning(f"Not enough contexts available. Retrieving all available contexts.")
        contexts = collection.get()['documents']
    
    logger.debug(f"Retrieved {len(contexts)} contexts")
    return contexts

def get_total_documents():
    return collection.count()