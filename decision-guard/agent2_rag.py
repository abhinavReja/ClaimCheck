import os

import chromadb

from config import CHROMA_COLLECTION, DOCS_FOLDER

# Initialize ChromaDB (persistent storage in ./chroma_db folder)
chroma_client = chromadb.PersistentClient(path="./chroma_db")


def load_documents():
    """
    Load all company docs from sample_data/ into ChromaDB.
    Run this ONCE at startup to set up the vector store.
    Skips transcript.txt — only loads company docs.
    """
    try:
        chroma_client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=CHROMA_COLLECTION, metadata={"hnsw:space": "cosine"}
    )

    docs = []
    ids = []
    metadatas = []

    for filename in os.listdir(DOCS_FOLDER):
        if filename == "transcript.txt":
            continue

        filepath = os.path.join(DOCS_FOLDER, filename)
        if not os.path.isfile(filepath):
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
        for i, chunk in enumerate(chunks):
            docs.append(chunk)
            ids.append(f"{filename}_{i}")
            metadatas.append({"source": filename, "chunk_index": i})

    if docs:
        collection.add(documents=docs, ids=ids, metadatas=metadatas)

    source_count = len(set(m["source"] for m in metadatas))
    print(f"✅ Loaded {len(docs)} chunks from {source_count} documents")
    return collection


def search_docs(query: str, n_results: int = 3) -> list:
    """
    Search company docs for information relevant to a claim or question.
    Returns the most relevant document chunks with source info.
    """
    collection = chroma_client.get_collection(CHROMA_COLLECTION)

    results = collection.query(query_texts=[query], n_results=n_results)

    formatted_results = []
    for i in range(len(results["documents"][0])):
        formatted_results.append(
            {
                "content": results["documents"][0][i],
                "source": results["metadatas"][0][i]["source"],
                "relevance_score": round(1 - results["distances"][0][i], 3),
            }
        )

    return formatted_results


if __name__ == "__main__":
    print("Loading documents into ChromaDB...\n")
    load_documents()

    print("\nTesting search: 'project budget 200k'")
    results = search_docs("project budget 200k")
    for r in results:
        print(f"\n📄 Source: {r['source']} (relevance: {r['relevance_score']})")
        print(f"   {r['content'][:150]}...")

    print("\n\nTesting search: 'security review complete'")
    results = search_docs("security review complete")
    for r in results:
        print(f"\n📄 Source: {r['source']} (relevance: {r['relevance_score']})")
        print(f"   {r['content'][:150]}...")
