"""
Downloads ERA5 monthly-mean data from the Copernicus Climate Data Store (CDS)
on a 1x1 degree grid over the specified domain.

To access the data, you must accept the terms and conditions:
https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels-monthly-means
"""

import os
import numpy as np
import xarray as xr
import cdsapi
import pandas as pd
from investor import config, misc

# input -----------------------------------------------------------
area       = '74/-27/33/45'       # Bounding box: North/West/South/East
grid       = '1.0/1.0'            # Resolution (lat/lon)
variable   = 'msl'
years      = np.arange(2025, 2026, 1)
months     = np.arange(1, 6, 1)
path_out   = config.dirs['raw_era5_monthly']
write2file = True
# -----------------------------------------------------------------


def create_request_dict(year, month):
    return {
        'product_type': 'monthly_averaged_reanalysis',
        'format': 'netcdf',
        'variable': variable,
        'year': str(year),
        'month': str(month).zfill(2),
        'time': '00:00',
        'area': area,
        'grid': grid,
    }


def download_era5_data(client, year, month, path_out, write2file):

    filename     = f"{path_out}{variable}/{variable}_{year}-{str(month).zfill(2)}.nc"
    tmp_filename = f"{path_out}{variable}/tmp_{year}-{str(month).zfill(2)}.nc"
    request_dict = create_request_dict(year, month)

    print(f"\nDownloading: {filename}")
    print(f"Request: {request_dict}\n")

    if write2file:
        try:
            misc.tic()
            client.retrieve('reanalysis-era5-single-levels-monthly-means', request_dict, tmp_filename)
            ds = xr.open_dataset(tmp_filename)
            ds = ds.rename({'valid_time': 'time'}).drop_vars(['expver', 'number'], errors='ignore')
            ds.to_netcdf(filename)
            ds.close()
            os.remove(tmp_filename)
            misc.toc()
        except Exception as e:
            print(f"Download failed for {year}-{month:02d}: {e}")



# ---------------------------- MAIN SCRIPT ------------------------
if __name__ == "__main__":

    c = cdsapi.Client()

    for year in years:
        for month in months:
            download_era5_data(c, year, month, path_out, write2file)
