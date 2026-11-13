# experiments/exp_date_template.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from lab_analysis_system.config import FIG_CONFIG, FIGURE_PATH
from lab_analysis_system.plot_helper import load_all_data, inspect_data_files, plot_spectrum_with_fit

def main():
    data_dict = load_all_data()
    inspect_data_files(data_dict)
    # Add day-specific plots below

if __name__ == "__main__":
    main()