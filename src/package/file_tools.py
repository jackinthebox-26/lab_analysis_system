# src/package/file_tools.py
from pathlib import Path
import logging

import shutil

from package.config import PROCESSED_DATA_PATH, FIGURE_PATH, RAW_DIR

logger = logging.getLogger(__name__)
folder_list = [PROCESSED_DATA_PATH, FIGURE_PATH]
PROTECTED_EXTENSIONS = [".py", ".toml", ".md", ".txt", ".gitkeep", ".gitignore", ".pdf", ".svg"]

def clean_folder(folder_path):
    if folder_path.resolve() == RAW_DIR.resolve():
        raise RuntimeError("Safety abort: Refusing to clean RAW_DIR!")
    deleted_count = 0
    if not folder_path.exists():
        logger.info(f"Directory does not exist yet: {folder_path}")
        return 0
    for item in folder_path.iterdir():
        if item.suffix not in PROTECTED_EXTENSIONS:
            if item.is_dir():
                shutil.rmtree(item)
                logger.info(f"Deleted {item.name}")
                deleted_count += 1
            if item.is_file():
                item.unlink()
                logger.info(f"Deleted {item.name}")
                deleted_count += 1
    return deleted_count



def clean_directories():
    logger.info("-------------------Initializing tree cleaning-------------------")
    deleted_count = 0
    for folder in folder_list:
        deleted_count += clean_folder(folder)
    logger.info(f"Deleted {deleted_count} files from {len(folder_list)} folders")
    


def find_all_files(data_dir: Path | str, nested: bool = False, resolve: bool = False) -> list[Path]:
    data_dir = Path(data_dir)
    if not data_dir.exists():
        return []
    iterator = data_dir.rglob("*") if nested else data_dir.iterdir()
    all_files = [f.resolve() if resolve else f for f in iterator if f.is_file()]
    logger.info(f"Found {len(all_files)} files in {data_dir}")
    return all_files


def main():
    clean_directories()
if __name__ == "__main__":
    main()