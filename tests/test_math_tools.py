import numpy as np
from package.math_tools import gaussian, FWHM_to_stddev, fit_gaussian_profile

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



def test_gaussian_evaluation():
    x = np.array([0, 800, 1600])
    amplitude, mean, stddev, offset = 10, 800, 5, 2
    y = gaussian(x, amplitude, mean, stddev, offset)
    
    assert np.isclose(y[1], 12.0)  # Peak: 10 + 2
    assert y[0] < 3.0  # Far from mean, should be close to offset
    assert y[2] < 3.0

def test_FWHM_to_stddev():
    fwhm = 10.0
    expected_stddev = fwhm / (2 * np.sqrt(2 * np.log(2)))
    assert np.isclose(FWHM_to_stddev(fwhm), expected_stddev)

def test_fit_gaussian_profile_flat_data():
    x_data = np.linspace(700, 900, 100)
    y_data = np.ones(100) * 5.0  # Flat line, no Gaussian peak
    
    result = fit_gaussian_profile(x_data, y_data)
    
    # Depending on scipy versions, this might either return the bounds or fail. 
    # Our math_tools.py catches failures and returns NaNs.
    if np.isnan(result["center"]):
        assert np.isnan(result["amplitude"])
    else:
        assert np.isclose(result["amplitude"], 0.0, atol=1e-5)