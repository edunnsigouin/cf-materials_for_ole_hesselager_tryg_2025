"""
hard coded paths in cf-trygdanmarkstormpred
"""

cf_space             = "/nird/projects/NS9873K/"
proj                 = "/nird/home/edu061/cf-investor/"
data_interim         = proj + "data/interim/"
fig                  = proj + "fig/"

raw                  = cf_space + "etdu/raw/"
raw_forecast_monthly = raw + 'seasonal/monthly/'
raw_era5_monthly     = raw + 'era5/monthly/'
raw_noaa             = raw + 'noaa/'
raw_tryg             = raw + 'tryg/'
raw_skadepool        = raw + 'skadepool/'

processed                       = cf_space + "etdu/processed/cf-investor/"
processed_forecast_seasonal     = processed + 'seasonal_forecast/seasonal/'
processed_forecast_monthly      = processed + 'seasonal_forecast/monthly/'
processed_era5_monthly          = processed + 'era5/monthly/'
processed_era5_seasonal         = processed + 'era5/seasonal/'
processed_era5_forecast_monthly = processed + 'era5/monthly/seasonal_forecast_format/' 
processed_noaa                  = processed + 'noaa/'
processed_tryg                  = processed + 'tryg/'
processed_skadepool             = processed + 'skadepool/'
processed_glm                   = processed + 'fitted_models/glm/'
processed_lr                    = processed + 'fitted_models/lr/'


dirs = {"proj":proj,
        "data_interim":data_interim,
        "fig":fig,
        "raw":raw,
        "raw_forecast_monthly":raw_forecast_monthly,
        "raw_era5_monthly":raw_era5_monthly,
        "raw_noaa":raw_noaa,
        "raw_tryg":raw_tryg,
        "raw_skadepool":raw_skadepool,
        "processed":processed,
        "processed_forecast_seasonal":processed_forecast_seasonal,
        "processed_forecast_monthly":processed_forecast_monthly,
        "processed_era5_monthly":processed_era5_monthly,
        "processed_era5_seasonal":processed_era5_seasonal,
        "processed_era5_forecast_monthly":processed_era5_forecast_monthly,
        "processed_noaa":processed_noaa,
        "processed_tryg":processed_tryg,
        "processed_skadepool":processed_skadepool,
        "processed_glm":processed_glm,
        "processed_lr":processed_lr,
}        


models = ['ecmwf','cmcc','dwd','eccc','jma','meteo_france','ncep','ukmo']

model_systems = {'ecmwf':51,
                 'cmcc':35,
                 'dwd':21,
                 'eccc':5,
                 'jma':3,
                 'meteo_france':8,
                 'ncep':2,
                 'ukmo':602,
}
