"""
converts era5 monthly data into monthly seasonal forecast/hindcast format.
"""

import numpy          as np
import xarray         as xr
import pandas         as pd
from dask.diagnostics import ProgressBar
from materials_for_ole_hesselager_tryg_2025         import config,misc

# INPUT -----------------------------------------------
variable         = 'msl'
init_years       = np.arange(2024,2025,1)
init_months      = np.arange(1,13,1)
n_lead_months    = 6
path_in          = config.dirs['raw_era5_monthly'] + variable + '/'
path_out         = config.dirs['processed_era5_forecast_monthly'] + variable + '/'
write2file       = True
# -----------------------------------------------------         


def load_era5_lead_months(year,month,variable,n_lead_months,path_in):

    init_date       = str(year) + '-' + str(month).zfill(2)
    lead_months     = pd.date_range(init_date,periods=n_lead_months,freq="MS").strftime('%Y-%m')
    filenames_in    = [path_in + variable + '_' + str(lead_month) + '.nc' for lead_month in lead_months]
    
    with ProgressBar():
        da = xr.open_mfdataset(filenames_in)[variable].compute()

    return da


def save_to_file(da,variable,year,month,path_out,write2file):

    # Create new coordinates
    forecast_reference_time = pd.Timestamp(f"{year}-{str(month).zfill(2)}")
    forecast_months = np.arange(da.sizes['time']) + 1 # or np.arange(n_lead_months)

    # Rename and expand dimensions
    da = da.rename({'time': 'forecastMonth'})  # Rename time -> forecastMonth
    da = da.expand_dims({'forecast_reference_time': [forecast_reference_time]})  # Add new dimension
    da = da.assign_coords({'forecastMonth': forecast_months})  # Set forecastMonth coord

    filename_out = f'{path_out}{variable}_{str(year)}-{str(month).zfill(2)}.nc'
    if write2file:
        da.to_netcdf(filename_out)
    

        
if __name__ == "__main__":
    
    for year in init_years:
        for month in init_months:
        
            da = load_era5_lead_months(year,month,variable,n_lead_months,path_in)

            save_to_file(da,variable,year,month,path_out,write2file)
