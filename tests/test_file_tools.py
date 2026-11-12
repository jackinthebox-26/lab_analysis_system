import pytest
from pathlib import Path
from package.file_tools import clean_folder
from package.config import RAW_DIR

def test_clean_folder_safety_abort():
    # Ensure attempting to clean the raw data directory raises a RuntimeError
    with pytest.raises(RuntimeError, match="Safety abort: Refusing to clean RAW_DIR!"):
        clean_folder(RAW_DIR)