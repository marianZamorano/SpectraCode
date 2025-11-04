import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="data/rag_db/chroma")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="microsoft/codebert-base")
collection = client.get_collection(name="python_ai_code_knowledge", embedding_function=embedding_fn)

def query_rag(code: str, n_results: int = 3) -> str:
    results = collection.query(
        query_texts=[code[:1000]],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    context = ""
    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        context += f"""
=== EJEMPLO {i+1} (Distancia: {dist:.4f}) ===
Fuente: {meta['source']}
Etiqueta: {meta['label']}
Dataset: {meta['dataset']} ({meta['paper']})
Código:
{doc}
"""
    return context.strip()