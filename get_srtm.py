import geopandas as gpd
import pystac_client
import planetary_computer
import odc.stac

def get_srtm(aoi_path):

    aoi = gpd.read_file(aoi_path).to_crs("EPSG:4326")

    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )
    print("Searching catalog")
    search = catalog.search(
        collections=["nasadem"],
        bbox=tuple(aoi.total_bounds))

    items = search.item_collection()

    # 4. Create the data cube targeting the GeoTIFF band explicitly
    cube = odc.stac.load(
        items,
        bbox=tuple(aoi.total_bounds),
        crs="EPSG:4326",
        resolution=0.00225
    )