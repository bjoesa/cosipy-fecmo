'''
    Input data reading
        and
    Initital layer setup
'''

import xarray as xr
from datetime import date
import numpy as np
import logging
from config import *
from config import input_netcdf, output_netcdf
from constants import *


def read_input():

    ''' Reads input parameters from climatic fields '''

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


def init_layer_two(initial_snowheight, temperature_2m):

    ''' Initialize layering properties '''
        
    log = logging.getLogger(__name__)
        
    # Init layers
    layer_heights =  np.ones(int(round(initial_snowheight / initial_snow_layer_heights))) * initial_snow_layer_heights
    layer_heights =  np.append(layer_heights, np.ones(int(round(initial_glacier_height / initial_glacier_layer_heights))) * initial_glacier_layer_heights)
    number_layers = len(layer_heights)

    # Init properties 
    rho = rho_top * np.ones(number_layers)
    
    # init density of snow+firn profile
    firn_density_gradient = (rho_top - ice_density) / number_layers
    
    #log.debug(str(firn_density_gradient))
    #log.debug(str(np.arange(number_layers)))
    
    for i in np.arange(number_layers):
        rho[int(i)] = rho_top - firn_density_gradient * i 

    # ---------
    #rho = firn_ice_threshold * np.ones(len(layer_heights))
    #rho = ice_density * np.ones(len(layer_heights))
    temperature_profile = temperature_bottom * np.ones(len(layer_heights))
    liquid_water_content = np.zeros(number_layers)
    
    # Init density of snow profile
    # density_gradient = (rho_top-rho_bottom)/(initial_snowheight//initial_snow_layer_heights)
    
    # log.info(str(density_gradient))
    # log.info(str(np.arange(initial_snowheight//initial_snow_layer_heights)))
    
    # for i in np.arange((initial_snowheight//initial_snow_layer_heights)):
       # rho[int(i)] = rho_top - density_gradient * i 
       
    # log.info(str(rho))
       
    # set bottom layer to ice_density
    rho[number_layers-1] = ice_density
    
    log.debug('---ARRAY---> Density layering, with bottom ice:')
    log.debug(str(rho))
    
    # Init temperature new
    temperature_gradient = (temperature_2m - temperature_bottom) / (initial_glacier_height // initial_glacier_layer_heights)
    for i in np.arange(0 ,(initial_glacier_height // initial_glacier_layer_heights)):
        temperature_profile[int(i)] = temperature_2m - temperature_gradient * i
        
    #return layer_heights, layer_densities, layer_temperature, liquid_water_content
    return layer_heights, rho, temperature_profile, liquid_water_content
