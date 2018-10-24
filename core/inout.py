"""
    ATTENTION: in Python 3.x the io module is the default interface to access files and 
    streams! (https://docs.python.org/2/library/io.html#module-io)
 This file reads in the input data (model forcing) and write output the output to a netcdf file
"""

# import scipy.io as sio
import xarray as xr
from datetime import date
from config import input_netcdf, output_netcdf


def read_input():
    DATA = xr.open_dataset(input_netcdf)
    wind_speed = DATA['u2'].values            # Wind speed (magnitude) m/s
    solar_radiation = DATA['G'].values           # Solar radiation at each time step [W m-2]
    temperature_2m = DATA['T2'].values         # Air temperature (2m over ground) [K]
    relative_humidity = DATA['rh2'].values       # Relative humidity (2m over ground)[%]
    precipitation = DATA['prec'].values                  # Total precipitation per time step [mmWE]
    air_pressure = DATA['p'].values              # Air Pressure [hPa]
    cloud_cover = DATA['N'].values               # Cloud cover  [fraction][%/100]
    initial_snow_height = DATA['sh'].values      # Initial snow height [m]
    #   wind_speed = DATA['u'].values            # Wind speed (magnitude) m/s
    #   solar_radiation = DATA['G'].values           # Solar radiation at each time step [W m-2]
    #   temperature_2m = DATA['T'].values         # Air temperature (2m over ground) [K]
    #   relative_humidity = DATA['rH'].values       # Relative humidity (2m over ground)[%]
    #   snowfall = DATA['snowfall'].values           # Snowfall per time step [m]
    #   air_pressure = DATA['p'].values              # Air Pressure [hPa]
    #   cloud_cover = DATA['N'].values               # Cloud cover  [fraction][%/100]
    #   initial_snow_height = DATA['sh'].values      # Initial snow height [m]
    return wind_speed, solar_radiation, temperature_2m, relative_humidity, precipitation, air_pressure, cloud_cover, initial_snow_height

def write_output_1D(lw_in,lw_out,h,lh,g,tsk,sw_net,albedo,sh):
    today = date.today()

    lw_in = xr.DataArray(lw_in)
    lw_out = xr.DataArray(lw_out)
    h = xr.DataArray(h)
    lh = xr.DataArray(lh)
    g = xr.DataArray(g)
    tsk = xr.DataArray(tsk)
    sw_net = xr.DataArray(sw_net)
    albedo = xr.DataArray(albedo)
    sh = xr.DataArray(sh)
    data = xr.Dataset({
                    'lw_in':lw_in,
                    'lw_out':lw_out,
                    'h':h,
                    'lh':lh,
                    'g':g,
                    'tsk':tsk,
                    'sw_net':sw_net,
                    'albedo':albedo,
                    'sh':sh
                    }
                    )
    data.attrs['TITLE'] = 'COSIPY 1D results'
    data.attrs['CREATION_DATE'] = str(today)
    data.to_netcdf(output_netcdf)

