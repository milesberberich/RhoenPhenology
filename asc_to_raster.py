
import numpy as np
import rasterio
from rasterio.transform import from_origin

def asc_to_raster(asc_path: str, output_path: str, crs: str = "EPSG:31467") -> None:
    """
    Convert an ASC file to a GeoTIFF raster.

    Args:
        asc_path:    Path to the input .asc file
        output_path: Path for the output .tif file
        crs:         CRS of the input data — defaults to EPSG:31467 (Gauss-Krüger Zone 3)
    """
    with open(asc_path, "r") as f:
        lines = f.readlines()

    # --- Parse header ---
    header = {}
    data_start = 0
    for i, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) == 2 and not parts[0].lstrip("-").isdigit():
            header[parts[0].lower()] = float(parts[1])
            data_start = i + 1
        else:
            break

    ncols     = int(header["ncols"])
    nrows     = int(header["nrows"])
    cellsize  = header["cellsize"]
    nodata    = header.get("nodata_value", -9999)

    # Handle both corner and center registration
    if "xllcorner" in header:
        xll = header["xllcorner"]
        yll = header["yllcorner"]
    else:
        # Shift from cell center to cell corner
        xll = header["xllcenter"] - cellsize / 2
        yll = header["yllcenter"] - cellsize / 2

    # --- Parse data ---
    values = []
    for line in lines[data_start:]:
        values.extend(float(v) for v in line.strip().split())

    data = np.array(values, dtype=np.float32).reshape(nrows, ncols)
    data[data == nodata] = np.nan

    # --- Build transform ---
    # from_origin expects the top-left corner (xll, yll + nrows * cellsize)
    transform = from_origin(
        west  = xll,
        north = yll + nrows * cellsize,
        xsize = cellsize,
        ysize = cellsize,
    )

    # --- Write GeoTIFF ---
    with rasterio.open(
        output_path,
        mode    = "w",
        driver  = "GTiff",
        height  = nrows,
        width   = ncols,
        count   = 1,
        dtype   = "float32",
        crs     = crs,
        transform = transform,
        nodata  = np.nan,
    ) as dst:
        dst.write(data, 1)

    print(f"Saved raster to {output_path}  ({ncols}×{nrows}, CRS={crs})")