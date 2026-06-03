from dea_tools import *
import numpy as np
import pandas as pd
import xarray as xr
import datetime as dt
import matplotlib.pyplot as plt


def smooth_timeseries(dc, window_size=4):

    dc_filled = dc.interpolate_na(dim="time", method="linear")
    dc_smooth = dc_filled.rolling(time=window_size, center=True, min_periods=1).mean()
    dc_smooth = dc_smooth.bfill(dim="time").ffill(dim="time")

    return dc_smooth