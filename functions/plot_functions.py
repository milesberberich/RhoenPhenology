import glob
import pandas as pd
import rioxarray
import joypy
import matplotlib.pyplot as plt

###################
### ridgeplot() ###
###################

def ridgeplot(data_path, index="NDVI", metric="SOS", band=1):

    files = sorted(glob.glob(f"{glob.escape(data_path)}/phenology_{index}_*.tif"))
    df_list = []

    for f in files:
        year = f.split('_')[-1].replace('.tif', '')  # Pull year from filename
        vals = rioxarray.open_rasterio(f).sel(band=band).values.flatten()
        vals = vals[(vals > 0) & (vals <= 366)]  # Filter valid DOY pixels
        df_list.append(pd.DataFrame({metric: vals, "Year": year}))


    df = pd.concat(df_list, ignore_index=True)

    joypy.joyplot(df, by="Year", column=metric, colormap=plt.cm.viridis, title=f"{metric} based on {index}")
    plt.show()


###################
### timeplot() ###
###################

def timeplot(datacube, title = "Mean VI Time Series"):

    timeseries = datacube.mean(dim= ["latitude", "longitude"])
    plt.figure(figsize=(10, 5))
    timeseries.plot(marker='o', linestyle='-', color='green')
    plt.title(title)
    plt.ylabel("Mean VI")
    plt.xlabel("Date")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

###################
### xarray_scatterplot() ###
###################


import xarray as xr
import numpy as np

def xarray_scatterplot(ds1, ds2, band1, band2):
    """
    Safely interpolates ds2 to match ds1's resolution, handles mismatched
    dimension names, drops NaNs, and plots band1 vs band2.
    """
    # 1. Smart extraction & Squeeze
    da1 = (ds1[band1] if isinstance(ds1, xr.Dataset) else ds1.sel(band=band1)).squeeze()
    da2 = (ds2[band2] if isinstance(ds2, xr.Dataset) else ds2.sel(band=band2)).squeeze()

    # 2. Fix Dimension Mismatches
    if set(da1.dims) != set(da2.dims):
        da2 = da2.rename({da2.dims[-2]: da1.dims[-2], da2.dims[-1]: da1.dims[-1]})

    # 3. Aligning rasters safely
    da2_aligned = da2.interp_like(da1)

    # 4. broadcasting
    da1, da2_aligned = xr.broadcast(da1, da2_aligned)

    # 5. Flatten arrays
    x = da1.values.flatten()
    y = da2_aligned.values.flatten()

    # 6. omit NAs
    valid_mask = np.isfinite(x) & np.isfinite(y)
    x_valid = x[valid_mask]
    y_valid = y[valid_mask]

    # 7. Only using few points
    if len(x_valid) > 5000:
        print("Plot will only use 5000 points")
        indices = np.random.choice(len(x_valid), 5000, replace=False)
        x_plot = x_valid[indices]
        y_plot = y_valid[indices]
    else:
        x_plot = x_valid
        y_plot = y_valid

    # Create scatterplot
    plt.figure(figsize=(6, 6))
    plt.scatter(x_plot, y_plot, alpha=0.3, s=2)
    plt.xlabel(band1)
    plt.ylabel(band2)
    plt.title(f"Scatterplot: {band1} vs {band2}")
    plt.grid(True)
    plt.show()

#######################
# xarray_ridgeplot() #
######################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joypy

# Preserved pandas/matplotlib compatibility patch
import pandas.plotting._matplotlib.tools as _tools

_tools.flatten_axes = lambda axes: list(_tools.flatten_axes.__wrapped__(axes)) \
    if hasattr(_tools.flatten_axes, "__wrapped__") \
    else (lambda f: lambda a: list(f(a)))(_tools.flatten_axes)


def xarray_ridgeplot(da, bands=None, title=None, valid_range=(1, 366)):
    """
    Simplified Yearwise ridge (joy) plot from an xarray DataArray.
    """
    has_band_dim = "band" in da.dims
    if not has_band_dim:
        band_list = [None]
    elif bands is None:
        band_list = da.band.values.tolist()
    elif isinstance(bands, str):
        band_list = [bands]
    else:
        band_list = list(bands)

    lo, hi = valid_range
    frames = []

    for t in da.time.values:
        year_str = str(pd.Timestamp(t).year)
        data_dict = {"Year": year_str}

        for b in band_list:
            da_b = da.sel(band=b) if b is not None else da
            vals = da_b.sel(time=t).values.flatten().astype(float)

            # Filter valid range and drop NaNs
            vals = vals[(vals > lo) & (vals <= hi) & ~np.isnan(vals)]

            col_name = b if b is not None else "value"
            data_dict[col_name] = pd.Series(vals)

        frames.append(pd.DataFrame(data_dict))

    df = pd.concat(frames, ignore_index=True)
    year_order = sorted(df["Year"].dropna().unique())
    cols_to_plot = band_list if has_band_dim else ["value"]

    figsize = (10, max(4, len(year_order)*1.533))

    band_colors = ['#2ca02c', '#d62728', '#1f77b4', '#ff7f0e', '#9467bd']

    if title is None:
        title = "Ridge plot" if not has_band_dim else f"Ridge plot – {', '.join(str(b) for b in band_list)}"

    if len(cols_to_plot) > 1:
        plot_color = band_colors[:len(cols_to_plot)]
        plot_cmap = None
        show_legend = True
    else:
        plot_color = None
        plot_cmap = plt.cm.viridis  # Gradient across the years for a single band
        show_legend = False

    fig, axes = joypy.joyplot(
        df,
        by="Year",
        column=cols_to_plot,
        labels=year_order,
        figsize=figsize,
        linewidth=1.0,
        alpha=0.85,
        overlap=2,
        bw_method=0.28,
        legend=show_legend,
        title=title,
        color=plot_color,
        colormap=plot_cmap
    )

    plt.tight_layout()
    plt.show()