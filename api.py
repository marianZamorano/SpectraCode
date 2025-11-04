from fastapi import FastAPI, File, UploadFile, WebSocket
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.zip_parser import extract_python_files
from detectors.ensemble import EnsembleDetector
from agent import explain_file
import json
import os
import tempfile
from datetime import datetime
import python_dotenv

# Cargar .env
python_dotenv.load_dotenv()

app = FastAPI(
    title="CodeGuard AI",
    description="Detecta código IA en repositorios ZIP → %IA + LLM + Explicación",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = EnsembleDetector()

@app.post("/analyze-repo")
async def analyze_repo(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp.write(await file.read())
        zip_path = tmp.name

    python_files = extract_python_files(zip_path)
    results = []
    
    for py_file in python_files:
        code = py_file["content"]
        prob_ai = detector.detect_probability(code)
        attribution = detector.attribute_llm(code)
        explanation = explain_file(code, prob_ai, attribution)
        
        results.append({
            "file": py_file["path"],
            "ai_probability": round(prob_ai * 100, 2),
            "attribution": attribution,
            "explanation": explanation
        })
    
    output_json = f"/tmp/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({"files": results, "total": len(results)}, f, indent=2, ensure_ascii=False)
    
    os.unlink(zip_path)
    return FileResponse(output_json, media_type="application/json", filename="resultados.json")