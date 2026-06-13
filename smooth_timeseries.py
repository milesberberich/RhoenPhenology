from dea_tools import *
import numpy as np
import pandas as pd
import xarray as xr
import datetime as dt
import matplotlib.pyplot as plt
import xrscipy.signal


def smooth_timeseries(dc, filter = "savgol", window_size=4):

    if filter == "moving_window":

        dc_filled = dc.interpolate_na(dim="time", method="linear")
        dc_smooth = dc_filled.rolling(time=window_size, center=True, min_periods=1).mean()
        dc_smooth = dc_smooth.bfill(dim="time").ffill(dim="time")

    if filter == "savgol":

        dc["time"] = pd.to_datetime(dc["time"].values)
        val = dc.time.values[0]
        print(type(val))
        dc_smooth = xrscipy.signal.savgol_filter(
            dc,
            window_length=60,
            polyorder=2,
            dim="time",
            mode="interp")

    return dc_smooth