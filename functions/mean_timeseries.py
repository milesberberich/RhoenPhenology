import glob
import rasterio
import numpy as np


def mean_timeseries(folder_path, bands=[1, 2, 3]):
    """
    Calculates the spatial mean for a specific list of 3 bands across a folder of TIFFs.
    Returns 3 separate 1D numpy arrays.
    """
    tiff_files = sorted(glob.glob(f"{glob.escape(folder_path)}/*.tif"))

    # Setup lists for the 3 time series
    series1, series2, series3 = [], [], []

    for file in tiff_files:
        with rasterio.open(file) as src:
            # Pass the list of bands to read them all at once into a 3D array
            data = src.read(bands).astype(float)

            # Mask out NoData
            if src.nodata is not None:
                data[data == src.nodata] = np.nan

            # Calculate the spatial mean for each of the 3 bands (axes 1 and 2 are rows/cols)
            means = np.nanmean(data, axis=(1, 2))

            # Append the means to their respective lists
            series1.append(means[0])
            series2.append(means[1])
            series3.append(means[2])

    # Convert lists to numpy arrays before returning
    return np.array(series1), np.array(series2), np.array(series3)