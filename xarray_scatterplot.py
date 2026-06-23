import matplotlib.pyplot as plt


def plot_xarray_scatter(ds1, ds2, band1, band2):
    """
    Interpolates ds2 to match ds1's resolution, then plots band1 vs band2.
    """
    # Aligning rasters
    ds2_aligned = ds2.interp_like(ds1)

    # extracting bands and flattening
    x = ds1[band1].values.flatten()
    y = ds2_aligned[band2].values.flatten()

    # Create the scatterplot
    plt.figure(figsize=(6, 6))
    plt.scatter(x, y, alpha=0.3, s=2)  # low alpha/size helps if datasets are large
    plt.xlabel(band1)
    plt.ylabel(band2)
    plt.title(f"Scatterplot: {band1} vs {band2}")
    plt.grid(True)
    plt.show()