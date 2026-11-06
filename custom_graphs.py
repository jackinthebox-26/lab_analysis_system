
import tomllib
from pathlib import Path
import re

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np

from package.config import DATA_LOAD_CONFIG, FIG_CONFIG, PROCESSED_DATA_PATH, FIGURE_PATH, BASE_DIR, RAW_DIR
from package.math_tools import gaussian, FWHM_to_stddev

def load_all_data() -> dict[str, pd.DataFrame]:
    data_sources = {
        "osa": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG['OSA_data']['data_file'],
        "rf": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG['RF_data']['data_file'],
        "aurora": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG['aurora_data']['data_file'],
        "ocean_optics": PROCESSED_DATA_PATH / DATA_LOAD_CONFIG['ocean_optics_data']['data_file'],
    }
    
    loaded_data: dict[str, pd.DataFrame] = {}
    
    for key, path in data_sources.items():
        path = Path(path)
        if path.exists():
            loaded_data[key] = pd.read_json(path)
        else:
            print(f"Warning: Data file for {key} not found at {path}.")
            
    return loaded_data


def inspect_data_files():
    data_dict = load_all_data()

    if 'osa' in data_dict:
        print('--OSA data--')
        print(data_dict['osa'].columns)
        print(data_dict['osa'].info())
    else:
        print("No OSA data found.")
    
    if 'rf' in data_dict:
        print('--RF data--')
        print(data_dict['rf'].columns)
        print(data_dict['rf'].info())
    else:
        print("No RF data found.")

    if 'aurora' in data_dict:
        print('--Aurora 4000 data--')
        print(data_dict['aurora'].columns)
        print(data_dict['aurora'].info())
    else:
        print("No Aurora 4000 data found.")

    if 'ocean_optics' in data_dict:
        print('--Ocean Optics data--')
        print(data_dict['ocean_optics'].columns)
        print(data_dict['ocean_optics'].info())
    else:
        print("No Ocean Optics data found.")

def tuning_to_1016():
    data_dict = load_all_data()
    osa_data = data_dict.get('osa')

    step_1 = osa_data[osa_data['exp_index'] == 61]
    step_2 = osa_data[osa_data['exp_index'] == 62]
    step_3 = osa_data[osa_data['exp_index'] == 63]
    step_4 = osa_data[osa_data['exp_index'] == 64]
    step_5 = osa_data[osa_data['exp_index'] == 65]
    step_6 = osa_data[osa_data['exp_index'] == 66]
    step_7 = osa_data[osa_data['exp_index'] == 67]
    step_8 = osa_data[osa_data['exp_index'] == 68]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(step_1['Wavelength (nm)'].item(), step_1['Normalized Power (mW)'].item(), label='Initial mode lock', color='blue')
    ax.plot(step_2['Wavelength (nm)'].item(), step_2['Normalized Power (mW)'].item(), label='Reduce pump current to 500 mA', color='red')
    ax.plot(step_3['Wavelength (nm)'].item(), step_3['Normalized Power (mW)'].item(), label='Increase HWP1 to 134 deg', color='green')
    ax.plot(step_4['Wavelength (nm)'].item(), step_4['Normalized Power (mW)'].item(), label='Tune to 1030 nm and increase pump current to 550 mA', color='orange')
    ax.plot(step_5['Wavelength (nm)'].item(), step_5['Normalized Power (mW)'].item(), label='Tune down to 1020 nm, increase pump current to 580 mA and decrease HWP2 to 274 deg ', color='purple')
    ax.plot(step_6['Wavelength (nm)'].item(), step_6['Normalized Power (mW)'].item(), label='Tune down to 1017 nm and let it settle', color='brown')
    ax.plot(step_7['Wavelength (nm)'].item(), step_7['Normalized Power (mW)'].item(), label='Tune to 1016 nm', color='gray')
    ax.plot(step_8['Wavelength (nm)'].item(), step_8['Normalized Power (mW)'].item(), label='Increase output power by setting HWP2 to 282 deg', color='black')
    ax.set_xlabel('Wavelength')
    ax.set_ylabel('Normalized Intensity')
    ax.set_title('Tuning to 1016')
    ax.legend()
    ax.grid()
    plt.savefig(FIGURE_PATH / 'tuning_to_1016.png', dpi=300)



def tuning_to_1016_cascade():
    data_dict = load_all_data()
    osa_data = data_dict.get('osa')

    # Define metadata for each step
    steps = [
        (61, 'Initial mode lock', '#1f77b4'),
        (62, 'Reduce pump to 500 mA', '#d62728'),
        (63, 'Increase HWP1 to 134 deg', '#2ca02c'),
        (64, 'Tune to 1030 nm, pump 550 mA', '#ff7f0e'),
        (65, 'Tune 1020 nm, pump 580 mA, HWP2 274 deg', '#9467bd'),
        (66, 'Tune to 1017 nm (settling)', '#8c564b'),
        (67, 'Tune to 1016 nm', '#7f7f7f'),
        (68, 'Increase power (HWP2 282 deg)', '#17becf'),
    ]

    # Initialize 3D plot
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(projection='3d')

    reversed_steps = steps[::-1]
    y_positions = np.arange(len(reversed_steps))

    for y_pos, (exp_idx, label, color) in zip(y_positions, reversed_steps):
        step_data = osa_data[osa_data['exp_index'] == exp_idx]
        
        x = np.array(step_data['Wavelength (nm)'].item())
        z = np.array(step_data['Normalized Power (mW)'].item())

        ax.plot(
            x,
            np.full_like(x, y_pos),
            z,
            color=color,
            markersize=3,
            linewidth=1.2,
            zorder=10 - y_pos
        )

        #z_min = 0
        #verts = [(x[0], z_min), *zip(x, z), (x[-1], z_min)]
        #poly = PolyCollection([verts], facecolors='#e0e0e0', edgecolors='none', alpha=0.7)
        #ax.add_collection3d(poly, zs=y_pos, zdir='y')

    # Update y-tick labels to match the reversed order
    ax.set_yticks(y_positions)
    ax.set_yticklabels([8-f for f in y_positions], fontsize=8)


    # Set optimal 3D perspective view angle
    ax.view_init(elev=26, azim=-60)
    ax.set_title('Tuning to 1016 nm (Waterfall Cascade)', pad=20, fontsize=13)
    ax.set_xlabel('Wavelength (nm)', labelpad=10, fontsize=10)
    ax.set_ylabel('Step Number', labelpad=10, fontsize=10)
    ax.set_zlabel('Normalized Power (mW)', labelpad=10, fontsize=10)
    plt.tight_layout()
    plt.savefig(FIGURE_PATH / 'tuning_to_1016_cascade.png', dpi=300)
    # plt.show()

def main():
    
    inspect_data_files()
    tuning_to_1016()
    tuning_to_1016_cascade()


if __name__ == "__main__":
    main()