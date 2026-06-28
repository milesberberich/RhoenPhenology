import numpy as np
import xarray as xr
from scipy.signal import savgol_filter




def smooth_timeseries(dc, window_size=5):
    """Smoothing a Vegetation-Index datacube with a Savitzky-Golay filter.
    Landcovered-masked pixels are preserved.
    """
    # Linear interpolation fills gaps, then pad edges
    dc_filled = dc.interpolate_na(dim="time", method="linear").bfill(dim="time").ffill(dim="time")

    def _savgol(arr):
        if np.all(np.isnan(arr)):
            return arr
        return savgol_filter(arr, window_length=window_size, polyorder=2, mode="interp")

    dc_smooth = xr.apply_ufunc(
        _savgol,
        dc_filled,
        input_core_dims=[["time"]],
        output_core_dims=[["time"]],
        vectorize=True,   # calls _savgol per pixel, so NaN check works
        keep_attrs=True,
    )

    dc_smooth = dc_smooth.where(dc.count(dim="time") > 0)

    return dc_smooth