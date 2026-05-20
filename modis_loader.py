import pystac_client
import xarray as xr
import geopandas as gpd
import pystac_client
import planetary_computer
import odc.stac
import stackstac

def modis_loader(aoi_path, index="NDVI", datetime="2025-01-01/2025-06-30"):
    """Loads MODIS data to an xarray dataset using Microsoft Planetary Computer"""

    # 1. Load aoi
    aoi = gpd.read_file(aoi_path).to_crs("EPSG:4326")

    # 2. Connect to Planetary Computer (with automatic token signing)
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    # 3. Search the catalog
    print("Searching catalog")
    search = catalog.search(
        collections=["modis-13Q1-061"],
        bbox=tuple(aoi.total_bounds),
        datetime=datetime
    )
    items = search.item_collection()
    print(f"Found {len(items)} items.")

    # 4. Create the data cube targeting the GeoTIFF band explicitly
    cube = odc.stac.load(
        items,
        bands=[f"250m_16_days_{index}"],  # FIXED: changed 'assets' to 'bands'
        bbox=tuple(aoi.total_bounds),
        crs="EPSG:4326",
        resolution=0.00225
    )

    return cube