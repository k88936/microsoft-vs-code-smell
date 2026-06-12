from pathlib import Path
import shutil


def validate_file(file_path: Path) -> None:
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(file_path)

def word_count(file_name: str) -> int:
    file_path = Path(file_name)
    validate_file(file_path)
    text = file_path.read_text(encoding="utf-8")
    return len(text.split())


def copy_file(src_name: str, dest_name: str) -> None:
    file_path = Path(src_name)
    destination = Path(dest_name)
    validate_file(file_path)
    shutil.copyfile(file_path, destination)