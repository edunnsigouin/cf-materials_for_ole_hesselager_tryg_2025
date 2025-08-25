"""
Calculates the standardized and non-standardized monthly nao for era5 in seasonal forecast format. 
NAO is calculated the 'station-way', i.e. the difference in mean-sea-level pressure between
azores and iceland. Standardization removes time-mean and divides by standard deviation.
"""

import os
import numpy as np
import xarray as xr
import pandas as pd
import cdsapi
from materials_for_ole_hesselager_tryg_2025 import config, misc

# input ----------------------------------------------------------
init_years     = np.arange(2010, 2025, 1)
init_months    = np.array([1,2,3,4,5,6,7,8,9,10,11,12])
leadtime_month = ['1', '2', '3', '4', '5', '6']
latlon_azores  = [37.74, -25.67]
latlon_iceland = [64.15, -21.94]
path_in        = config.dirs['processed_era5_forecast_monthly'] 
path_out       = config.dirs['processed_era5_forecast_monthly'] 
write2file     = True
# ----------------------------------------------------------------


def load_msl_era5_data(year, month, path_in):
    filename = f"{path_in}msl/msl_{year}-{str(month).zfill(2)}.nc"
    return xr.open_dataset(filename)['msl']


def calc_nao_station(msl,latlon_azores,latlon_iceland):

    # get nao station grid points
    lat_points = [latlon_azores[0], latlon_iceland[0]]
    lon_points = [latlon_azores[1], latlon_iceland[1]]
    msl        = msl.sel(latitude=lat_points,longitude=lon_points,method='nearest')

    # calc nao
    azores_val  = msl.sel(latitude=latlon_azores[0], longitude=latlon_azores[1], method='nearest')
    iceland_val = msl.sel(latitude=latlon_iceland[0], longitude=latlon_iceland[1], method='nearest')
    nao         = azores_val - iceland_val
    nao         = nao.rename('nao')

    return nao



def standardize_nao(nao_raw):
    """standardizes nao timeseries by removing the time-mean and dividing by the standard deviation"""

    mu_time = nao_raw.mean(dim='forecast_reference_time', skipna=True)
    sd_time = nao_raw.std(dim='forecast_reference_time', skipna=True)
    nao     = (nao_raw - mu_time) / sd_time

    return nao



def save_nao_to_file(path_out,nao_raw,nao,init_years,init_months,write2file):
    """Combine raw and standardized nao into one dataset + save to file"""
    nao_raw                                = nao_raw.rename_vars({'nao':'nao_raw'})
    ds_out                                 = xr.merge([nao_raw,nao])
    desc1                                  = "station-based NAO index following Scaife et al. 2014 GRL"
    desc2                                  = "Standardized station-based NAO index following Scaife et al. 2014 GRL"
    ds_out['nao_raw'].attrs['description'] = desc1
    ds_out['nao_raw'].attrs['units']       = 'Pa'
    ds_out['nao'].attrs['description']     = desc2
    ds_out['nao'].attrs['units']           = 'none'
    
    if write2file:
        timestamp    = str(init_years[0]) + '-' + str(init_months[0]).zfill(2) + '_' + str(init_years[-1]) + '-' + str(init_months[-1]).zfill(2)
        filename_out = f'{path_out}nao/nao_{timestamp}.nc'
        ds_out.to_netcdf(filename_out)


    


if __name__ == "__main__":
    
    forecast_list = [] # to dump all forecast files in

    for year in init_years:
        for month in init_months:
            print(year,month)
            msl     = load_msl_era5_data(year, month, path_in)
            nao_tmp = calc_nao_station(msl,latlon_azores,latlon_iceland)
            forecast_list.append(nao_tmp)
            
    nao_raw = xr.combine_by_coords(forecast_list, combine_attrs="override")
    nao     = standardize_nao(nao_raw)
    save_nao_to_file(path_out,nao_raw,nao,init_years,init_months,write2file)

