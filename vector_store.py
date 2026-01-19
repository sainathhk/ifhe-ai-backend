import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client()

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_function
)

def add_document(text: str, metadata: dict, doc_id: str):
    collection.add(
        documents=[text],
        metadatas=[metadata],
        ids=[doc_id]
    )

def query_documents(query: str, k: int = 3):
    results = collection.query(
        query_texts=[query],
        n_results=k
    )
    return results["documents"][0] if results["documents"] else []
