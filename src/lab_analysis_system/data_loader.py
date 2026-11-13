from pathlib import Path
import logging

from lab_analysis_system.logger import setup_logging

import pandas as pd

from lab_analysis_system.instrument_base import Instrument
import lab_analysis_system.instruments

from lab_analysis_system.config import RAW_DIR, PROCESSED_DATA_PATH
from lab_analysis_system.parsers import data_parser
from lab_analysis_system.data_analysis import data_analysis

from lab_analysis_system.config import RAW_DIR, PROCESSED_DATA_PATH, DATA_LOAD_CONFIG
from lab_analysis_system.file_tools import find_all_files


logger = logging.getLogger(__name__)

DATA_TYPE_TO_CONFIG_KEY = {
    "OSA": "OSA_data",
    "RF analyser": "RF_data",
    "Aurora 4000": "aurora_data",
    "Ocean Optics": "ocean_optics_data",
    "FROG pulse stats": "FROG_data",
}

class LabDataLoader:
    def __init__(self, data_dir: str = str(RAW_DIR)):
        self.data_dir = Path(data_dir)
    
    def get_data_type(self, file_path: Path):  # Called in LabDataLoader.make_raw_data_dict()
        # Implement logic to determine the data type based on the file path or first 5 lines content
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            first_5_lines = [f.readline().strip() for _ in range(5)]
        for inst in Instrument.registry:
            if inst.can_identify(file_path, first_5_lines):
                print(f"Success! {inst.config_key}")
                return inst.config_key
            
        logger.info(f"{file_path.name} not categorized")
        return "Other"

 

    
    def make_raw_data_dict(self): # Called in LabDataLoader.initiate_data_saving()
        # Implement the logic to create a dictionary of raw data files categorized by their data type
        raw_data_dict = {}
        logger.info("Pull Data")
        all_files = find_all_files(self.data_dir, nested=False) # Get list of files 
        for file in all_files:  # file is a Path object
            data_type = self.get_data_type(file)  #Peak in all files and determine where the data came from
            if data_type not in raw_data_dict:  # If this is the first one, create the data type
                raw_data_dict[data_type] = []
            raw_data_dict[data_type].append(file) # Add it to the list of this type
        return raw_data_dict # A dictionary where the keys are data types and values is a list of files of this type

    def initiate_data_saving(self): # Called in main()
        logger.info("-------------------Initializing Data saving-------------------")
        logger.info('Initializing data catagorization')
        data_dict = self.make_raw_data_dict()  # Contains categorized data
        logger.info(f"Found the following data types: {data_dict.keys()}")
        logger.info('Data catagorized')
        
        
        logger.info('Initializing raw data processing and json saving.')
        for key, file_list in data_dict.items():
            logger.info(f'Key: {key}')
            records = []
            for file in file_list:
                logger.info(f"{' ' * 5}File: {file}")
                try:
                    raw_dict = data_parser(file, key).data
                    analyzed_dict = data_analysis(raw_dict, key).data
                    records.append(analyzed_dict)
                except Exception as e:
                    logger.warning(f"WARNING: Skipping {file.name} due to parse/analysis error: {e}")

            if records and key in DATA_TYPE_TO_CONFIG_KEY:
                temp_df = pd.DataFrame(records)
                PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
                config_key = DATA_TYPE_TO_CONFIG_KEY[key]
                file_name = PROCESSED_DATA_PATH / DATA_LOAD_CONFIG[config_key]["data_file"]
                temp_df.to_json(file_name)
                logger.info(f"Saved {key} data to {file_name}")


                
        

        
def main():
    setup_logging()
    LabDataLoader().initiate_data_saving()
if __name__ == "__main__":
    main()