
import pystac_client
import planetary_computer
import odc.stac
import geopandas as gpd

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
        resolution=0.00225,
        fail_on_error=False,
    )

    # 5. NAN-handling, scaling and masking
    qa_layer = cube["250m_16_days_VI_Quality"]
    #ndvicube = cube.where((cube >= -2000) & (cube <= 10000)) * 0.0001 # only valid from -2000 to 10.000

    ndvicube = cube[f"250m_16_days_{index}"].where(cube[f"250m_16_days_{index}"] != -3000) * 0.0001
    summary_mask = (qa_layer & 3) == 0  # Bits 0-1: Good Quality
    adjacent_cloud_mask = (qa_layer & (1 << 8)) == 0  # Bit 8: Adjacent cloud
    mixed_cloud_mask = (qa_layer & (1 << 10)) == 0  # Bit 10: Mixed cloud
    snow_mask = (qa_layer & (1 << 14)) == 0  # Bit 14: Possible snow/ice
    shadow_mask = (qa_layer & (1 << 15)) == 0  # Bit 15: Possible shadow

    # Combine all masks
    strict_mask = (
            summary_mask &
            adjacent_cloud_mask &
            mixed_cloud_mask &
            snow_mask &
            shadow_mask
    )
    ndvicube = ndvicube.where(strict_mask)

    if clip_to_exact_aoi_outlines == True:
        ndvicube = ndvicube.rio.clip(aoi.geometry, aoi.crs, drop=True)


    print(f"Found {len(items)} items ({ndvicube.nbytes / (1024 ** 2):.2F} MB")

    return ndvicube

######################
## modis_loader8() ##
######################


def modis_loader8(aoi_path, datetime="2025-01-01/2025-06-30", clip_to_exact_aoi_outlines=True):
    """Loads MODIS 8-day surface reflectance via Planetary Computer and calculates NDVI."""

    # 1. Load aoi
    aoi = gpd.read_file(aoi_path).to_crs("EPSG:4326")

    # 2. Connect to Planetary Computer
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    # 3. Search the catalog
    print("Searching MODIS catalog for 8 day resolution...")
    search = catalog.search(
        collections=["modis-09Q1-061"],
        bbox=tuple(aoi.total_bounds),
        datetime=datetime
    )
    items = search.item_collection()

    # 4. Create the data cube
    cube = odc.stac.load(
        items,
        bands=["sur_refl_b01", "sur_refl_b02", "sur_refl_qc_250m"],
        bbox=tuple(aoi.total_bounds),
        crs="EPSG:4326",
        resolution=0.00225
    )

    # 5. Masking (Consolidated for brevity)
    qa = cube["sur_refl_qc_250m"]
    strict_mask = ((qa & 3) == 0) & ((qa & (1 << 8)) == 0) & ((qa & (1 << 10)) == 0)

    # 6. Calculate NDVI: (NIR - Red) / (NIR + Red)
    red = cube["sur_refl_b01"].where(strict_mask)
    nir = cube["sur_refl_b02"].where(strict_mask)
    ndvicube = (nir - red) / (nir + red)

    # 7. Clip
    if clip_to_exact_aoi_outlines:
        ndvicube = ndvicube.rio.clip(aoi.geometry, aoi.crs, drop=True)

    print(f"Found {len(items)} items ({ndvicube.nbytes / (1024 ** 2):.2f} MB)")

    return ndvicube


#################################
### modis_daily_ndvi_loader() ###
#################################

def modis_loader1(aoi_path, datetime="2025-01-01/2025-06-30", clip_to_exact_aoi_outlines=True):
    """Loads daily MODIS MCD43A4 (500m BRDF-Adjusted) via Planetary Computer and calculates NDVI."""

    # 1. Load AOI
    aoi = gpd.read_file(aoi_path).to_crs("EPSG:4326")

    # 2. Connect to Planetary Computer
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    # 3. Search the catalog for MCD43A4
    print("Searching MCD43A4 catalog for daily 500m resolution...")
    search = catalog.search(
        collections=["modis-43A4-061"],
        bbox=tuple(aoi.total_bounds),
        datetime=datetime
    )
    items = search.item_collection()

    if len(items) == 0:
        print("No items found for the given parameters.")
        return None

    # 4. Create the data cube targeting Red (Band 1) and NIR (Band 2)
    cube = odc.stac.load(
        items,
        bands=["Nadir_Reflectance_Band1", "Nadir_Reflectance_Band2"],
        bbox=tuple(aoi.total_bounds),
        crs="EPSG:4326",
        resolution=0.0045  # ~500m in degrees
    )

    # 5. Extract bands and handle valid ranges (Reflectance valid range is <= 10000)
    # xarray .where() keeps the values that are TRUE, turning the fill values to NaN.
    red = cube["Nadir_Reflectance_Band1"].where(cube["Nadir_Reflectance_Band1"] <= 10000)
    nir = cube["Nadir_Reflectance_Band2"].where(cube["Nadir_Reflectance_Band2"] <= 10000)

    # 6. Calculate NDVI
    # The scale factor mathematically cancels out in a normalized difference ratio
    ndvicube = (nir - red) / (nir + red)
    ndvicube.name = "NDVI"

    # 7. Clip to exact outlines
    if clip_to_exact_aoi_outlines:
        ndvicube = ndvicube.rio.clip(aoi.geometry, aoi.crs, drop=True)

    print(f"Found {len(items)} daily items. Array size: {ndvicube.nbytes / (1024 ** 2):.2F} MB")

    return ndvicube