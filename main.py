# python3

from pathlib import Path
import sys



from package.data_loader import LabDataLoader
from package.graph_default import create_all_graphs
from package.file_tools import clean_directories
from package.metadata import save_metadata

def main():
    clean_directories()
    LabDataLoader().initiate_data_saving()
    create_all_graphs()
    save_metadata()

if __name__ == '__main__':
    main()