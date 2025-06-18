"""
compares yearly nao timeseries from monthly era5 and a seasonal forecast.
Options for lead month, model, aggregation (month, season, quarter). 
"""

import numpy            as np
import xarray           as xr
import pandas           as pd
from investor           import config, misc
from matplotlib         import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors  import to_rgba
from matplotlib.patches import Patch
from matplotlib.lines   import Line2D

# input --------------------------------------------
model            = 'jma'
system           = config.model_systems[model]
init_years       = np.arange(2010,2025,1)
lead_month       = 1
target_month     = 1
path_in_era5     = config.dirs['processed_era5_forecast_monthly']
path_in_forecast = config.dirs['processed_forecast_monthly']
path_out         = config.dirs['fig'] + 'forecast/' 
write2file       = False
# --------------------------------------------------


def load_nao_data(path_in_era5, path_in_forecast, init_years, model, system):

    # Load full datasets
    filename_forecast = f'{path_in_forecast}nao_{model}_{system}_{init_years[0]}-01_{init_years[-1]}-12.nc'
    ds_forecast       = xr.open_dataset(filename_forecast)

    filename_era5     = f'{path_in_era5}nao/nao_{init_years[0]}-01_{init_years[-1]}-12.nc'
    ds_era5           = xr.open_dataset(filename_era5)

    # convert to hPa from Pa
    ds_forecast['nao_raw_ensemble_mean'] = ds_forecast['nao_raw_ensemble_mean']/1000
    ds_forecast['nao_raw_ensemble']      = ds_forecast['nao_raw_ensemble']/1000
    ds_era5['nao_raw']                   = ds_era5['nao_raw']/1000

    return ds_era5, ds_forecast

    
def filter_forecasts_by_valid_month(ds: xr.Dataset, lead_month: int, target_month: int) -> xr.Dataset:
    """
    Filters a forecast dataset to include only entries where:
    forecastMonth == lead_month AND the corresponding valid_time lands in target_month.

    Parameters:
    - ds: xarray Dataset with dimensions (forecast_reference_time, forecastMonth)
    - lead_month: int (e.g. 1, 2, 3, ...)
    - target_month: int (calendar month 1–12)

    Returns:
    - Filtered xarray Dataset with forecast_reference_time subset accordingly,
      and forecastMonth dimension reduced to lead_month only.
    """

    # Step 1: select the desired lead month
    ds_lead = ds.sel(forecastMonth=lead_month)
    
    # Step 2: calculate valid_time for each forecast given init time and lead time
    init_times  = ds_lead['forecast_reference_time'].values
    valid_times = pd.to_datetime(init_times) + pd.DateOffset(months=(lead_month-1))
    
    # Step 3: find indices where valid_time month matches target_month
    month_mask      = valid_times.month == target_month
    selected_inits  = init_times[month_mask]
    filtered_valids = valid_times[month_mask]
    
    # Step 4: subset the dataset
    ds_filtered = ds_lead.sel(forecast_reference_time=selected_inits)

    # Step 5: assign valid_time coordinate
    ds_filtered = ds_filtered.assign_coords(valid_time=("forecast_reference_time", filtered_valids))

    return ds_filtered



def plot_nao(nao_era5, nao_forecast, lead_month, target_month, write2file, filename_out):

    fontsize = 11
    figsize  = (12, 5)
    fig, ax  = plt.subplots(figsize=figsize)

    # Main lines
    ax.plot(nao_era5.valid_time, nao_era5['nao_raw'], 'k', linewidth=2, label='ERA5')
    ax.plot(nao_era5.valid_time, nao_era5['nao_raw'], 'ko')

    ax.plot(nao_forecast.valid_time, nao_forecast['nao_raw_ensemble_mean'],color='tab:blue', linewidth=2)
    ax.plot(nao_forecast.valid_time, nao_forecast['nao_raw_ensemble_mean'],color='tab:blue', marker='o')

    # Box plots overlaid: use a lighter color of tab:blue
    light_blue     = to_rgba('tab:blue', alpha=0.3)
    forecast_times = nao_forecast['valid_time'].values
    ensemble_data  = nao_forecast['nao_raw_ensemble'].values  # shape: (number, time)
    
    # box and whisker
    for i, vt in enumerate(forecast_times):
        data = ensemble_data[:, i]
        data_clean = data[~np.isnan(data)]

        if len(data_clean) > 0:
            ax.boxplot(data_clean,
                       positions=[mdates.date2num(vt)],
                       widths=150,
                       showfliers=False,
                       patch_artist=True,
                       boxprops=dict(facecolor=light_blue, color='tab:blue'),
                       capprops=dict(color='tab:blue'),
                       whiskerprops=dict(color='tab:blue'),
                       medianprops=dict(color='tab:blue'))

    # Compute correlation
    common_dates = nao_era5['valid_time'].values
    mask         = np.isfinite(nao_era5['nao_raw'].values) & np.isfinite(nao_forecast['nao_raw_ensemble_mean'].values)
    if np.any(mask):
        correlation = np.corrcoef(nao_era5['nao_raw'].values[mask],nao_forecast['nao_raw_ensemble_mean'].values[mask])[0, 1]
    else:
        correlation = np.nan

    # Title
    month_name = pd.to_datetime(f'2000-{target_month:02d}-01').strftime('%b')
    ax.set_title(f"Target month: {month_name}, Lead month: {lead_month}, Correlation: {correlation:.2f}", fontsize=fontsize+1)

    # Custom legend handles
    handles = [
        Line2D([], [], color='k', linewidth=2, label='ERA5'),
        Line2D([], [], color='tab:blue', linewidth=2, label='Ensemble mean'),
        Patch(facecolor=light_blue, edgecolor='tab:blue', label='Ensemble')
    ]
    ax.legend(handles=handles, frameon=False, loc='best', ncol=3)

    # Formatting
    ax.set_xlabel('Time', fontsize=fontsize)
    ax.set_ylabel('NAO Index (hPa)', fontsize=fontsize)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()
    
    if write2file:
        fig.savefig(filename_out, bbox_inches='tight')
        print(f"Saved figure to: {filename_out}")

    plt.show()


        
if __name__ == "__main__":

    ds_era5, ds_forecast = load_nao_data(path_in_era5,path_in_forecast,init_years,model,system)
    ds_era5              = filter_forecasts_by_valid_month(ds_era5, lead_month, target_month)
    ds_forecast          = filter_forecasts_by_valid_month(ds_forecast, lead_month, target_month)

    month_abbr   = pd.to_datetime(f'2000-{target_month:02d}-01').strftime('%b')
    filename_out = f"{path_out}t_nao_{model}_{system}_target-{month_abbr}_lead-{lead_month}_{init_years[0]}-{init_years[-1]}.pdf"

    plot_nao(ds_era5, ds_forecast, lead_month, target_month, write2file, filename_out)
    
