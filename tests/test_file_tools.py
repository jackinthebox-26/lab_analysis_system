import pytest
from pathlib import Path
from package.file_tools import clean_folder
from package.config import RAW_DIR

from package.file_tools import find_all_files, clean_folder

def test_clean_folder_safety_abort():
    # Ensure attempting to clean the raw data directory raises a RuntimeError
    with pytest.raises(RuntimeError, match="Safety abort: Refusing to clean RAW_DIR!"):
        clean_folder(RAW_DIR)


def test_find_all_files_flat(tmp_path):
    (tmp_path / "file1.txt").write_text("test")
    (tmp_path / "file2.csv").write_text("test")
    
    # Create a directory to ensure it is ignored
    (tmp_path / "subdir").mkdir()
    
    files = find_all_files(tmp_path, nested=False)
    assert len(files) == 2
    assert all(f.is_file() for f in files)

def test_find_all_files_nested(tmp_path):
    (tmp_path / "file1.txt").write_text("test")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file2.csv").write_text("test")
    
    files = find_all_files(tmp_path, nested=True)
    assert len(files) == 2

def test_clean_folder_deletes_unprotected(tmp_path):
    # Create a protected and unprotected file
    protected = tmp_path / "script.py"
    protected.write_text("print('hello')")
    
    unprotected = tmp_path / "data.csv"
    unprotected.write_text("1,2,3")
    
    deleted_count = clean_folder(tmp_path)
    
    assert deleted_count == 1
    assert not unprotected.exists()
    assert protected.exists()