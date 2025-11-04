from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from utils.zip_parser import extract_python_files
from detectors.ensemble import EnsembleDetector
from agent import explain_file
import os
import tempfile
from datetime import datetime
from dotenv import load_dotenv

try:
    import pandas as pd
except ImportError:
    pd = None

load_dotenv()
app = FastAPI(title="CodeGuard AI", version="1.0.0")

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
        res = detector.predict(code)
        prob_ai = res.get("ai_probability", 0.0)
        attribution = detector.attribute_llm(res)
        explanation = explain_file(code, prob_ai, attribution)
        comps = res.get("components", {})

        results.append({
            "file": py_file["path"],
            "ai_probability": round(prob_ai * 100, 2),
            "perplexity_score": comps.get("perplexity", {}).get("score", 0.0),
            "ast_score": comps.get("ast", {}).get("score", 0.0),
            "codebert_score": comps.get("codebert", {}).get("score", 0.0),
            "attribution": attribution,
            "explanation": explanation,
        })

    if not results:
        results = [{
            "file": "(ningún .py encontrado)",
            "ai_probability": 0.0,
            "attribution": "",
            "explanation": "No se encontraron archivos .py en el ZIP o el ZIP está corrupto."
        }]

    tmpdir = tempfile.gettempdir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if pd:
        output_path = os.path.join(tmpdir, f"results_{timestamp}.xlsx")
        df = pd.DataFrame(results)
        df.to_excel(output_path, index=False)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = "resultados.xlsx"
    else:
        output_path = os.path.join(tmpdir, f"results_{timestamp}.csv")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("file,ai_probability,attribution,explanation\n")
            for r in results:
                f.write(f"{r['file']},{r['ai_probability']},{r['attribution']},{r['explanation']}\n")
        media_type = "text/csv"
        filename = "resultados.csv"

    os.unlink(zip_path)
    return FileResponse(output_path, media_type=media_type, filename=filename)