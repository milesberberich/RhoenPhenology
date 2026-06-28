import xarray as xr
import numpy as np
from scipy import stats

def mk_test(decomposition):
    def pixel_test(ts):
        slope, _, _, p_value, _ = stats.linregress(np.arange(len(ts)), ts)
        return slope if p_value < 0.05 else np.nan

    trend_slope = xr.apply_ufunc(
        pixel_test,
        decomposition["trend"],
        input_core_dims=[["time"]],
        vectorize=True,
        output_dtypes=[float],
    )

    increasing = trend_slope.where(trend_slope > 0)
    decreasing = trend_slope.where(trend_slope < 0)

    return trend_slope, increasing, decreasing