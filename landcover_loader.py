import pystac_client
import xarray as xr
import geopandas as gpd
import pystac_client
import planetary_computer
import odc.stac

def landcover_loader(aoi_path, datetime="2025-01-01/2025-06-30"):
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

    # 5. NAN-handling, scaling and masking
    qa_layer = cube["250m_16_days_VI_Quality"]
    ndvicube = cube[f"250m_16_days_{index}"].where(cube[f"250m_16_days_{index}"] != -3000) * 0.0001
    mask = (qa_layer & 3) <= 1
    ndvicube = ndvicube.where(mask)

    print(f"Found {len(items)} items ({ndvicube.nbytes / (1024 ** 2):.2F} MB")

    return ndvicube