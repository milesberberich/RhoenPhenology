import xarray as xr
import numpy as np


def get_phenology(year_dc):
    """Calculates SOS and EOS for a single year of data."""

    # 1. defining threshold
    ndvi_min = year_dc.min(dim='time')
    ndvi_max = year_dc.max(dim='time')
    amplitude = ndvi_max - ndvi_min
    threshold = ndvi_min + (0.5 * amplitude)

    # find yearly max
    peak_time = year_dc.idxmax(dim='time')

    # Splitting year in spring and autumn
    is_spring = year_dc['time'] <= peak_time
    is_autumn = year_dc['time'] > peak_time

    # 4. SOS: first day abouve threshold
    spring_pixels = year_dc.where(is_spring & (year_dc > threshold))
    sos_date = spring_pixels.idxmax(dim='time')  # Date of crossing
    sos_doy = sos_date.dt.dayofyear

    # EOS, last day above threshold
    autumn_pixels = year_dc.where(is_autumn & (year_dc > threshold))
    eos_date = autumn_pixels.idxmax(dim='time')
    eos_doy = eos_date.dt.dayofyear

    # Combine into a new Dataset
    return xr.Dataset({
        'SOS': sos_doy,
        'EOS': eos_doy,
        'MAX_NDVI': ndvi_max
    })

