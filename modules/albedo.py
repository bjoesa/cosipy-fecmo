import numpy as np
from constants import *


def updateAlbedo(GRID, hours_since_snowfall):
    """ This methods updates the albedo """

    # Check if snow or ice
    if (GRID.get_rho_node(0) <= firn_ice_threshold):
    
        # Get current snowheight from layer height 
        idx = (next((i for i, x in enumerate(GRID.get_rho()) if x >= firn_ice_threshold), None))
        h = np.sum(GRID.get_hlayer()[0:idx])
    
        # Surface albedo according to Oerlemans & Knap 1998, JGR)
        alphaSnow = albedo_firn + (albedo_fresh_snow - albedo_firn) * \
                                  np.exp((-hours_since_snowfall) / (albedo_mod_snow_aging * 24.0))
        alphaMod = alphaSnow + (albedo_ice - alphaSnow) * \
                               np.exp((-1.0*h) / (albedo_mod_snow_depth / 100.0))
    
    else:
    
        # If no snow cover than set albedo to ice albedo
        alphaMod = albedo_ice


    return alphaMod


def updateAlbedo_dev(GRID, hours_since_snowfall):
    """ This methods updates the albedo """

    # Check if snow or ice
    if (GRID.get_rho_node(0) <= firn_ice_threshold):
    
        # Get current snowheight from layer height 
        idx = (next((i for i, x in enumerate(GRID.get_rho()) if x >= firn_ice_threshold), None))
        h = np.sum(GRID.get_hlayer()[0:idx])
    
        # Surface albedo according to Oerlemans & Knap 1998, JGR)
        alphaSnow = albedo_firn + (albedo_fresh_snow - albedo_firn) * \
                                  np.exp((-hours_since_snowfall) / (albedo_mod_snow_aging * 24.0))
        alphaMod = alphaSnow + (albedo_ice - alphaSnow) * \
                               np.exp((-1.0*h) / (albedo_mod_snow_depth / 100.0))
    
    else:
    
        # If no snow cover than set albedo to ice albedo
        alphaMod = albedo_ice


    return alphaMod


### idea; albedo decay like (Brock et al. 2000)? or?
### Schmidt et al 2017 >doi:10.5194/tc-2017-67, 2017 use the same albedo parameterisation from Oerlemans and Knap 1998 with a slight updated implementation of considering the surface temperature?

'''
    OR after
    Bougamont, M., Bamber, J. L. and Greuell, W.: A surface mass balance model for the Greenland Ice Sheet, Journal of Geophysical Research: Earth Surface, 110(F4), doi:10.1029/2005JF000348, 2005.
    
    "In our model we represent snow metamorphism by parameterizing albedo as a function of the age of the snow. The effect of aging and of the presence of a thin layer of fresh snow on the albedo value can be modeled using exponential functions to insure a smooth transition between different states [Oerlemans and Knap, 1998]. Similarly, the influence of a water layer at the surface can be parameterized using an exponential function [Zuo and Oerlemans, 1996]. The albedo calculation used here and detailed next is modified from those two studies." p.3
    
    "we use an exponential decay [Zuo and Oerlemans, 1996; Oerlemans and Knap, 1998] to combine the effect of age and snow temperature" p.3    
'''
    