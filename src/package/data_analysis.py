from pathlib import Path
import tomllib

import pandas as pd
import numpy as np


from package.config import BASE_DIR, DATA_LOAD_CONFIG, FIG_CONFIG, PROCESSED_DATA_PATH, FIGURE_PATH
from package.math_tools import gaussian, fit_gaussian_profile


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


