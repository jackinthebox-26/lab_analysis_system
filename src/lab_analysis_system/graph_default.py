import logging
import pandas as pd

from lab_analysis_system.instrument_base import Instrument
import lab_analysis_system.instruments
from lab_analysis_system.logger import setup_logging
from lab_analysis_system.config import DATA_LOAD_CONFIG, PROCESSED_DATA_PATH

logger = logging.getLogger(__name__)


def load_data(config_key: str) -> pd.DataFrame | None:
    file_path = PROCESSED_DATA_PATH / DATA_LOAD_CONFIG[config_key]['data_file']
    logger.info(f"Loading data from {file_path}")
    if not file_path.is_file():
        return None
    return pd.read_json(file_path)


def create_all_graphs():
    logger.info("-------------------Initializing plot creation-------------------")
    for inst in Instrument.get_all_instruments():
        logger.info(f"Creating {inst.name} graphs")
        data = load_data(inst.name)
        if data is None:
            logger.info(f"No {inst.name} data")
            continue
        for _, row in data.iterrows():
            inst.plot(row)
    logger.info("Completed graph creation")


if __name__ == "__main__":
    setup_logging()
    create_all_graphs()