import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.mask import mask as rio_mask
from pathlib import Path
import json
from shapely.geometry import shape
from shapely.ops import transform as shp_transform
from pyproj import Transformer

def asc_to_raster(asc_path, output_path, crs="EPSG:25832", clip_geojson=None):

    with open(asc_path) as f:
        lines = f.readlines()

    header, i = {}, 0
    while len(lines[i].split()) == 2 and not lines[i].split()[0].lstrip("-").isdigit():
        k, v = lines[i].split()
        header[k.lower()] = float(v)
        i += 1

    ncols, nrows, cellsize = int(header["ncols"]), int(header["nrows"]), header["cellsize"]
    xll = header.get("xllcorner") or header["xllcenter"] - cellsize / 2
    yll = header.get("yllcorner") or header["yllcenter"] - cellsize / 2

    data = np.array(lines[i:], dtype=str)
    data = np.hstack([r.split() for r in data]).astype(np.float32).reshape(nrows, ncols)
    data[data == header.get("nodata_value", -9999)] = np.nan

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    profile = dict(driver="GTiff", height=nrows, width=ncols, count=1, dtype="float32",
                   crs=crs, transform=from_origin(xll, yll + nrows * cellsize, cellsize, cellsize), nodata=np.nan)

    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(data, 1)

    from pyproj import Transformer
    from shapely.ops import transform as shp_transform

    if clip_geojson:
        geojson = json.load(open(clip_geojson))
        geoms = [f["geometry"] for f in geojson["features"]] if geojson["type"] == "FeatureCollection" else [geojson]

        t = Transformer.from_crs("EPSG:25832", "EPSG:31467", always_xy=True)
        geoms = [shp_transform(t.transform, shape(g)).__geo_interface__ for g in [shape(g) for g in geoms]]

        with rasterio.open(output_path) as src:
            clipped, tf = rio_mask(src, geoms, crop=True, nodata=-9999)
            profile = {**src.meta, "height": clipped.shape[1], "width": clipped.shape[2], "transform": tf}

        clipped = clipped.astype(np.float32)
        clipped[clipped == -9999] = np.nan

        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(clipped)