from modis_loader import *
from landcover_loader import *
from lc_filter import *
from smooth_timeseries import *


def multiannual_timeseries(aoi_path, start_year = 2000, end_year = 2025, landcover_code = [60]):
    '''This function gives you a multiyear timeseries data cube for a desired landcover, using the 16day NDVI MODIS data.'''

    dc_raw = modis_loader16(
        r"C:\Users\miles\OneDrive\Dokumente\EAGLE SoSe\Linking science\gis\geodata\bioreservat_rhön.geojson",
        datetime=f"{start_year}-01-01/{end_year}-12-30")#.sel(time=year).transpose('time', 'latitude', 'longitude')

    lc_year = round((start_year + end_year) / 2)
    lc = landcover_loader(
        r"C:\Users\miles\OneDrive\Dokumente\EAGLE SoSe\Linking science\gis\geodata\bioreservat_rhön.geojson",
        as_single_layer=True, datetime=f"{lc_year}-01-01/{lc_year}-12-30")

    dc = lc_filter(dc_raw, lc, class_codes=landcover_code)

    dc = smooth_timeseries(dc, window_size=5)

    return dc