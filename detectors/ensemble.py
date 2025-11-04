from .perplexityScore import PerplexityDetector
from .stylometryModel import StylometryDetector
from .classifier import CodeBERTClassifier
from utils.astUtils import get_ast_score
import numpy as np
from typing import Dict, Any

class EnsembleDetector:
    def __init__(self):
        self.perplexity = PerplexityDetector()
        self.stylometry = StylometryDetector()
        self.classifier = CodeBERTClassifier()
    
    def predict(self, code: str) -> Dict[str, Any]:
        try:
            # 1. Perplexity (GPT-2)
            perp_score = self.perplexity.get_score(code)
            
            # 2. AST Stylometry
            ast_result = get_ast_score(code)
            ast_score = ast_result.get("score", 0.0)
            
            # 3. CodeBERT
            bert_prob = self.classifier.predict_proba(code)
            
            # 4. Ensemble: weighted average
            weights = [0.4, 0.3, 0.3]  # Perplexity, AST, BERT
            ai_probs = [
                perp_score,           # 1.0 = AI, 0.0 = Human
                1.0 - ast_score,      # 1.0 = AI, 0.0 = Human
                bert_prob             # 1.0 = AI, 0.0 = Human
            ]
            final_prob = np.average(ai_probs, weights=weights)
            
            return {
                "ai_probability": round(final_prob, 3),
                "components": {
                    "perplexity": round(perp_score, 3),
                    "ast": round(1.0 - ast_score, 3),
                    "codebert": round(bert_prob, 3)
                },
                "explanation": self._explain(ai_probs, ast_result.get("features", {}))
            }
        except Exception as e:
            return {
                "ai_probability": 0.0,
                "error": str(e),
                "explanation": "Error en análisis de código."
            }
    
    def _explain(self, probs: list, features: dict) -> str:
        perp, ast_ai, bert = probs
        if max(probs) < 0.3:
            return "Código con alta entropía, profundidad variable y estilo humano. Probablemente escrito por persona."
        elif perp > 0.7:
            return f"Perplejidad baja (GPT-like). Patrón típico de IA ({perp:.2f})."
        elif ast_ai > 0.7:
            return f"AST rígido: profundidad baja ({features.get('depth',0)}), complejidad alta. IA probable."
        elif bert > 0.7:
            return "CodeBERT detecta patrones de entrenamiento en IA."
        else:
            return f"Ensemble: Perp={perp:.2f}, AST={ast_ai:.2f}, BERT={bert:.2f}. IA probable."