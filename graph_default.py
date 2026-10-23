import pandas as pd

OSA_data = pd.read_json("processed_data/OSA_data.json")

print(OSA_data.head())