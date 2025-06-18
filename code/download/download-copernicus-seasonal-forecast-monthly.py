"""
Downloads Copernicus seasonal forecast/hindcast monthly-mean data for a specific variable
over the european domain.
Files are downloaded in 1x1 degree resolution. 
NOTE: to download you need to accept the terms and conditions found here:
https://cds.climate.copernicus.eu/datasets/seasonal-monthly-single-levels?tab=download
"""

import os
import numpy as np
import xarray as xr
import pandas as pd
import cdsapi
from investor import config, misc

# input ----------------------------------------------------------
area           = '74/-27/33/45'
variable       = 'msl' # mean-sea-level pressure
models         = ['cmcc','dwd','eccc','ecmwf','jma','meteo_france','ncep','ukmo']
init_years     = np.arange(2009, 2010, 1)
init_months    = np.array([1,2,3,4,5,6,7,8,9,10,11,12])
leadtime_month = ['1', '2', '3', '4', '5', '6']
path_out       = config.dirs['raw_forecast_monthly']
write2file     = True
# ----------------------------------------------------------------


def create_request_dict(year, month, system):
    return {
        'format': 'netcdf',
        'originating_centre': model,
        'system': system,
        'variable': variable,
        'product_type': 'monthly_mean',
        'year': str(year),
        'month': str(month).zfill(2),
        'leadtime_month': leadtime_month,
        'area': area,
    }


def download_forecast_data(client, year, month, path_out, write2file):

    system       = config.model_systems[model]
    filename     = f"{path_out}{model}/{variable}/{variable}_{model}_{system}_{year}-{str(month).zfill(2)}.nc"    
    request_dict = create_request_dict(year, month, system)

    print('')
    print(filename)
    print(request_dict)
    print('')
    
    if write2file:
        try:
            misc.tic()
            client.retrieve('seasonal-monthly-single-levels', request_dict, filename)
            misc.toc()
        except Exception as e:
            print(f"Download failed for {year}-{month:02d}: {e}")
    

        
if __name__ == "__main__":
    
    c = cdsapi.Client()

    for model in models:
        for year in init_years:
            for month in init_months:
                download_forecast_data(c, year, month, path_out, write2file)
