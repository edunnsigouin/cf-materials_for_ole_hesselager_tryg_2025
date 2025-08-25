"""
Calculates the standardized and non-standardized monthly nao for seasonal forecasts taken from copernicus.
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
models         = ['ecmwf']
init_years     = np.arange(2009, 2025, 1)
init_months    = np.array([1,2,3,4,5,6,7,8,9,10,11,12])
leadtime_month = ['1', '2', '3', '4', '5', '6']
latlon_azores  = [37.74, -25.67]
latlon_iceland = [64.15, -21.94]
path_in        = config.dirs['raw_forecast_monthly'] 
path_out       = config.dirs['processed_forecast_monthly'] 
write2file     = True
# ----------------------------------------------------------------


def load_msl_forecast_data(year, month, model, path_in):

    system   = config.model_systems[model]
    filename = f"{path_in}{model}/msl/msl_{model}_{system}_{year}-{str(month).zfill(2)}.nc"
    
    if os.path.exists(filename):
        msl = xr.open_dataset(filename)['msl']
    else:
        # Fallback to a known-good reference file (e.g., 2010-01)
        fallback_file = f"{path_in}{model}/msl/msl_{model}_{system}_2010-01.nc"
        print(f"File not found: {filename}. Using fallback with NaNs: {fallback_file}")
        
        if not os.path.exists(fallback_file):
            raise FileNotFoundError(f"Fallback file also missing: {fallback_file}")

        ref_ds      = xr.open_dataset(fallback_file)
        msl         = ref_ds['msl'].copy(deep=True)
        msl.data[:] = np.nan  # Fill data with NaNs

        # Patch forecast_reference_time
        target_time = np.datetime64(f"{year}-{str(month).zfill(2)}-01T00:00:00", 'ns')
        if 'forecast_reference_time' in msl.coords:
            msl = msl.assign_coords(forecast_reference_time=("forecast_reference_time", [target_time]))

        ref_ds.close()

    # Ensure ensemble dimension 'number' has length 51
    # so that all models and forecast have same number dimension size.
    if 'number' in msl.dims and msl.sizes['number'] < 51:
        
        existing_n = msl.sizes['number']
        new_shape = list(msl.shape)
        new_shape[msl.dims.index('number')] = 51

        # Create new array filled with NaNs
        new_data = np.full(new_shape, np.nan, dtype=msl.dtype)
        new_data[:existing_n, ...] = msl.data

        # Create new coords (extend 'number' coordinate if needed)
        new_coords = msl.coords.to_dataset().copy()
        if 'number' in new_coords:
            full_numbers = np.arange(51)
            new_coords['number'] = ('number', full_numbers)

        msl = xr.DataArray(
            new_data,
            dims=msl.dims,
            coords={dim: new_coords[dim] for dim in msl.dims},
            attrs=msl.attrs,
        )

    if ((model == 'jma') or (model=='ncep') or (model =='ukmo')):
        msl = msl.rename({'indexing_time':'forecast_reference_time'})
        
    return msl


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



def standardize_nao(nao_raw_ensemble,nao_raw_ensemble_mean):
    """standardizes nao timeseries by removing the time-mean and dividing by the standard deviation.
    individual ensembles are standardized relative to time and ensemble-mean and std"""

    # Mean over ensemble members, standardize in time
    mu_time           = nao_raw_ensemble_mean.mean(dim='forecast_reference_time', skipna=True)
    sd_time           = nao_raw_ensemble_mean.std(dim='forecast_reference_time', skipna=True)
    nao_ensemble_mean = (nao_raw_ensemble_mean - mu_time) / sd_time

    # Full ensemble standardization across year + ensembles (number)
    mu_all            = nao_raw_ensemble.mean(dim=('forecast_reference_time', 'number'), skipna=True)
    sd_all            = nao_raw_ensemble.std(dim=('forecast_reference_time', 'number'), skipna=True)
    nao_ensemble      = (nao_raw_ensemble - mu_all) / sd_all
    
    return nao_ensemble, nao_ensemble_mean



def save_nao_to_file(path_out,nao_raw_ensemble,nao_raw_ensemble_mean,nao_ensemble,nao_ensemble_mean,init_years,init_months,model,write2file):
    """Combine ensemble-mean and ensemble into one dataset"""
    nao_ensemble_mean                                    = nao_ensemble_mean.rename_vars({'nao':'nao_ensemble_mean'})
    nao_ensemble                                         = nao_ensemble.rename_vars({'nao':'nao_ensemble'})
    nao_raw_ensemble                                     = nao_raw_ensemble.rename_vars({'nao':'nao_raw_ensemble'})
    nao_raw_ensemble_mean                                = nao_raw_ensemble_mean.rename_vars({'nao':'nao_raw_ensemble_mean'})
    ds_out                                               = xr.merge([nao_raw_ensemble, nao_raw_ensemble_mean, nao_ensemble, nao_ensemble_mean])
    desc1                                                = "station-based NAO index following Scaife et al. 2014 GRL"
    desc2                                                = "Standardized station-based NAO index following Scaife et al. 2014 GRL"
    ds_out['nao_raw_ensemble'].attrs['description']      = desc1
    ds_out['nao_raw_ensemble'].attrs['units']            = 'Pa'
    ds_out['nao_raw_ensemble_mean'].attrs['description'] = desc1
    ds_out['nao_raw_ensemble_mean'].attrs['units']       = 'Pa'
    ds_out['nao_ensemble_mean'].attrs['description']     = desc2
    ds_out['nao_ensemble_mean'].attrs['units']           = 'none'
    ds_out['nao_ensemble'].attrs['description']          = desc2
    ds_out['nao_ensemble'].attrs['units']                = 'none'
    
    if write2file:
        timestamp    = str(init_years[0]) + '-' + str(init_months[0]).zfill(2) + '_' + str(init_years[-1]) + '-' + str(init_months[-1]).zfill(2)
        filename_out = f'{path_out}nao_{model}_{config.model_systems[model]}_{timestamp}.nc'
        ds_out.to_netcdf(filename_out)


    


if __name__ == "__main__":
    
    for model in models:

        forecast_list = [] # to dump all forecast files in

        for year in init_years:
            for month in init_months:

                print(year,month)
                msl     = load_msl_forecast_data(year, month, model, path_in)
                nao_tmp = calc_nao_station(msl,latlon_azores,latlon_iceland)
                forecast_list.append(nao_tmp)

        nao_raw_ensemble                = xr.combine_by_coords(forecast_list, combine_attrs="override")
        nao_raw_ensemble_mean           = nao_raw_ensemble.mean(dim='number',skipna=True)
        nao_ensemble, nao_ensemble_mean = standardize_nao(nao_raw_ensemble,nao_raw_ensemble_mean)

        save_nao_to_file(path_out,nao_raw_ensemble,nao_raw_ensemble_mean, nao_ensemble, nao_ensemble_mean, init_years,init_months,model,write2file)

