import zipfile
from pathlib import Path
from typing import List, Dict
import tempfile
import os


def extract_python_files(zip_path: str) -> List[Dict[str, str]]:
    files = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            with tempfile.TemporaryDirectory() as tmpdir:
                z.extractall(tmpdir)
                tmp_path = Path(tmpdir)
                for py_file in tmp_path.rglob("*.py"):
                    if py_file.is_file() and py_file.stat().st_size < 10_000_000:
                        try:
                            content = py_file.read_text(encoding="utf-8", errors="ignore")
                            rel_path = str(py_file.relative_to(tmp_path))
                            files.append({"path": rel_path, "content": content})
                        except:
                            continue
    except zipfile.BadZipFile:
        pass
    return files