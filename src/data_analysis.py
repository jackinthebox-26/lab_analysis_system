from pathlib import Path
import tomllib

import pandas as pd
import numpy as np

from scipy.optimize import curve_fit


BASE_DIR = Path(__file__).resolve().parent.parent
config_path = BASE_DIR / 'config' / 'data_load_config.toml'

config_path = Path(config_path)
with open(config_path, 'rb') as f:
    config = tomllib.load(f)

def gaussian(x, amplitude, mean, stddev, offset):
    """1D Gaussian model with a baseline offset."""
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2)) + offset

def fit_gaussian_profile(x_data, y_data):
    """
    Fits a Gaussian profile to 1D data and returns the center and FWHM.
    
    Parameters:
        x_data (array-like): Independent variable (e.g., wavelength, position).
        y_data (array-like): Dependent variable (e.g., power, intensity).
        
    Returns:
        dict: Fitted parameters (center, FWHM, amplitude, stddev, offset, fit_y).
    """
    x = np.hstack(x_data).astype(float)
    y = np.hstack(y_data).astype(float)
    
    # Estimate initial guesses for stable optimization convergence
    offset_guess = np.min(y)
    amp_guess = np.max(y) - offset_guess
    mean_guess = x[np.argmax(y)]
    
    # Estimate standard deviation using full width at half max of raw data
    half_max = offset_guess + amp_guess / 2.0
    above_half = np.where(y >= half_max)[0]
    if len(above_half) > 1:
        fwhm_guess = x[above_half[-1]] - x[above_half[0]]
        stddev_guess = fwhm_guess / 2.35482
    else:
        stddev_guess = (np.max(x) - np.min(x)) / 6.0

    p0 = [amp_guess, mean_guess, stddev_guess, offset_guess]

    # Fit the Gaussian curve
    popt, _ = curve_fit(gaussian, x, y, p0=p0)
    amplitude, center, stddev, offset = popt

    # Standard deviation can converge as negative depending on initial signs
    stddev = abs(stddev)
    
    # Calculate FWHM from standard deviation
    fwhm = stddev / (1 / (2 * np.sqrt(2 * np.log(2))))  # 2 * sqrt(2 * ln(2)) * sigma

    return {
        "center": center,
        "fwhm": fwhm,
        "amplitude": amplitude,
        "stddev": stddev,
        "offset": offset,
        "fit_y": gaussian(x, *popt)
    }

class data_analysis:
    def __init__(self, raw_data, data_type):
        self.data = raw_data
        self.data_type = data_type
        match data_type:
            case 'OSA':
                self.data = self.OSA_analysis()
            case 'Aurora 4000':
                self.data = self.Aurora_analysis()
            case 'Ocean Optics':
                self.data = self.OCEAN_OPTICS_analysis()


    def OSA_analysis(self):
        fit_dict = fit_gaussian_profile(self.data['Wavelength (nm)'],
                                        self.data['Power (mW)'])

        
        self.data['Center Wavelength (nm)'] = fit_dict['center']
        self.data['FWHM Wavelength (nm)'] = fit_dict['fwhm']
        self.data['amplitude'] = fit_dict['amplitude']
        self.data['offset'] = fit_dict['offset']
        offset =self.data['offset'].iloc[0]
        self.data['Normalized Power (mW)'] = [np.hstack(self.data['Power (mW)']).astype(float) - offset]
        self.data['Normalized Power (mW)'] = self.data['Normalized Power (mW)'].apply(
                lambda p: np.array(p, dtype=float) / np.max(p)
                )
        return self.data


    def Aurora_analysis(self):
        fit_dict = fit_gaussian_profile(self.data['Wavelength (nm)'],
                                        self.data['Power (mW)'])
        
                
        self.data['Center Wavelength (nm)'] = fit_dict['center']
        self.data['FWHM Wavelength (nm)'] = fit_dict['fwhm']
        self.data['amplitude'] = fit_dict['amplitude']
        self.data['offset'] = fit_dict['offset']
        offset =self.data['offset'].iloc[0]
        self.data['Normalized Power (mW)'] = [np.hstack(self.data['Power (mW)']).astype(float) - offset]
        self.data['Normalized Power (mW)'] = self.data['Normalized Power (mW)'].apply(
                        lambda p: np.array(p, dtype=float) / np.max(p))
        return self.data

    def OCEAN_OPTICS_analysis(self):
            fit_dict = fit_gaussian_profile(self.data['Wavelength (nm)'],
                                            self.data['Power (mW)'])
            
                    
            self.data['Center Wavelength (nm)'] = fit_dict['center']
            self.data['FWHM Wavelength (nm)'] = fit_dict['fwhm']
            self.data['amplitude'] = fit_dict['amplitude']
            self.data['offset'] = fit_dict['offset']
            offset =self.data['offset'].iloc[0]
            self.data['Normalized Power (mW)'] = [np.hstack(self.data['Power (mW)']).astype(float) - offset]
            self.data['Normalized Power (mW)'] = self.data['Normalized Power (mW)'].apply(
                    lambda p: np.array(p, dtype=float) / np.max(p))
            return self.data


