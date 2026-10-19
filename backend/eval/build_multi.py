import chromadb
from chromadb.utils import embedding_functions

from app.rag import CHROMA_PATH, load_conditions, build_document

MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION = "podiatry_multi"


def get_multi_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL)
    return client.get_or_create_collection(name=COLLECTION, embedding_function=ef)


def build():
    conditions = load_conditions()
    collection = get_multi_collection()
    collection.upsert(
        ids=[c["id"] for c in conditions],
        documents=[build_document(c) for c in conditions],
        metadatas=[
            {
                "title": c["title"],
                "category": c["category"],
                "source_name": c["source"]["name"],
                "source_url": c["source"]["url"],
            }
            for c in conditions
        ],
    )
    print(collection.count())


def search_multi(question, n_results=3):
    collection = get_multi_collection()
    results = collection.query(query_texts=[question], n_results=n_results)
    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "title": results["metadatas"][0][i]["title"],
            "source_url": results["metadatas"][0][i]["source_url"],
            "distance": results["distances"][0][i],
            "document": results["documents"][0][i],
        })
    return hits


if __name__ == "__main__":
    build()