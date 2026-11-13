# src/package/logger.py
import logging
from pathlib import Path
import sys


def setup_logging(
    log_dir: Path | None = None,
    log_filename: str = "data_analysis_log.log",
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Configures root logging for the `package` namespace.
    - Console receives clean INFO+ messages.
    - File (if log_dir is provided) receives detailed DEBUG+ records with module & line info.
    """
    pkg_logger = logging.getLogger("lab_analysis_system")
    pkg_logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if setup_logging() is called multiple times
    if pkg_logger.handlers:
        pkg_logger.handlers.clear()

    # 1. Console Handler (clean, human-readable for terminal runs)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_fmt)
    pkg_logger.addHandler(console_handler)

    # 2. File Handler (detailed provenance & debugging log)
    if log_dir is not None:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / log_filename

        file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        file_handler.setLevel(file_level)
        file_fmt = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_fmt)
        pkg_logger.addHandler(file_handler)

    # Avoid double-printing if root logger also has handlers
    pkg_logger.propagate = False
    return pkg_logger