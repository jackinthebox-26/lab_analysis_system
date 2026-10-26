# python3

from src.data_loader import LabDataLoader
from src.graph_default import create_all_graphs

def main():
    LabDataLoader().initiate_data_saving()
    create_all_graphs()

if __name__ == '__main__':
    main()