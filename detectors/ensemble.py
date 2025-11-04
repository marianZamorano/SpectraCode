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
            perp_score = self.perplexity.get_score(code)
            ast_result = get_ast_score(code)
            ast_score = ast_result.get("score", 0.0)
            bert_prob = self.classifier.predict_proba(code)

            weights = [0.4, 0.3, 0.3]
            ai_probs = [
                perp_score,
                1.0 - ast_score,
                bert_prob,
            ]
            final_prob = np.average(ai_probs, weights=weights)

            def comp_meta(score: float):
                confidence = min(max(abs(score - 0.5) * 2.0, 0.0), 1.0)
                bias = score - 0.5
                return {"score": round(float(score), 3), "confidence": round(float(confidence), 3), "bias": round(float(bias), 3)}

            components = {
                "perplexity": comp_meta(perp_score),
                "ast": comp_meta(1.0 - ast_score),
                "codebert": comp_meta(bert_prob),
            }

            return {
                "ai_probability": round(float(final_prob), 3),
                "components": components,
                "explanation": self._explain(ai_probs, ast_result.get("features", {})),
            }
        except Exception as e:
            return {"ai_probability": 0.0, "error": str(e), "explanation": "Error en análisis de código."}

    def _explain(self, probs: list, features: dict) -> str:
        perp, ast_ai, bert = probs
        if max(probs) < 0.3:
            return "Código con alta entropía, profundidad variable y estilo humano. Probablemente escrito por persona."
        if perp > 0.7:
            return f"Perplejidad baja (GPT-like). Patrón típico de IA ({perp:.2f})."
        if ast_ai > 0.7:
            return f"AST rígido: profundidad baja ({features.get('depth',0)}), complejidad alta. IA probable."
        if bert > 0.7:
            return "CodeBERT detecta patrones de entrenamiento en IA."
        return f"Ensemble: Perp={perp:.2f}, AST={ast_ai:.2f}, BERT={bert:.2f}. IA probable."

    def detect_probability(self, code: str) -> float:
        res = self.predict(code)
        return float(res.get("ai_probability", 0.0))

    def attribute_llm(self, code_or_res) -> str:
        if isinstance(code_or_res, dict):
            res = code_or_res
        else:
            res = self.predict(code_or_res)
        comps = res.get("components", {})
        perp = comps.get("perplexity", {})
        ast = comps.get("ast", {})
        codebert = comps.get("codebert", {})
        return (
            f"Perplexity(score={perp.get('score',0):.3f},conf={perp.get('confidence',0):.3f},bias={perp.get('bias',0):.3f}); "
            f"AST(score={ast.get('score',0):.3f},conf={ast.get('confidence',0):.3f},bias={ast.get('bias',0):.3f}); "
            f"CodeBERT(score={codebert.get('score',0):.3f},conf={codebert.get('confidence',0):.3f},bias={codebert.get('bias',0):.3f})"
        )