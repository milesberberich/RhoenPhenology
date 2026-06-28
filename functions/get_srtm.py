import geopandas as gpd
import pystac_client
import planetary_computer
import odc.stac


def get_srtm(aoi_path):

    # 1. Load and reproject AOI
    aoi = gpd.read_file(aoi_path).to_crs("EPSG:4326")

    # 2. Open Catalog
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    print("Searching catalog...")

    # 3. Perform the search (using only the optimized parameters)
    search = catalog.search(
        collections=["nasadem"],
        bbox=tuple(aoi.total_bounds),
        datetime="2000-02-01/2000-02-28",
        method="GET"
    )

    # Fetch the items
    items = search.item_collection()
    print(f"Found {len(items)} items.")

    # 4. Create the data cube
    cube = odc.stac.load(
        items,
        bands=["elevation"],
        bbox=tuple(aoi.total_bounds),
        crs="EPSG:4326",
        resolution=0.00027
    )

    return cube