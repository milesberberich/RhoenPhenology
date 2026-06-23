import numpy as np
import xarray as xr
from scipy.optimize import curve_fit
from scipy.optimize import OptimizeWarning
import warnings


def ads(t, p, a, b, c, d, e, SOS, EOS):
    """Asymmetric Double Sigmoid (Hmimina et al. 2013, Eq. 2)."""
    return (
            p * t + (a + c)
            + 0.5 * (a - c) * np.tanh(b * (t - SOS))
            - 0.5 * (a - e) * np.tanh(d * (t - EOS))
    )


def fit_ads_pixel(ndvi: np.ndarray, t: np.ndarray) -> dict:
    """
    Fit ADS to a single pixel time series.
    Returns dict with SOS, EOS, LOS, and ADS shape parameters.
    """
    keys = ("SOS", "EOS", "LOS", "p", "a", "b", "c", "d", "e")
    NAN = {k: np.nan for k in keys}

    # masking NAs and pixels out of boundary
    mask = np.isfinite(ndvi)
    if mask.sum() < 10:
        return NAN
    y, x = ndvi[mask], t[mask]

    amp = y.max() - y.min()

    # Rise (spring) and Decrease (fall)
    mid_year = np.median(x)
    spring_mask = x < mid_year
    autumn_mask = x >= mid_year

    # Seed SOS at the highest NDVI rise, EOS at the fastest fall
    sos0 = x[spring_mask][np.argmax(np.gradient(y[spring_mask]))] if spring_mask.sum() > 2 else 100
    eos0 = x[autumn_mask][np.argmin(np.gradient(y[autumn_mask]))] if autumn_mask.sum() > 2 else 260

    p0 = [0, y.mean(), 0.1, amp / 2, 0.1, amp / 2, sos0, eos0]

    # Expanded bounds for SOS and EOS to encompass the full year (0 to 366)
    bounds = (
        [-0.01, -1, 0.001, -1, 0.001, -1, 0, 0],
        [0.01, 2, 1, 1, 1, 1, 366, 366],
    )

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", (OptimizeWarning, RuntimeWarning))
            popt, _ = curve_fit(ads, x, y, p0=p0, bounds=bounds, maxfev=5000)

        p, a, b, c, d, e, SOS, EOS = popt
        LOS = EOS - SOS

        return dict(SOS=SOS, EOS=EOS, LOS=LOS, p=p, a=a, b=b, c=c, d=d, e=e)

    except RuntimeError:
        return NAN


def get_phenology(dc: xr.DataArray) -> xr.Dataset:
    """
    Fit ADS pixelwise to a (time, latitude, longitude) xarray DataArray.
    Returns xr.Dataset with SOS, EOS, LOS (day-of-year/duration) and all ADS parameters.
    """
    t = dc.time.dt.dayofyear.values.astype(float)
    ndvi = dc.values  # (time, lat, lon)
    n_time, n_lat, n_lon = ndvi.shape

    keys = ("SOS", "EOS", "LOS", "p", "a", "b", "c", "d", "e")
    results = {k: np.full((n_lat, n_lon), np.nan) for k in keys}

    for i in range(n_lat):
        for j in range(n_lon):
            fit = fit_ads_pixel(ndvi[:, i, j], t)
            for k in keys:
                results[k][i, j] = fit[k]

    coords = {"latitude": dc.latitude, "longitude": dc.longitude}
    return xr.Dataset({k: xr.DataArray(v, coords=coords) for k, v in results.items()})