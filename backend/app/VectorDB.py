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
def retrieve_diverse_contexts(n_contexts: int = 5):
    all_docs = collection.get()['documents']
    if not all_docs:
        return []
    step = max(1, len(all_docs) // n_contexts)
    return [all_docs[i] for i in range(0, len(all_docs), step)][:n_contexts]