from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

def get_vectorstore():
    return Chroma(
        collection_name="web_content",
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

def store_web_content(topic: str, content: str) -> bool:
    try:
        chunks = text_splitter.split_text(content)
        docs = [
            Document(
                page_content=chunk,
                metadata={"topic": topic}
            )
            for chunk in chunks
        ]
        vectorstore = get_vectorstore()
        vectorstore.add_documents(docs)
        print(f"Stored {len(docs)} web content chunks for: {topic}")
        return True
    except Exception as e:
        print(f"Store error: {str(e)}")
        return False

def retrieve_web_content(topic: str) -> str:
    try:
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search_with_score(
            query=topic,
            k=3
        )
        if not results:
            return None
        best_topic = results[0][0].metadata.get("topic", "")
        best_score = results[0][1]
        print(f"Web content match: {best_topic}, Score: {best_score}")
        if best_topic.lower() == topic.lower() and best_score < 0.4:
            combined = " ".join([doc.page_content for doc, score in results])
            return combined
        return None
    except Exception as e:
        print(f"Retrieve error: {str(e)}")
        return None