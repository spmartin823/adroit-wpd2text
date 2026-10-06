import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


def extract_text(file_bytes: bytes) -> str:
    package_dir = Path(__file__).resolve().parent
    library_path_variable = "DYLD_LIBRARY_PATH" if sys.platform == "darwin" else "LD_LIBRARY_PATH"
    with TemporaryDirectory() as temporary_dir:
        document_path = Path(temporary_dir) / "document.wpd"
        document_path.write_bytes(file_bytes)
        result = subprocess.run(
            [str(package_dir / "bin" / "wpd2text"), str(document_path)],
            check=True,
            capture_output=True,
            env=os.environ | {library_path_variable: str(package_dir / "lib")},
        )
    return result.stdout.decode("utf-8")
