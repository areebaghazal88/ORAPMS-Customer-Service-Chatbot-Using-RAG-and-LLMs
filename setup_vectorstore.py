# setup_vectorstore_once.py
import os
import re
import uuid
from langchain.schema import Document
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client import QdrantClient

def preprocess(text):
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=500, overlap=50):
    return [Document(page_content=text[i:i+chunk_size]) for i in range(0, len(text), chunk_size - overlap)]

def create_collection():
    try:
        file_path = "data/mini dataset.txt"
        collection_name = "customer_service_static"
        model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        client = QdrantClient(path="qdrant_data")

        with open(file_path, "r", encoding="utf-8") as f:
            text = preprocess(f.read())

        docs = chunk_text(text)
        vectors = [model.encode(f"passage: {doc.page_content}") for doc in docs]

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=model.get_sentence_embedding_dimension(),
                distance=Distance.COSINE
            )
        )

        points = [
            PointStruct(id=i, vector=v.tolist(), payload={"text": f"passage: {docs[i].page_content}"})
            for i, v in enumerate(vectors)
        ]

        client.upsert(collection_name=collection_name, points=points)
        print(f"✅ Created collection '{collection_name}' with {len(points)} vectors.")

    except Exception as e:
        print(f"[Vectorstore Setup ERROR] {e}")


if __name__ == "__main__":
    create_collection()
