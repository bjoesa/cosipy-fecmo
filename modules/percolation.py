import numpy as np
import logging

from constants import *
from config import *


def percolation(GRID, rain, melt, runoff, dt):

    """ Percolation and refreezing of melt water and rain through the snow- and firn pack """

    log = logging.getLogger(__name__)
    log.info('Percolation is running...')
    
    runoff = 0
    
    '''
        1. percolate and refreeze melt water
        2. percolate and refreeze rain --> REEFREZING PROCES ???
        3. Temperature rises when water refreezes (phase change): latent heat of fusion L_f [DeWalle and Rango, 2008: Ch.1.4.2, p.17]
            Changes in phase involve energy transfer expressed as latent heats in MJ kg^-1: Liquid to solid +0.334
            L_f in MJ kg^-1 = −1 * 10**(-5) T**2 + 0.0019T + 0.3332, −50 °C ≤ T ≤  0°C 
    '''
    for t in range(0, GRID.nnodes, 1):
    
        # if layer is ice_density, liquid = runoff
        # if layer is < density 
        # and liquid is less than layer can hold, liquid is added to lwc and if T remains lower than zeroT in refreezing process, lwc refreezes to ice (!)(a fraction stays in the layer) in/above/below the layer (ice lense) and raises the layer temp  [if refreezed liquid produces a new layer, we need a layer height, the same T as layer where it comes from, lwc = 0., density = 917.] 
        
        # if layer would exceed zeroT, rest liquid is stored as lwc 
        # and liquid is more than layer can hold, a storable part is added to refreezing process OR to the lwc and the liquid_rest is passed to the next layer and so on
        
        # TODO take account of percolation velocity 0.0006 m s^-1
        
        meter_percolation_velocity_per_time_step = dt * percolation_velocity / 3600
        
        
        while refreezing:
            
            temp_profile = GRID.get_T()
            rho_profile = GRID.get_rho()
            h_profile = GRID.get_h()
            
            #latent_fused_temp = -1 * 10**(-5) * GRID.get_T_node(t)**2 + (0.0019*GRID.get_T_node(t)) + 0.3332
            #new_temp_node = GRID.get_T_node(t) + latent_fused_temp
            
            GRID.set_T_node(t, new_temp_node)
            
            # add node
            # calc height of node
                # if lwc is in m w.e.q
                # liquid water fraction depends on layers mass
                # lwc_rest = lwc of parent layer - liquid_water_fraction[dM = V * rho = A * dh * rho ]
                
            # TODO
            lwc_rest = where_do_i_come_from
            
            h_ice_lense = lwc_rest / GRID.get_rho_node(t) / water_density

            # add node or layer density
            if h_ice_lense > merge_snow_threshold:
                
                # TODO reduce heigth of parent layer, reduce lwc
                GRID.set_h_node(t, GRID.get_h_node(t)-h_ice_lense)            
                GRID.add_node_idx(t, h_ice_lense, ice_density, new_temp_node, 0)
                
            else:
                # raise rho of parent layer by the height fraction: h_ice_lense/GRID.get_h_node(t)*100.
                old_density_node = GRID.get_rho_node(t)
                GRID.set_rho_node(t, old_density_node + (h_ice_lense/GRID.get_h_node(t)*100) )
                
            
            
            refreezing = False
            
            
    # percolate and refreeze melt_water
    if melt != 0:
        melt_water = True
    else:
        melt_water = False
    
    while melt_water:
    
        # do it!
        required_stuff = ...
        
        melt_rest = melt - melt_required 
         
        if ...:
            melt_water = True
        else:
            melt_water = False
            
    
    # percolate and refreeze rain
    if rain != 0:
        rain_water = True
    else:
        rain_water = False
    
    while rain:
    
        # do it!
        
        if ...:
            rain = True
        else:
            rain = False
            
        
    
        
    
    if rain > 0:
    
        if GRID.get_rho_node(0) < snow_ice_threshold:
            # maximum amount of liquid water content which the first layer can hold - when the bucket is full?
            max_amount_possible_water_content =  GRID.get_LWC_node(0)                                                                                           'TODO'
            
            # add rain to first layer
            if (GRID.get_LWC_node(0) + rain) < max_amount_possible_water_content:
                GRID.set_LWC_node(0, GRID.get_LWC_node(0) + rain)
                
            elif (GRID.get_LWC_node(0) + rain) > max_amount_possible_water_content:
                # calc overflow/surplus
                overflow = GRID.get_LWC_node(0) + rain - max_amount_possible_water_content
                GRID.set_LWC_node(0, GRID.get_LWC_node(0) + rain - overflow)

                # add overflow to next layer
                # test how much is possible
                max_amount_possible_water_content = GRID.get_LWC_node(1)
                
                if (GRID.get_LWC_node(1) + overflow) < max_amount_possible_water_content:
                
                # add amount which is possible
                GRID.set_LWC_node(1, overflow)
            
            for idx in range(1, GRID.nnodes, 1):
                
                if GRID.get_rho_node(idx) < snow_ice_threshold:
                    
                    # amount of water which has to stay in the layer
                    min_lwc = GRID.get_LWC_node[idx] .... liquid_water_fraction                                                     'TODO'
                    
                    if GRID.get_LWC_node(idx) < min_lwc:
                        log.warning('Liquid water content was below irreducable water content.')
                        GRID.set_LWC_node(idx)
                    
                    water_content_present = GRID.get_LWC_node(idx)
                    
                    # maximum amount of liquid water content which the snow/firn layer can hold - when the bucket is full?
                    max_amount_possible_water_content = 
                    
        else:
            # first layer is impermeable
             runoff += rain
             
    return runoff
        