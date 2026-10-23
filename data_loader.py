from pathlib import Path

class LabDataLoader:
    def __init__(self, data_dir: str = "raw_data"):
        self.data_dir = Path(data_dir)

    def find_all_files(self):
        # Implement the logic to find all files in the specified directory
        all_files = [f for f in self.data_dir.rglob('*') if f.is_file()]
        print(f"Found {len(all_files)} files in {self.data_dir}")
        return all_files

    def load_data(self, data_type):
        # Implement the logic to load data based on the data type
        match data_type:
            case "OSA":
                print("Loading OSA data...")

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

def main():
    raw_data_dict = LabDataLoader().make_raw_data_dict()
    print("Raw data dictionary:")
    for data_type, files in raw_data_dict.items():
        print(f"  {data_type}: {len(files)} files")

if __name__ == "__main__":
    main()