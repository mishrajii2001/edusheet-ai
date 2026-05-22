import chromadb
from chromadb.utils import embedding_functions
import os

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

client = chromadb.PersistentClient(path=CHROMA_PATH)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="worksheets",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}
)

def store_worksheet(topic: str, content: dict) -> bool:
    try:
        import json
        collection.upsert(
            documents=[json.dumps(content)],
            metadatas=[{"topic": topic}],
            ids=[topic.lower().replace(" ", "_")]
        )
        return True
    except Exception as e:
        print(f"Store error: {str(e)}")
        return False

def retrieve_worksheet(topic: str) -> dict:
    try:
        results = collection.query(
            query_texts=[topic],
            n_results=1
        )
        if results and results["documents"][0]:
            import json
            distance = results["distances"][0][0]
            matched_topic = results["metadatas"][0][0]["topic"]
            print(f"Distance found: {distance}, Matched topic: {matched_topic}")
            
            if matched_topic.lower() == topic.lower():
                return json.loads(results["documents"][0][0])
            
            if distance < 0.8:
                return json.loads(results["documents"][0][0])
                
        return None
    except Exception as e:
        print(f"Retrieve error: {str(e)}")
        return None