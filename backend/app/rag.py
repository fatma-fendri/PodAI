import json
from pathlib import Path
import chromadb
import os

# Corpus version: "v1" (15 sheets, default) or "v2" (v1 + new sheets), chosen with PODAI_CORPUS
CORPUS = os.getenv("PODAI_CORPUS", "v1")
if CORPUS not in ("v1", "v2"):
    raise ValueError(f"PODAI_CORPUS must be 'v1' or 'v2', got {CORPUS!r}")
DATA_DIR = Path(__file__).parent.parent / "data"
DATASET_PATH = DATA_DIR / ("podiatry_dataset.json" if CORPUS == "v1" else "podiatry_dataset_v2.json")
COLLECTION_NAME = "podiatry" if CORPUS == "v1" else "podiatry_v2"
CHROMA_PATH = Path(__file__).parent.parent / "chroma_db"

def load_conditions():
    with open(DATASET_PATH, encoding="utf-8") as f:
        return json.load(f)

def build_document(condition):
    title = condition["title"]
    overview = condition["overview"]
    symptoms = ", ".join(condition["symptoms"])
    causes = ", ".join(condition["causes"])
    treatment = ", ".join(condition["treatment"])

    return (
        f"{title}. "
        f"Overview: {overview} "
        f"Symptoms: {symptoms}. "
        f"Causes: {causes}. "
        f"Treatment: {treatment}."
    )

def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_or_create_collection(name=COLLECTION_NAME)

def ingest():
    # 1. load the conditions and get the collection
    conditions = load_conditions()
    collection = get_collection()
    # 2. create three empty lists: ids, documents, metadatas
    ids = []
    documents = []
    metadatas = []
    # 3. loop over the conditions and append to the three lists
    for c in conditions:
        ids.append(c["id"])
        documents.append(build_document(c))
        metadatas.append({
            "title": c["title"],
            "category": c["category"],
            "source_name": c["source"]["name"],
            "source_url": c["source"]["url"],
        })
    # 4. upsert everything into the collection
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )
    # 5. print the number of documents stored
    print(collection.count())

def search(question, n_results=3):
    collection = get_collection()
    results = collection.query(
        query_texts=[question],
        n_results=n_results,
    )

    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "title": results["metadatas"][0][i]["title"],
            "source_url": results["metadatas"][0][i]["source_url"],
            "distance": results["distances"][0][i],
            "document": results["documents"][0][i],
        })
    return hits

_ranker = None


def get_ranker():
    global _ranker
    if _ranker is None:
        from flashrank import Ranker
        _ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")
    return _ranker


def rerank(question, hits, n_results):
    from flashrank import RerankRequest
    if not hits:
        return hits
    passages = [{"id": i, "text": h["document"]} for i, h in enumerate(hits)]
    out = get_ranker().rerank(RerankRequest(query=question, passages=passages))
    return [hits[p["id"]] for p in out][:n_results]


def search_reranked(question, n_results=5, n_candidates=10):
    hits = search(question, n_results=max(n_candidates, n_results))
    return rerank(question, hits, n_results)

if __name__ == "__main__":
    #conditions = load_conditions()
    #for c in conditions: build_document(c)
    ingest()
    #collection = get_collection()
    #print(collection.get(limit=2))
    for q in [
        "pain in the heel when I wake up",
        "my big toe is bending sideways",
        "numbness between my toes",
        "how to bake bread",
    ]:
        print(q)
        for hit in search(q):
            print("  ", hit["title"], round(hit["distance"], 3))

