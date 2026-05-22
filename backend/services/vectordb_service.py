from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import json

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

def get_vectorstore():
    return Chroma(
        collection_name="worksheets",
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )

def store_worksheet(topic: str, content: dict) -> bool:
    try:
        text = json.dumps(content)

        chunks = text_splitter.split_text(text)

        docs = [
            Document(
                page_content=chunk,
                metadata={"topic": topic}
            )
            for chunk in chunks
        ]

        vectorstore = get_vectorstore()
        vectorstore.add_documents(docs)
        print(f"Stored {len(docs)} chunks for topic: {topic}")
        return True

    except Exception as e:
        print(f"Store error: {str(e)}")
        return False

def retrieve_worksheet(topic: str) -> dict:
    try:
        vectorstore = get_vectorstore()

        results = vectorstore.similarity_search_with_score(
            query=topic,
            k=3
        )

        if not results:
            return None

        best_score = results[0][1]
        best_topic = results[0][0].metadata.get("topic", "")

        print(f"Best match: {best_topic}, Score: {best_score}")

        if best_topic.lower() == topic.lower():
            all_chunks = []
            for doc, score in results:
                if doc.metadata.get("topic", "").lower() == topic.lower():
                    all_chunks.append(doc.page_content)

            combined = " ".join(all_chunks)
            try:
                start = combined.find("{")
                end = combined.rfind("}") + 1
                if start != -1 and end > start:
                    return json.loads(combined[start:end])
            except:
                pass

        return None

    except Exception as e:
        print(f"Retrieve error: {str(e)}")
        return None