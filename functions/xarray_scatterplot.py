import matplotlib.pyplot as plt
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