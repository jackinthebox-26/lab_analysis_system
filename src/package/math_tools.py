import numpy as np

from scipy.optimize import curve_fit

def gaussian(x, amplitude, mean, stddev, offset):
    """1D Gaussian model with a baseline offset."""
    if not isinstance(x, np.ndarray):
        x = np.array(x)
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2)) + offset

def FWHM_to_stddev(FWHM):
    return (1 / (2 * np.sqrt(2 * np.log(2)))) * FWHM


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


    x_min, x_max = np.min(x), np.max(x)
    lower_bounds = [0.0, x_min, 0.0, -np.inf]
    upper_bounds = [np.inf, x_max, x_max - x_min, np.inf]
    try:
        popt, _ = curve_fit(
            gaussian, x, y, p0=p0, bounds=(lower_bounds, upper_bounds), maxfev=5000
        )
        amplitude, center, stddev, offset = popt
        stddev = abs(stddev)
        fwhm = stddev * (2 * np.sqrt(2 * np.log(2)))
        fit_y = gaussian(x, *popt)
    except (RuntimeError, ValueError) as e:
        print(f"Warning: Gaussian fit failed ({e}). Storing NaN values.")
        amplitude = center = stddev = fwhm = offset = np.nan
        fit_y = np.full_like(x, np.nan)
    return {
        "center": center,
        "fwhm": fwhm,
        "amplitude": amplitude,
        "stddev": stddev,
        "offset": offset,
        "fit_y": fit_y
    }
