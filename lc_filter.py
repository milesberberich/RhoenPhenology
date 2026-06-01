
import xarray as xr
import rioxarray
from rasterio.enums import Resampling

def lc_filter(modis_cube, landcover_cube, class_codes):
    """Filters modis data for specific landcoverclasses loaded with the landcover_loader"""

    landcover_cube = landcover_cube.rio.reproject_match(modis_cube, resampling=Resampling.nearest)
    mask = landcover_cube.isin(class_codes).values
    mak = xr.DataArray(mask, dims = ["x", "y"])

    modis_cube = modis_cube.where(mask)

    print("datacube clipped")

    return modis_cube