from pathlib import Path
from collections import defaultdict

import pandas as pd

from parsers import parse_FROG_pulse_stats, parse_OSA, parse_RF_analyser, parse_aurora_4000, parse_ocean_optics

class LabDataLoader:
    def __init__(self, data_dir: str = "raw_data"):
        self.data_dir = Path(data_dir)

    def find_all_files(self):
        # Implement the logic to find all files in the specified directory
        all_files = [f for f in self.data_dir.rglob('*') if f.is_file()]
        print(f"Found {len(all_files)} files in {self.data_dir}")
        return all_files

    
    def get_data_type(self, file_path: Path):
        # Implement logic to determine the data type based on the file path or content
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
            return "Other"

    def load_data(self, file_path: Path, data_type: str):
            # Implement the logic to load data based on the data type
            match data_type:
                case "OSA":
                    data = parse_OSA(file_path)
                case "Aurora 4000":
                    # Implement the logic to parse Aurora 4000 data
                    data = parse_aurora_4000(file_path)
                case "Ocean Optics":
                    data = parse_ocean_optics(file_path)
                case "RF analyser":
                    data = parse_RF_analyser(file_path)
                case "FROG pulse stats":
                    data = parse_FROG_pulse_stats(file_path)
                case _:
                    data = {"source_file": file_path.name, "message": "No parser available for this data type."}   
            
            return pd.DataFrame([data])

    
    def make_raw_data_dict(self):
        # Implement the logic to create a dictionary of raw data files categorized by their data type
        raw_data_dict = {}
        all_files = self.find_all_files()
        for file in all_files:
            data_type = self.get_data_type(file)
            if data_type not in raw_data_dict:
                raw_data_dict[data_type] = []
            raw_data_dict[data_type].append(file)
        return raw_data_dict

    def initiate_data_saving(self):
        data_dict = self.make_raw_data_dict()
        OSA_data = []
        RF_data = []
        pulse_data = []
        aurora_data = []
        ocean_optics_data = []
        for data_type, files in data_dict.items():
            for file in files:
                data = self.load_data(file, data_type)
                match data_type:
                    case "OSA":
                        OSA_data.append(file)
                    case "RF analyser":
                        RF_data.append(file)
                    case "FROG pulse stats":
                        pulse_data.append(file)
                    case "Aurora 4000":
                        aurora_data.append(file)
                    case "Ocean Optics":
                        ocean_optics_data.append(file)


        root_path = Path('processed_data')
        OSA_dataframe = pd.DataFrame()
        for file in OSA_data:
            OSA_dataframe = pd.concat([OSA_dataframe, self.load_data(file, "OSA")], ignore_index=True)
        OSA_dataframe.to_json(root_path / "OSA_data.json", orient="records", indent=4)

        RF_dataframe = pd.DataFrame()
        for file in RF_data:
            RF_dataframe = pd.concat([RF_dataframe, self.load_data(file, "RF analyser")], ignore_index=True)
        RF_dataframe.to_json(root_path / "RF_data.json", orient="records", indent=4)

        pulse_dataframe = pd.DataFrame()
        for file in pulse_data:
            pulse_dataframe = pd.concat([pulse_dataframe, self.load_data(file, "FROG pulse stats")], ignore_index=True)
        pulse_dataframe.to_json(root_path / "pulse_data.json", orient="records", indent=4)

        aurora_dataframe = pd.DataFrame()
        for file in aurora_data:
            aurora_dataframe = pd.concat([aurora_dataframe, self.load_data(file, "Aurora 4000")], ignore_index=True)
        aurora_dataframe.to_json(root_path / "aurora_data.json", orient="records", indent=4)

        ocean_optics_dataframe = pd.DataFrame()
        for file in ocean_optics_data:
            ocean_optics_dataframe = pd.concat([ocean_optics_dataframe, self.load_data(file, "Ocean Optics")], ignore_index=True)
        ocean_optics_dataframe.to_json(root_path / "ocean_optics_data.json", orient="records", indent=4)

        
def main():
    LabDataLoader().initiate_data_saving()
if __name__ == "__main__":
    main()