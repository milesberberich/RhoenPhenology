import numpy as np
import xarray as xr
from statsmodels.tsa.seasonal import STL


def stl_decompose(da: xr.DataArray, period: int=23, seasonal: int=45, trend: int=101) -> xr.Dataset:
    """
    Pixel-wise STL decomposition on a (time, latitude, longitude) DataArray.
    Returns an xr.Dataset with trend, seasonal, and residual.
    """

    def _stl(ts):
        out = np.full((3, len(ts)), np.nan)
        valid = np.isfinite(ts)
        if valid.sum() < 2 * period:
            return out
        idx = np.arange(len(ts))
        ts = np.interp(idx, idx[valid], ts[valid])  # fill gaps
        res = STL(ts, period=period, seasonal=seasonal, trend=trend, robust=True).fit()
        out[0], out[1], out[2] = res.trend, res.seasonal, res.resid
        return out  # shape (3, time)

    result = xr.apply_ufunc(
        _stl, da,
        input_core_dims=[["time"]],
        output_core_dims=[["component", "time"]],
        vectorize=True,
        output_dtypes=[float],
    ).transpose("component", "time", "latitude", "longitude")

    return xr.Dataset({
        "trend":    result[0],
        "seasonal": result[1],
        "residual": result[2],
    })