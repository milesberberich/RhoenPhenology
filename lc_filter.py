
import xarray as xr
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