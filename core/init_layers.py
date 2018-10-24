#!/usr/bin/env python

import numpy as np
import logging

from config import *
from constants import *


def init_layer(temperature_2m):

    layer_heights = 0.1 * np.ones(number_layers)

    # TODO implement density gradient profile from core.core_1D
    rho = ice_density * np.ones(number_layers)
    rho[0] = 250.
    rho[1] = 400.
    rho[2] = 550.
    rho[3] = 700.
    rho[4] = snow_ice_threshold

    # Init temperature profile
    # TODO implement temperature gradient profile from core.core_1D
    temperature_surface = temperature_bottom * np.ones(number_layers)
    for i in range(len(temperature_surface)):
        gradient = ((temperature_2m - temperature_bottom) / number_layers)
        temperature_surface[i] = temperature_2m - gradient * i

    # Init liquid water content
    liquid_water_content = np.zeros(number_layers)

    return layer_heights, rho, temperature_surface, liquid_water_content
    
def init_layer_two(initial_snowheight, temperature_2m):
        
    log = logging.getLogger(__name__)
        
    # Init layers
    layer_heights =  np.ones(int(initial_snowheight // initial_snow_layer_heights)) * initial_snow_layer_heights
    layer_heights =  np.append(layer_heights, np.ones(int(initial_glacier_height // initial_glacier_layer_heights)) * initial_glacier_layer_heights)
    number_layers = len(layer_heights)

    # Init properties # TODO add Init density of firn profile with gradient
    rho = rho_top * np.ones(number_layers)
    
    log.info(str(rho))
    
    # init density of snow+firn profile
    firn_density_gradient = (rho_top-ice_density)/(number_layers)
    
    log.info(str(firn_density_gradient))
    log.info(str(np.arange(number_layers)))
    
    for i in np.arange(number_layers):
        rho[int(i)] = rho_top - firn_density_gradient * i 

    log.info(str(rho))
        
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
    
    log.info(str(rho))
    
    # Init temperature new
    temperature_gradient = (temperature_2m - temperature_bottom) / (initial_glacier_height // initial_glacier_layer_heights)
    for i in np.arange(0 ,(initial_glacier_height // initial_glacier_layer_heights)):
        temperature_profile[int(i)] = temperature_2m - temperature_gradient * i
        
    #return layer_heights, layer_densities, layer_temperature, liquid_water_content
    return layer_heights, rho, temperature_profile, liquid_water_content
