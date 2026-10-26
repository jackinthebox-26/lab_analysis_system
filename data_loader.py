from pathlib import Path
from collections import defaultdict
import tomllib


import pandas as pd

config_path = Path('config/data_load_config.toml')
with open(config_path, 'rb') as f:
    config = tomllib.load(f)



from parsers import data_parser
class LabDataLoader:
    def __init__(self, data_dir: str = config['raw_data']['raw_data_folder']):
        self.data_dir = Path(data_dir)

    def find_all_files(self): # Called in LabDataLoader.make_raw_data_dict()
        # Implement the logic to find all files in the specified directory
        all_files = [f for f in self.data_dir.rglob('*') if f.is_file()]
        print(f"Found {len(all_files)} files in {self.data_dir}")
        return all_files

    
    def get_data_type(self, file_path: Path):  # Called in LabDataLoader.make_raw_data_dict()
        # Implement logic to determine the data type based on the file path or first 5 lines content
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            first_5_lines = [f.readline().strip() for _ in range(5)]

        if "Device Name:Aurora 4000" in first_5_lines[4]:
            return "Aurora 4000"
        elif "Spectrometer: HR600944" in first_5_lines[4]:
            return "Ocean Optics"
        elif "Date (day-month-year)," in first_5_lines[0]:
            return "RF analyser"
        elif ",dBm" in first_5_lines[0]:
            return "OSA"
        elif "Pulse_Stats" in file_path.name:
            return "FROG pulse stats"
        elif "RetrievedFT" in file_path.name:
            return "FROG retrieved FT"
        elif "Pulse_Time_Domain" in file_path.name:
            return "FROG time domain"
        elif "Pulse_Freq_Domain" in file_path.name:
            return "FROG frequency domain"
        elif "Pulse_Complex_Time_Domain" in file_path.name:
            return "FROG complex time domain"
        elif "Gate" in file_path.name:
            return "FROG gate"
        elif "FROGtrace" in file_path.name:
            return "FROG trace"
        else:
            print(f"{file_path.name} not categorized")
            return "Other"

    def load_data(self, file_path: Path, data_type: str): # Called in LabDataLoader.initiate_data_saving
            # Implement the logic to load data based on the data type and output a dataframe with all associated raw data
            data = data_parser(file_path, data_type).data
           
            
            return pd.DataFrame([data])

    
    def make_raw_data_dict(self): # Called in LabDataLoader.initiate_data_saving()
        # Implement the logic to create a dictionary of raw data files categorized by their data type
        raw_data_dict = {}
        print("Pull Data")
        all_files = self.find_all_files() # Get list of files 
        for file in all_files:  # file is a Path object
            data_type = self.get_data_type(file)  #Peak in all files and determine where the data came from
            if data_type not in raw_data_dict:  # If this is the first one, create the data type
                raw_data_dict[data_type] = []
            raw_data_dict[data_type].append(file) # Add it to the list of this type
        return raw_data_dict # A dictionary where the keys are data types and values is a list of files of this type

    def initiate_data_saving(self): # Called in main()
        print('Initiate data saving')
        print('Initializing data catagorization')
        data_dict = self.make_raw_data_dict()  # Contains categorized data
        print(f"Found the following data types: {data_dict.keys()}")
        print('Data catagorized')
        
        root_path = Path(config['processed_data']['processed_data_folder'])

        print('Initializing raw data processing and json saving.')
        for key, file_list in data_dict.items():
            temp_df = pd.DataFrame()
            print(f'Key: {key}')
            for file in file_list:
                print(f"File: {file}")
                this_file_df = self.load_data(file, key)
                print('----this_file_df--------')
                print(this_file_df)
                if this_file_df is not None:
                    temp_df = pd.concat([temp_df, this_file_df], ignore_index=True, axis=0)
            print('------temp_df-----')
            print(temp_df)
            if this_file_df is not None:
                file_name = key.replace(" ", "_") + "_data.json"
                temp_df.to_json(root_path / file_name, indent=4)
                print(f"Saved {key} data to {file_name}")

                reload_data = pd.read_json(root_path / file_name)
                print('reloaded data')
                print(reload_data)
                
        

        
def main():
    LabDataLoader().initiate_data_saving()
if __name__ == "__main__":
    main()