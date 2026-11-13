# experiments/exp_date_template.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path

from lab_analysis_system.config import FIG_CONFIG, FIGURE_PATH, PROCESSED_DATA_PATH
from lab_analysis_system.plot_helper import load_all_data, inspect_data_files, plot_spectrum_with_fit

def main(processed_dir: Path = PROCESSED_DATA_PATH, figure_dir: Path = FIGURE_PATH):
    data_dict = load_all_data(processed_dir)
    inspect_data_files(data_dict)
    # Add day-specific plots below

if __name__ == "__main__":
    main()