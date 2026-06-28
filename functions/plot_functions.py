import glob
import pandas as pd
import rioxarray
import joypy
import matplotlib.pyplot as plt

###################
### ridgeplot() ###
###################

def ridgeplot(data_path, metric="SOS", band=1):

    files = sorted(glob.glob(f"{data_path}/phenology_*_*.tif"))
    df_list = []

    for f in files:
        year = f.split('_')[-1].replace('.tif', '')  # Pull year from filename
        vals = rioxarray.open_rasterio(f).sel(band=band).values.flatten()
        vals = vals[(vals > 0) & (vals <= 366)]  # Filter valid DOY pixels
        df_list.append(pd.DataFrame({metric: vals, "Year": year}))


    df = pd.concat(df_list, ignore_index=True)

    joypy.joyplot(df, by="Year", column=metric, colormap=plt.cm.viridis, title=f"{metric} Over Time")
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
