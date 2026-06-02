import pystac_client
import xarray as xr
import geopandas as gpd
import pystac_client
import planetary_computer
import odc.stac
import geopandas as gpd
import rioxarray

########################
### modis_loader16() ###
########################

def modis_loader16(aoi_path, index="NDVI", datetime="2025-01-01/2025-06-30", clip_to_exact_aoi_outlines = True):
    """Loads MODIS data to an xarray dataset using Microsoft Planetary Computer"""

    # 1. Load aoi
    aoi = gpd.read_file(aoi_path).to_crs("EPSG:4326")

    # 2. Connect to Planetary Computer (with automatic token signing)
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    # 3. Search the catalog
    print("Searching MODIS catalog for 16 day resolution")
    search = catalog.search(
        collections=["modis-13Q1-061"],
        bbox=tuple(aoi.total_bounds),
        datetime=datetime
    )
    items = search.item_collection()

    # 4. Create the data cube targeting the GeoTIFF band explicitly
    cube = odc.stac.load(
        items,
        bands=[f"250m_16_days_{index}", "250m_16_days_VI_Quality"],  # FIXED: changed 'assets' to 'bands'
        bbox=tuple(aoi.total_bounds),
        crs="EPSG:4326",
        resolution=0.00225
    )

    # 5. NAN-handling, scaling and masking
    qa_layer = cube["250m_16_days_VI_Quality"]
    ndvicube = cube[f"250m_16_days_{index}"].where(cube[f"250m_16_days_{index}"] != -3000) * 0.0001

    summary_mask = (qa_layer & 3) == 0
    adjacent_cloud_mask = (qa_layer & (1 << 8)) == 0
    mixed_cloud_mask = (qa_layer & (1 << 10)) == 0
    strict_mask = summary_mask & adjacent_cloud_mask & mixed_cloud_mask
    ndvicube = ndvicube.where(strict_mask)

    if clip_to_exact_aoi_outlines == True:
        ndvicube = ndvicube.rio.clip(aoi.geometry, aoi.crs, drop=True)


    print(f"Found {len(items)} items ({ndvicube.nbytes / (1024 ** 2):.2F} MB")

    return ndvicube

######################
### modis_loader8() ###
######################

def modis_loader16(aoi_path, index="NDVI", datetime="2025-01-01/2025-06-30", clip_to_exact_aoi_outlines = True):
    """Loads MODIS data to an xarray dataset using Microsoft Planetary Computer"""

    # 1. Load aoi
    aoi = gpd.read_file(aoi_path).to_crs("EPSG:4326")

    # 2. Connect to Planetary Computer (with automatic token signing)
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    # 3. Search the catalog
    print("Searching MODIS catalog for 8 day resolution")
    search = catalog.search(
        collections=["modis-09Q1-061"],
        bbox=tuple(aoi.total_bounds),
        datetime=datetime
    )
    items = search.item_collection()

    # 4. Create the data cube targeting the GeoTIFF band explicitly
    cube = odc.stac.load(
        items,
        bands=["sur_refl_b01", "sur_refl_b02", "sur_refl_qc_250m"],  # FIXED: changed 'assets' to 'bands'
        bbox=tuple(aoi.total_bounds),
        crs="EPSG:4326",
        resolution=0.00225
    )

    # 5. NAN-handling, scaling and masking
    qa_layer = cube["250m_16_days_VI_Quality"]
    ndvicube = cube[f"250m_16_days_{index}"].where(cube[f"250m_16_days_{index}"] != -3000) * 0.0001

    summary_mask = (qa_layer & 3) == 0
    adjacent_cloud_mask = (qa_layer & (1 << 8)) == 0
    mixed_cloud_mask = (qa_layer & (1 << 10)) == 0
    strict_mask = summary_mask & adjacent_cloud_mask & mixed_cloud_mask
    ndvicube = ndvicube.where(strict_mask)

    if clip_to_exact_aoi_outlines == True:
        ndvicube = ndvicube.rio.clip(aoi.geometry, aoi.crs, drop=True)


    print(f"Found {len(items)} items ({ndvicube.nbytes / (1024 ** 2):.2F} MB")

    return ndvicube