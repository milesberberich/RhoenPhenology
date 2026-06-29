import re
from pathlib import Path

import pandas as pd
import rioxarray
import xarray as xr


def dwd_to_xarray(sos_dir, eos_dir):
    """Combine SOS and EOS GeoTIFF folders into one (band, time, y, x) DataArray."""

    def load(folder, band_name):
        tifs = sorted(Path(folder).glob("*.tif"))
        years = [int(re.search(r"(19|20)\d{2}", p.stem).group()) for p in tifs]
        tiles = [rioxarray.open_rasterio(p, masked=True).squeeze("band", drop=True) for p in tifs]

        da = xr.concat(tiles, dim=pd.to_datetime([f"{y}-01-01" for y in years]))
        da.name = band_name
        return da.rename({"concat_dim": "time"})

    sos = load(sos_dir, "SOS")
    eos = load(eos_dir, "EOS")
    cube = xr.concat([sos, eos], dim=pd.Index(["SOS", "EOS"], name="band"))
    return cube
