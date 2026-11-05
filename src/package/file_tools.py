from pathlib import Path
import shutil

import tomllib

from package.config import PROCESSED_DATA_PATH, FIGURE_PATH

folder_list = [PROCESSED_DATA_PATH, FIGURE_PATH]
PROTECTED_EXTENSIONS = [".py", ".toml", ".md", ".txt", ".gitkeep", ".gitignore"]

def clean_folder(folder_path):
    deleted_count = 0
    if not folder_path.exists():
        print(f"Directory does not exist yet: {folder_path}")
        return 0
    for item in folder_path.iterdir():
        if item.suffix not in PROTECTED_EXTENSIONS:
            if item.is_dir():
                shutil.rmtree(item)
                print(f"Deleted {item.name}")
                deleted_count += 1
            if item.is_file():
                item.unlink()
                print(f"Deleted {item.name}")
                deleted_count += 1
    return deleted_count



def clean_directories():
    print("-------------------Initializing tree cleaning-------------------")
    deleted_count = 0
    for folder in folder_list:
        deleted_count += clean_folder(folder)
    print(f"Deleted {deleted_count} files from {len(folder_list)} folders")
    

def main():
    clean_directories()
if __name__ == "__main__":
    main()