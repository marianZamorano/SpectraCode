import ast
import math
from typing import Dict, Any

def get_ast_score(code: str) -> Dict[str, Any]:
    """
    Analiza el AST del código y devuelve métricas estilométricas.
    Basado en patrones humanos vs IA (profundidad, complejidad, repetición).
    """
    try:
        tree = ast.parse(code)
    except:
        return {"error": "syntax_error", "score": 0.0}

    class ASTVisitor(ast.NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.max_depth = 0
            self.node_count = 0
            self.function_count = 0
            self.loop_count = 0
            self.branch_count = 0
            self.node_types = {}

        def visit(self, node):
            self.node_count += 1
            self.depth += 1
            self.max_depth = max(self.max_depth, self.depth)
            
            node_type = type(node).__name__
            self.node_types[node_type] = self.node_types.get(node_type, 0) + 1

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.function_count += 1
            elif isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
                self.loop_count += 1
            elif isinstance(node, ast.If):
                self.branch_count += 1

            self.generic_visit(node)
            self.depth -= 1

    visitor = ASTVisitor()
    visitor.visit(tree)

    if visitor.node_count == 0:
        return {"score": 0.0, "features": {}}

    # Métricas estilométricas (human-like vs AI-like)
    avg_depth = visitor.max_depth
    complexity = (visitor.loop_count + visitor.branch_count) / max(1, visitor.function_count)
    entropy = 0.0
    if visitor.node_types:
        total = sum(visitor.node_types.values())
        entropy = -sum((count/total) * math.log(count/total + 1e-10) for count in visitor.node_types.values())

    # Score: IA tiende a profundidad baja, complejidad alta, entropía baja
    score = 0.0
    score += min(avg_depth / 10.0, 1.0) * 0.3
    score += min(complexity, 3.0) / 3.0 * 0.4
    score += (1.0 - min(entropy / 5.0, 1.0)) * 0.3

    return {
        "score": round(1.0 - score, 3),  # 1.0 = humano, 0.0 = IA
        "features": {
            "depth": avg_depth,
            "complexity": round(complexity, 2),
            "entropy": round(entropy, 3),
            "nodes": visitor.node_count,
            "functions": visitor.function_count
        }
    }