import chromadb
from chromadb.utils import embedding_functions

_client = None
_collection = None


def get_collection():
    """
    Lazy-load Chroma client and embedding model
    ONLY when needed (critical for Render free tier)
    """
    global _client, _collection

    if _client is None:
        _client = chromadb.Client()

    if _collection is None:
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        _collection = _client.get_or_create_collection(
            name="documents",
            embedding_function=embedding_function
        )

    return _collection


def add_document(text: str, metadata: dict, doc_id: str):
    collection = get_collection()
    collection.add(
        documents=[text],
        metadatas=[metadata],
        ids=[doc_id]
    )


def query_documents(query: str, k: int = 3):
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    return results["documents"][0] if results["documents"] else []
