# python3

import lab_analysis_system.instruments

from lab_analysis_system.data_loader import LabDataLoader
from lab_analysis_system.graph_default import create_all_graphs
from lab_analysis_system.file_tools import clean_directories
from lab_analysis_system.metadata import save_metadata
from lab_analysis_system.logger import setup_logging

from lab_analysis_system.config import BASE_DIR, RAW_DIR, FIGURE_PATH, PROCESSED_DATA_PATH
import importlib.util
import shutil
import logging

logger = logging.getLogger(__name__)

def run_daily_custom_plots():
    # Turns '.../2026/11/03' into '2026_11_03.py'
    parts = RAW_DIR.resolve().parts[-3:]
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
    setup_logging(log_dir=None)
    clean_directories()
    setup_logging(log_dir=PROCESSED_DATA_PATH)
    logger.info("Starting lab analysis pipeline for PROCESSED_DATA=%s", PROCESSED_DATA_PATH)
    LabDataLoader().initiate_data_saving()
    create_all_graphs()
    run_daily_custom_plots()
    save_metadata()
    logger.info("Pipeline run completed successfully.")

if __name__ == '__main__':
    main()