from landcover_loader import *
from modis_loader import *
from lc_filter import *
import rioxarray
from dea_tools.temporal import xr_phenology
from tqdm.auto import tqdm

def phen_loop(start_year, end_year, output_filepath, index = "NDVI", class_codes = [60, 90], Save = True):

    years = list(range(start_year, end_year+1))

    for y in tqdm(years, desc=f"Processing {index}"):


        # loading modis
        dc_raw = modis_loader(
            r"C:\Users\miles\OneDrive\Dokumente\EAGLE SoSe\Linking science\gis\geodata\bioreservat_rhön.geojson",
            index=index, datetime=f"{y}-01-01/{y}-12-30")

        # loading landcover
        lc = landcover_loader(
            r"C:\Users\miles\OneDrive\Dokumente\EAGLE SoSe\Linking science\gis\geodata\bioreservat_rhön.geojson",
            as_single_layer=True)

        # filtering modis using landcover
        dc = lc_filter(dc_raw, lc, class_codes=class_codes)

        # calulating phenology
        phenology = xr_phenology(dc, stats=['SOS', 'POS', 'EOS', 'Trough', 'vSOS', 'vPOS', 'vEOS', 'LOS', 'AOS', 'ROG', 'ROS'])

        # filter results
        phenology = lc_filter(phenology, lc, class_codes=class_codes)

        # saving results
        if Save == True:

            multiband_array = phenology.to_array(dim="band")
            band_names = multiband_array.band.values.tolist()
            multiband_array.attrs["long_name"] = band_names
            multiband_array.rio.to_raster(
                f"{output_filepath}/phenology_{index}_{y}.tif.tif")

    tqdm.write(f"Saved {y} - {index}!")


