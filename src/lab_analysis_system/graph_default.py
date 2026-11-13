import logging
import pandas as pd

from pathlib import Path

from lab_analysis_system.instrument_base import Instrument
from lab_analysis_system.logger import setup_logging
from lab_analysis_system.config import DATA_LOAD_CONFIG, PROCESSED_DATA_PATH, FIGURE_PATH

logger = logging.getLogger(__name__)


def load_data(config_key: str, processed_dir: Path) -> pd.DataFrame | None:
    file_path = processed_dir / DATA_LOAD_CONFIG[config_key]['data_file']
    logger.info(f"Loading data from {file_path}")
    if not file_path.is_file():
        return None
    return pd.read_json(file_path)


def create_all_graphs(processed_dir: Path = PROCESSED_DATA_PATH, figure_dir: Path = FIGURE_PATH):
    logger.info("-------------------Initializing plot creation-------------------")
    for inst in Instrument.get_all_instruments():
        logger.info(f"Creating {inst.name} graphs")
        data = load_data(inst.name, processed_dir)
        if data is None:
            logger.info(f"No {inst.name} data")
            continue
        for _, row in data.iterrows():
            inst.plot(row, figure_dir)
    logger.info("Completed graph creation")


if __name__ == "__main__":
    setup_logging()
    create_all_graphs()