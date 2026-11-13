import numpy as np
from lab_analysis_system.data_analysis import data_analysis

def test_analyze_spectrum_normalization(mocker):
    # Mock the fit_gaussian_profile to avoid testing math_tools logic here
    mocker.patch(
        'lab_analysis_system.data_analysis.fit_gaussian_profile', 
        return_value={'center': 800, 'fwhm': 10, 'amplitude': 5, 'offset': 2, 'stddev': 4, 'fit_y': []}
    )
    
    raw_data = {
        'Wavelength (nm)': [799, 800, 801],
        'Power (mW)': [2, 12, 2] # Max is 12, offset is 2 -> Max shifted is 10
    }
    
    analyzer = data_analysis(raw_data, 'OSA')
    
    norm_power = analyzer.data['Normalized Linear Power (a.u.)']
    assert np.isclose(max(norm_power), 1.0)
    assert np.isclose(min(norm_power), 0.0)