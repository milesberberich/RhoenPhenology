from landcover_loader import *
from modis_loader import *
from lc_filter import *
from dea_tools.temporal import xr_phenology
from tqdm.auto import tqdm

def phen_loop(start_year, end_year, output_filepath, index = "NDVI", class_codes = [60, 70, 90], Save = True, dynamik_landcover = "False"):

    years = list(range(start_year, end_year+1))

    # Info what will happen
    print(f"phenology will be calculated on the basis of {index} for the years from {start_year} to {end_year - 1}.")

    # print statement for usability
    legend_dict = get_lc_legend()
    class_values = [legend_dict[code] for code in class_codes]
    print(f"The landcover classes {class_values} will be used")
    if dynamik_landcover == "True":
        print("Dynamic landcover will be used.")
    if dynamik_landcover == "False":
        print("Static landcover data from 2022 will be used.")
        lc = landcover_loader(
            r"C:\Users\miles\OneDrive\Dokumente\EAGLE SoSe\Linking science\gis\geodata\bioreservat_rhön.geojson",
            datetime="2020-01-01/2020-12-30",
            as_single_layer=True)


    # acutal loop
    for y in tqdm(years, desc=f"Processing {index}"):
        # loading modis
        dc_raw = modis_loader(
            r"C:\Users\miles\OneDrive\Dokumente\EAGLE SoSe\Linking science\gis\geodata\bioreservat_rhön.geojson",
            index=index, datetime=f"{y}-01-01/{y}-12-30")

        # loading landcover

        # dynamik and capped LC
        if dynamik_landcover == "True":
            y_capped = y
            if y > 2020:
                y_capped = 2020
                print(f"LC-DATA FROM 2020 was used for the year {y}")

            lc = landcover_loader(
                r"C:\Users\miles\OneDrive\Dokumente\EAGLE SoSe\Linking science\gis\geodata\bioreservat_rhön.geojson", datetime=f"{y_capped}-01-01/{y_capped}-12-30",
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
                f"{output_filepath}/phenology_{index}_{y}.tif")

    tqdm.write(f"Saved {y} - {index}!")



