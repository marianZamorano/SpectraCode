import re
from collections import Counter

class StylometryDetector:
    def detect(self, code: str) -> float:
        lines = [l.strip() for l in code.splitlines() if l.strip()]
        if not lines:
            return 0.5

        comment_ratio = sum(1 for l in lines if l.startswith("#")) / len(lines)
        avg_line_len = sum(len(l) for l in lines) / len(lines)
        var_names = re.findall(r"def (\w+)\(|(\w+) =", code)
        avg_name_len = sum(len(n) for n in var_names) / max(1, len(var_names))

        score = 0.0
        score += comment_ratio * 0.4
        score += min(avg_line_len / 80.0, 1.0) * 0.3
        score += min(avg_name_len / 8.0, 1.0) * 0.3
        return 1.0 - score