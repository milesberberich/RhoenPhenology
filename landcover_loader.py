import geopandas as gpd
import pystac_client
import planetary_computer
import odc.stac
import rioxarray


################################
####### landcover_loader()#####
################################

def landcover_loader(aoi_path, datetime="2020-01-01/2020-12-30", as_single_layer = False, clip_to_exact_aoi_outlines = True):
    """Loads ESA-CCI-LC data to an xarray dataset using Microsoft Planetary Computer"""

    # 1. Load aoi
    aoi = gpd.read_file(aoi_path).to_crs("EPSG:4326")

    # 2. Connect to Planetary Computer
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace)

    # 3. Search the catalog
    print("Searching LC catalog")
    search = catalog.search(
        collections=["esa-cci-lc"],
        bbox=tuple(aoi.total_bounds),
        datetime=datetime
    )
    items = search.item_collection()

    # 4. Create the data cube targeting the GeoTIFF band explicitly
    cube = odc.stac.load(
        items,
        bands=["lccs_class"],  # FIXED: changed 'assets' to 'bands'
        bbox=tuple(aoi.total_bounds),
        crs="EPSG:4326",
        resolution=0.00225
    )
    cube = cube.squeeze("time")
    # option to get only one layer back
    if as_single_layer == True:
        cube = cube["lccs_class"]
    # option to instantly clip to exact aoi, not only bounding box
    if clip_to_exact_aoi_outlines == True:
        cube = cube.rio.clip(aoi.geometry, aoi.crs, drop=True)

    print("landcover loaded")

    return cube

################################
####### get_lc_legend() ########
################################

def get_lc_legend():
    cci_legend = {0: "No Data", 10: "Cropland, rainfed", 11: "Herbaceous cover",
                  30: "Mosaic cropland (>50%) / natural vegetation (tree, shrub, herbaceous cover) (<50%)",
                  40: "Mosaic natural vegetation (tree, shrub, herbaceous cover) (>50%) / cropland (<50%)",
                  60: "Tree cover, broadleaved, deciduous, closed to open (>15%)",
                  61: "Tree cover, broadleaved, deciduous, closed (>40%)",
                  70: "Tree cover, needleleaved, evergreen, closed to open (>15%)",
                  90: "Tree cover, mixed leaf type (broadleaved and needleleaved)",
                  100: "Mosaic tree and shrub (>50%) / herbaceous cover (<50%)",
                  110: "Mosaic herbaceous cover (>50%) / tree and shrub (<50%)", 130: "Grassland",
                  180: "Shrub or herbaceous cover, flooded, fresh/saline/brakish water", 190: "Urban areas"}
    return cci_legend