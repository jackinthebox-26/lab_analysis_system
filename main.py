# python3

from package.data_loader import LabDataLoader
from package.graph_default import create_all_graphs
from package.file_tools import clean_directories
from package.metadata import save_metadata
import custom_graphs as cg

def main():
    clean_directories()
    LabDataLoader().initiate_data_saving()
    create_all_graphs()
    cg.main()
    save_metadata()

if __name__ == '__main__':
    main()