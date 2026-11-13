# python3
from pathlib import Path
import lab_analysis_system.instruments
import argparse

from lab_analysis_system.data_loader import LabDataLoader
from lab_analysis_system.graph_default import create_all_graphs
from lab_analysis_system.file_tools import clean_directories
from lab_analysis_system.metadata import save_metadata
from lab_analysis_system.logger import setup_logging


from lab_analysis_system.config import BASE_DIR, RAW_DIR, FIGURE_PATH, PROCESSED_DATA_PATH, DATA_LOAD_CONFIG, resolve_paths
import importlib.util
import shutil
import logging

logger = logging.getLogger("lab_analysis_system.main")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the lab spectroscopy analysis pipeline.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d", "--date",
        type=str,
        help="Experiment date (e.g., '2026/10/29' or '2026-10-29'), resolved relative to data root.",
    )
    group.add_argument(
        "--data-dir",
        type=str,
        help="Explicit path to raw data directory.",
    )
    return parser.parse_args()


def normalize_date_folder(date_str: str) -> str:
    # Replace dashes or underscores with forward slashes: "2026-10-29" -> "2026/10/29"
    clean_date = date_str.strip().replace("-", "/").replace("_", "/")
    prefix = DATA_LOAD_CONFIG["src_config"]["prefix_to_head"]  # ".."
    return f"{prefix}/{clean_date}"

def run_daily_custom_plots(raw_dir: Path = RAW_DIR, processed_dir: Path = PROCESSED_DATA_PATH, figure_dir: Path = FIGURE_PATH):
    # Turns '.../2026/11/03' into '2026_11_03.py'
    parts = raw_dir.resolve().parts[-3:]
    date_slug = "_".join(parts)

    experiments_dir = BASE_DIR / "experiments"
    experiments_dir.mkdir(parents=True, exist_ok=True)

    script_path = experiments_dir / f"exp_{date_slug}.py"
    template_path = experiments_dir / "exp_date_template.py"

    if not script_path.is_file():
        if template_path.is_file():
            shutil.copyfile(template_path, script_path)
            logger.info(f"Created new custom plot script from template: {script_path.name}")
        else:
            logger.warning(f"Warning: Neither {script_path.name} nor template.py found. Skipping custom plots.")
            return

    if not script_path.is_file():
        logger.info(f"No custom script found at {script_path}, skipping custom plots.")
        return

    logger.info(f"Running custom plots from {script_path.name}")
    spec = importlib.util.spec_from_file_location(f"exp_{date_slug}", script_path)
    if spec is None or spec.loader is None:
        logger.error(f"Failed to load the custom script at {script_path}.")
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "main"):
        module.main()

def main():
    args = parse_args()
    if args.date:
        target_folder = normalize_date_folder(args.date)
    elif args.data_dir:
        target_folder = args.data_dir
    else:
        target_folder = None  # Falls back to data_load_config.toml

    raw_dir, processed_dir, figure_dir = resolve_paths(target_folder)
    setup_logging(log_dir=None)
    clean_directories([processed_dir, figure_dir])
    setup_logging(log_dir=processed_dir)
    logger.info("Starting lab analysis pipeline for RAW_DIR=%s", raw_dir)
    LabDataLoader(data_dir=raw_dir, processed_dir=processed_dir).initiate_data_saving()
    create_all_graphs(processed_dir=processed_dir, figure_dir=figure_dir)
    run_daily_custom_plots(raw_dir=raw_dir, processed_dir=processed_dir, figure_dir=figure_dir)
    save_metadata(raw_dir=raw_dir, processed_dir=processed_dir, figure_dir=figure_dir)
    logger.info("Pipeline run completed successfully.")

if __name__ == '__main__':
    main()