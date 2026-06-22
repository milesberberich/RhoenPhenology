import xarray as xr
import numpy as np


def get_phenology(dc):
    """Calculate SOS, EOS, and MAX_NDVI using a 50% amplitude threshold."""

    ndvi_min = dc.min(dim="time", skipna=True)
    ndvi_max = dc.max(dim="time", skipna=True)
    threshold = ndvi_min + 0.5 * (ndvi_max - ndvi_min)

    # Find the indices for the peak and the trough
    peak_idx = dc.fillna(-9999).argmax(dim="time")

    # NEW: Find the index of the absolute minimum NDVI (the bottom of the winter dip)
    min_idx = dc.fillna(9999).argmin(dim="time")

    time_idx = xr.DataArray(np.arange(len(dc.time)), dims="time")

    above = dc > threshold

    # NEW: SOS must be above threshold, BEFORE the peak, but AFTER the winter minimum
    spring = above & (time_idx >= min_idx) & (time_idx <= peak_idx)

    valid = spring.any(dim="time")
    sos_idx = spring.astype(float).argmax(dim="time")
    sos_doy = dc.time.dt.dayofyear.isel(time=sos_idx).where(valid)

    # EOS: last timestep above threshold after the peak
    fall = above & (time_idx > peak_idx)
    valid = fall.any(dim="time")
    eos_idx_rev = fall.astype(float).isel(time=slice(None, None, -1)).argmax(dim="time")
    eos_idx = (len(dc.time) - 1) - eos_idx_rev
    eos_doy = dc.time.dt.dayofyear.isel(time=eos_idx).where(valid)

    # LOS
    los_doy = eos_doy - sos_doy

    return xr.Dataset({
        "SOS": sos_doy.drop_vars("time", errors="ignore"),
        "EOS": eos_doy.drop_vars("time", errors="ignore"),
        "LOS": los_doy.drop_vars("time", errors="ignore"),
        "MAX_NDVI": ndvi_max.drop_vars("time", errors="ignore"),
    })
