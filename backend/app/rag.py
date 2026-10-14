import json
from pathlib import Path
import chromadb

#Path to the dataset file
DATASET_PATH = Path(__file__).parent.parent / "data" / "podiatry_dataset.json"
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
    return client.get_or_create_collection(name="podiatry")

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

