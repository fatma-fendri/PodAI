import json

import chromadb

from app.rag import CHROMA_PATH, DATASET_PATH, load_conditions, build_document

HINTS_PATH = DATASET_PATH.parent / "search_hints.json"
COLLECTION = "podiatry_enriched"


def load_hints():
    return json.loads(HINTS_PATH.read_text(encoding="utf-8"))


def build_enriched_document(condition, hints):
    base = build_document(condition)
    extra = hints.get(condition["id"], [])
    if not extra:
        return base
    return f"{base} Patient wording: {'; '.join(extra)}."


def get_enriched_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(name=COLLECTION)


def build():
    conditions = load_conditions()
    hints = load_hints()
    collection = get_enriched_collection()
    collection.upsert(
        ids=[c["id"] for c in conditions],
        documents=[build_enriched_document(c, hints) for c in conditions],
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


def search_enriched(question, n_results=3):
    collection = get_enriched_collection()
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