import numpy as np
from package.math_tools import gaussian, fit_gaussian_profile

def test_fit_gaussian_profile_clean_data():
    # Generate a perfect Gaussian to test the fitting algorithm
    x_data = np.linspace(700, 900, 200)
    true_amplitude, true_center, true_stddev, true_offset = 10.0, 800.0, 5.0, 2.0
    y_data = gaussian(x_data, true_amplitude, true_center, true_stddev, true_offset)
    
    result = fit_gaussian_profile(x_data, y_data)
    
    assert np.isclose(result["center"], true_center, atol=0.1)
    assert np.isclose(result["amplitude"], true_amplitude, atol=0.1)
    assert np.isclose(result["offset"], true_offset, atol=0.1)
    assert not np.isnan(result["fwhm"])