import numpy as np


from package.config import BASE_DIR, DATA_LOAD_CONFIG, FIG_CONFIG, PROCESSED_DATA_PATH, FIGURE_PATH
from package.math_tools import gaussian, fit_gaussian_profile


class data_analysis:
    def __init__(self, raw_data, data_type):
        self.data = raw_data
        self.data_type = data_type
        match data_type:
            case 'OSA' | 'Aurora 4000' | 'Ocean Optics':
                self.data = self.analyze_spectrum()


    def analyze_spectrum(self):
        fit_dict = fit_gaussian_profile(
            self.data['Wavelength (nm)'],
            self.data['Power (mW)']
        )

        self.data['Center Wavelength (nm)'] = fit_dict['center']
        self.data['FWHM Wavelength (nm)'] = fit_dict['fwhm']
        self.data['amplitude'] = fit_dict['amplitude']
        self.data['offset'] = fit_dict['offset']

        power = np.asarray(self.data['Power (mW)'], dtype=float)
        offset = fit_dict['offset'] if not np.isnan(fit_dict['offset']) else np.min(power)
        shifted = power - offset
        max_val = np.max(shifted)
        norm_power = shifted / max_val if max_val > 0 else shifted

        self.data['Normalized Power (mW)'] = norm_power.tolist()
        return self.data


