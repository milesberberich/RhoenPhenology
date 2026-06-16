import xarray as xr
import numpy as np


def get_phenology(dc):
    """Calculate SOS, EOS, and MAX_NDVI using a 50% amplitude threshold."""

    ndvi_min = dc.min(dim="time", skipna=True)
    ndvi_max = dc.max(dim="time", skipna=True)
    threshold = ndvi_min + 0.5 * (ndvi_max - ndvi_min)

    peak_idx = dc.fillna(-9999).argmax(dim="time")
    time_idx = xr.DataArray(np.arange(len(dc.time)), dims="time")

    above = dc > threshold

    # SOS: first timestep above threshold before (and including) the peak
    spring = above & (time_idx <= peak_idx)
    sos_idx = spring.astype(float).argmax(dim="time")
    sos_doy = dc.time.dt.dayofyear.isel(time=sos_idx)

    # EOS: last timestep above threshold after the peak
    # hier weirder trick mit time auf reverse um dann "erste" statt letzten zu finden
    fall = above & (time_idx > peak_idx)
    eos_idx_rev = fall.astype(float).isel(time=slice(None, None, -1)).argmax(dim="time")
    eos_idx = (len(dc.time) - 1) - eos_idx_rev
    eos_doy = dc.time.dt.dayofyear.isel(time=eos_idx)

    # LOS
    los_doy = eos_doy - sos_doy

    return xr.Dataset({"SOS": sos_doy, "EOS": eos_doy, "LOS": los_doy, "MAX_NDVI": ndvi_max})

