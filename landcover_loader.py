import geopandas as gpd
import pystac_client
import planetary_computer
import odc.stac

def landcover_loader(aoi_path, datetime="2020-01-01/2020-12-30"):
    """Loads ESA-CCI-LC data to an xarray dataset using Microsoft Planetary Computer"""

    # 1. Load aoi
    aoi = gpd.read_file(aoi_path).to_crs("EPSG:4326")

    # 2. Connect to Planetary Computer
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace)

    # 3. Search the catalog
    print("Searching catalog")
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
    return cube