import re
from typing import List, Tuple

VULNERABILITIES = [
    (r'eval\s*\(', "eval() detected - INSECURE"),
    (r'os\.system\s*\(', "os.system() - command injection risk"),
    (r'subprocess\.call\s*\(', "subprocess.call() - use subprocess.run"),
    (r'pickle\.loads\s*\(', "pickle.loads() - deserialization risk"),
    (r'input\s*\(', "input() - potential code injection")
]

def apply_patch(code: str) -> Tuple[str, List[str]]:
    patched_code = code
    issues = []
    
    for pattern, warning in VULNERABILITIES:
        matches = re.finditer(pattern, code)
        for match in matches:
            start, end = match.span()
            issues.append(f"{warning} at line ~{code[:start].count(chr(10))+1}")
            patched_code = (
                patched_code[:start] +
                f"# SECURE PATCH: {warning}\n# " +
                patched_code[start:end] +
                patched_code[end:]
            )
    
    return patched_code, issues