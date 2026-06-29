import numpy as np
import xarray as xr


def decompose(da: xr.DataArray, num_harmonics: int = 2, period: float = 365.25) -> xr.Dataset:
    """
    Pixel-wise Harmonic (Fourier) decomposition on a (time, latitude, longitude) DataArray.
    Returns an xr.Dataset with trend, seasonal, and residual.
    """

    # 1. Compute time vector in elapsed days from the start
    # This assumes da.time is a standard datetime coordinate
    t = (da.time - da.time[0]).dt.days.values

    # 2. Build the Design Matrices ONCE for the entire dataset (massive speedup)
    X_trend = np.column_stack((np.ones(len(t)), t))

    X_season_list = []
    for k in range(1, num_harmonics + 1):
        X_season_list.append(np.sin(2 * np.pi * k * t / period))
        X_season_list.append(np.cos(2 * np.pi * k * t / period))
    X_season = np.column_stack(X_season_list)

    # Full matrix to fit against (Intercept, Trend, Sine 1, Cosine 1, etc.)
    X = np.column_stack((X_trend, X_season))

    # Minimum points needed to solve the equation (2 for trend + 2*K for harmonics)
    min_valid_points = 2 + (2 * num_harmonics)

    def _harmonic(ts):
        out = np.full((3, len(ts)), np.nan)
        valid = np.isfinite(ts)

        if valid.sum() < min_valid_points:
            return out

        # Fit the model using numpy's least-squares solver on VALID data only
        # This completely removes the need for gap-filling via np.interp!
        coeffs, _, _, _ = np.linalg.lstsq(X[valid], ts[valid], rcond=None)

        # Reconstruct the curves for the ENTIRE time series (even across gaps)
        out[0] = np.dot(X_trend, coeffs[0:2])  # Trend component
        out[1] = np.dot(X_season, coeffs[2:])  # Seasonal component
        out[2] = ts - (out[0] + out[1])  # Residual (preserves original NaNs)

        return out  # shape (3, time)

    # Apply across spatial dimensions
    result = xr.apply_ufunc(
        _harmonic, da,
        input_core_dims=[["time"]],
        output_core_dims=[["component", "time"]],
        vectorize=True,
        output_dtypes=[float],
    ).transpose("component", "time", "latitude", "longitude")

    return xr.Dataset({
        "trend": result[0],
        "seasonal": result[1],
        "residual": result[2],
    })