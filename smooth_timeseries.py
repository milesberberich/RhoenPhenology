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
        # window_size = number of time steps (not days)
        # must be odd
        dc_smooth = dc.copy()
        dc_smooth = dc_smooth.bfill(dim="time").ffill(dim="time")
        window = window_size if window_size % 2 != 0 else window_size + 1

        dc_smooth = xr.apply_ufunc(
            savgol_filter,
            dc_smooth,
            kwargs={
                "window_length": window,
                "polyorder": 2,
                "axis": -1,  # apply along last axis (time)
                "mode": "interp"
            },
            input_core_dims=[["time"]],
            output_core_dims=[["time"]],
            vectorize=False,
            keep_attrs=True,
        )

    return dc_smooth

    return dc_smooth