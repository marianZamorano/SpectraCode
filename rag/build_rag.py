import os
import json
import zipfile
import tempfile
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions
import requests
from tqdm import tqdm
import pandas as pd  # Para parquet si necesario

# -------------------------------
# CONFIGURACIÓN
# -------------------------------
DATA_DIR = Path("data/rag_db")
DATA_DIR.mkdir(exist_ok=True)
CHROMA_PATH = DATA_DIR / "chroma"
CHROMA_PATH.mkdir(exist_ok=True)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="microsoft/codebert-base")
client = chromadb.PersistentClient(path=str(CHROMA_PATH))
collection = client.get_or_create_collection(name="python_ai_code_knowledge", embedding_function=embedding_fn)

# -------------------------------
# DATASETS PÚBLICOS (Python-only, de links proporcionados)
# -------------------------------
DATASETS = {
    "MBPP": {
        "url": "https://raw.githubusercontent.com/google-research/google-research/master/mbpp/mbpp.jsonl",
        "label": "Human",
        "paper": "MBPP: A Dataset for Evaluating Machine Learning Programs (Google Research, 2020)",
        "format": "jsonl"
    },
    "HumanEval_Pro": {
        "url": "https://huggingface.co/datasets/CodeEval-Pro/humaneval_pro/resolve/main/refined_humaneval_pro.json",
        "label": "Human",  # Base problems human-written
        "paper": "HumanEval Pro and MBPP Pro (CodeEval-Pro, 2024)",
        "format": "json"
    },
    "MBPP_Pro": {
        "url": "https://huggingface.co/datasets/CodeEval-Pro/mbpp_pro/resolve/main/refined_mbpp_pro.json",
        "label": "Human",  # Self-invoking but base human
        "paper": "HumanEval Pro and MBPP Pro (CodeEval-Pro, 2024)",
        "format": "json"
    },
    "CodeSearchNet_Python": {
        "url": "https://s3.amazonaws.com/code-search-net/CodeSearchNet/v2/python.zip",
        "label": "Human",
        "paper": "CodeSearchNet: Datasets for Code Search (GitHub, 2019)",
        "format": "zip"
    }
    # Skip plag_detection_on_SO and scored23: No Python or insufficient
}

# -------------------------------
# DESCARGA Y PROCESAMIENTO
# -------------------------------
def download_file(url: str, dest: Path):
    if dest.exists():
        print(f"[SKIP] {dest.name}")
        return
    print(f"[DOWNLOAD] {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in tqdm(response.iter_content(8192), desc="Downloading"):
            f.write(chunk)
    print(f"[OK] Saved {dest}")

def process_jsonl(url: str, label: str) -> List[Dict]:
    dest = DATA_DIR / "temp.jsonl"
    download_file(url, dest)
    docs = []
    with open(dest, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            try:
                data = json.loads(line)
                # MBPP: 'text' is prompt + solution code
                code = data.get("code", "") or data.get("text", "")
                if code and "def " in code and len(code) > 50:
                    docs.append({
                        "content": code[:3000],
                        "label": label,
                        "source": f"mbpp_{line_num}"
                    })
            except:
                continue
    os.unlink(dest)
    return docs

def process_json(url: str, label: str) -> List[Dict]:
    dest = DATA_DIR / "temp.json"
    download_file(url, dest)
    docs = []
    with open(dest, "r", encoding="utf-8") as f:
        data = json.load(f)
        for i, item in enumerate(data):
            code = item.get("code", "") or item.get("solution", "")
            if code and len(code) > 50:
                docs.append({
                    "content": code[:3000],
                    "label": label,
                    "source": f"{Path(url).stem}_{i}"
                })
    os.unlink(dest)
    return docs

def process_zip(url: str, label: str) -> List[Dict]:
    dest_zip = DATA_DIR / "temp.zip"
    download_file(url, dest_zip)
    docs = []
    with zipfile.ZipFile(dest_zip, 'r') as z:
        with tempfile.TemporaryDirectory() as tmpdir:
            z.extractall(tmpdir)
            tmp_path = Path(tmpdir)
            # CodeSearchNet: JSONL in /python/final/jsonl/train.0.jsonl etc.
            for jsonl_file in tmp_path.rglob("*.jsonl"):
                with open(jsonl_file, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f):
                        try:
                            data = json.loads(line)
                            code = data.get("code", "")
                            if code and len(code) > 100:  # Filter meaningful code
                                docs.append({
                                    "content": code[:3000],
                                    "label": label,
                                    "source": str(jsonl_file.relative_to(tmp_path)) + f"_{line_num}"
                                })
                        except:
                            continue
    os.unlink(dest_zip)
    return docs

# -------------------------------
# CONSTRUCCIÓN
# -------------------------------
def build_rag():
    print("Construyendo RAG con datasets Python de GitHub/HF...\n")
    total_docs = 0
    for name, info in DATASETS.items():
        print(f"Procesando: {name} ({info['paper']})")
        try:
            if info["format"] == "jsonl":
                docs = process_jsonl(info["url"], info["label"])
            elif info["format"] == "json":
                docs = process_json(info["url"], info["label"])
            elif info["format"] == "zip":
                docs = process_zip(info["url"], info["label"])
            else:
                docs = []
            
            if docs:
                print(f"   {len(docs)} docs extraídos")
                for i, doc in enumerate(tqdm(docs, desc="Indexando")):
                    collection.add(
                        ids=[f"{name}_{i}"],
                        documents=[doc["content"]],
                        metadatas=[{
                            "label": doc["label"],
                            "source": doc["source"],
                            "paper": info["paper"]
                        }]
                    )
                total_docs += len(docs)
                print(f"   Indexados en ChromaDB\n")
            else:
                print(f"   No docs encontrados\n")
        except Exception as e:
            print(f"   [ERROR] {e}\n")
    
    print(f"RAG CONSTRUIDO: {collection.count()} docs Python en {CHROMA_PATH}")

if __name__ == "__main__":
    build_rag()