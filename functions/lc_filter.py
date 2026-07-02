
import xarray as xr
import numpy as np
import rioxarray
from rasterio.enums import Resampling

def lc_filter(modis_cube, landcover_cube, class_codes):
    landcover_cube = landcover_cube.rio.reproject_match(modis_cube, resampling=Resampling.nearest)
    mask = landcover_cube.isin(class_codes)

    spatial_dims = [d for d in modis_cube.dims if d != "time"]
    mask = mask.rename(dict(zip(mask.dims, spatial_dims)))

    modis_cube = modis_cube.where(mask)
    print("datacube clipped")
    return modis_cube

####################################################################################################################

def lc_filter_dwd(modis_cube, landcover_cube, class_codes):


    matched_lc = landcover_cube.rio.reproject_match(modis_cube, resampling=Resampling.nearest)

    if "band" in matched_lc.dims:
        matched_lc = matched_lc.squeeze("band", drop=True)

    mask = matched_lc.isin(class_codes)

    filtered_cube = modis_cube.where(mask)
    print("datacube clipped")
    return filtered_cube