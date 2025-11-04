from detectors.ensemble import EnsembleDetector
from utils.zip_parser import extract_python_files
from sklearn.metrics import classification_report, f1_score
import sys

detector = EnsembleDetector()

def evaluate(zip_path: str):
    files = extract_python_files(zip_path)
    y_true = []
    y_pred = []

    for f in files:
        label = 1 if any(x in f["path"].lower() for x in ["gpt", "ai", "generated"]) else 0
        prob = detector.detect_probability(f["content"])
        pred = 1 if prob > 0.5 else 0
        y_true.append(label)
        y_pred.append(pred)

    f1 = f1_score(y_true, y_pred)
    print(f"F1 Score: {f1:.4f}")
    print(classification_report(y_true, y_pred, target_names=["Humano", "IA"]))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python evaluate.py <archivo_zip>")
    else:
        evaluate(sys.argv[1])