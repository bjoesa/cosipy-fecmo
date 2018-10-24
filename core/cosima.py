#!/usr/bin/env python

'''
    Core module of COSPIY

    Main routine of COSIPY.
'''

import numpy as np
from datetime import datetime
import logging
import os.path
import pandas as pd

from modules.dry_densification import dry_densification     # TODO change back to densification module after dev
from modules.densification_tester import test_densification
from modules.densification import wet_densification

from modules.albedo import updateAlbedo, updateAlbedo_dev
from modules.roughness import updateRoughness
from modules.heatEquation import solveHeatEquation
from modules.heatEquation_lagrange import solveHeatEquation_lagrange
from modules.surfaceTemperature import update_surface_temperature
from modules.penetratingRadiation import penetrating_radiation
#from modules.percolation import percolation
from modules.percofreeze import percolation_refreezing
from modules.precipitation_input import split_precipitation

from constants import *
from config import *
import core.grid as grd
from core.input_data_variables import read_input, init_layer_two
from postprocessing.export import varInit, varStore, write_to_netcdf, write_output_1D, write_to_csv
from postprocessing.visualization import pltTimeseries


def cosima():

    ''' COSPIY main routine '''
    #start_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())
    
    # create logger
    log = logging.getLogger(__name__)
    log.info('Start cosima...with input:' + str(input_netcdf))
    
    ''' Initialization '''

    # read input data
    wind_speed, solar_radiation, temperature_2m, relative_humidity, precipitation, \
    air_pressure, cloud_cover, initial_snowheight = read_input()
    
    # split total precipitation into rain [mmWE] and snowfall [m and mmWE] based on a density vs. temperature relation
    prec_file = 'input/precipitation_separated_input.csv'
    if os.path.isfile(prec_file):  
        log.info('Import split precipitation from csv...')
        df = pd.read_csv(prec_file)
        rain = df['rain[mm]']
        snowfall = df['snowfall[m]']
        snowfall_density = df['snowfall_density[kgm3]']
        snowfall_mmWE = df['snowfall[mmWE]']
    else:
        rain, snowfall, snowfall_density, snowfall_mmWE = split_precipitation(precipitation[:], temperature_2m[:])
    
    hours_since_snowfall = 0
    
    # Init layers - inital snow height trigger the top layering
    layer_heights, layer_densities, layer_temperature, liquid_water_content = \
        init_layer_two(initial_snowheight, temperature_2m[0])

    log.info('Initial snow height: %s' % str(initial_snowheight))

    # Initialize grid, the grid class contains all relevant grid information
    GRID = grd.Grid(layer_heights, layer_densities, layer_temperature, \
                    liquid_water_content, debug_level)
        
    GRID.update_grid(merging_level)

    # inital mass balance
    #mass_balance = 0
   
    ''' Time loop '''
    
    # TODO spinup: A Time loop before the official time loop, 
    # or is a mission start time -7a enough?

    for t in range(tstart, tend, 1):
    
        ''' Add snowfall ''' 
        # integrate the new snow density here and add a rain variable 
        # which triggers a new module (Barrys cryosphere book) - the rain 
        # module can at the beginning use rain as runoff/lwc input for the 
        # sfc layer until lwc threshold is reached (bucket) and later 
        # percolate the liquid water e.g. with a complete bucket scheme, 
        # which maybe simulates pipes etc.
        # This method also allows to use total precipitation as input
        
        log.info('New loop # ' + str(t))
        log.info('Number of layers: ' + str(GRID.nnodes) + '\n')

        runoff = 0.
        
        if snowfall[t] > 0.0:
            # TODO: Better use weq than snowheight
            log.info('Snowfall: ' + str(snowfall[t]) + ' [m]' + ' | snowfall mmWE: ' + str(snowfall_mmWE[t]))
            log.info('Snowfall density: ' + str(snowfall_density[t]) + ' [kg/m³]')
            log.info('Temperature: ' + str(temperature_2m[t]) + ' [K]')

            # Add a new snow node on top
            #GRID.add_node(float(snowfall[t]), density_fresh_snow, float(temperature_2m[t]), 0)
            GRID.add_node(float(snowfall[t]), snowfall_density[t], float(temperature_2m[t]), 0)
            GRID.merge_new_snow(merge_snow_threshold)  # TODO too much layer merge?

        #if rain[t] > 0.0:
            # raise liquid water content
            
        ''' 
            switch for test purposes 
        '''
        
        if switch_for_test == 0:
            log.warning('For densification test purposes all other modules are set off.') 
        else:
        
            if snowfall[t] < 0.005:
                hours_since_snowfall += dt / 3600.0
            else:
                hours_since_snowfall = 0

            # -------------------------
            log.info('Surface Model...')
            # -------------------------

            # Calculate albedo and roughness length changes if first layer is snow
            if albedo_scheme == 1:
                alpha = updateAlbedo_dev(GRID, hours_since_snowfall)
            else:
                alpha = updateAlbedo(GRID, hours_since_snowfall)
            log.debug('Albedo:' + str(alpha))

            # Update roughness length
            z0 = updateRoughness(GRID, hours_since_snowfall)
            log.debug('Roughness length:' + str(z0))

            # Merge grid layers, if necessary --> important for heatEquation
            GRID.update_grid(merging_level)

            # Solve the heat equation
            if (t == 0):
                log.warning('The heat equation tends to be unstable, the amount of while loops will suddenly increase. Configure c_stab with care!')

            if (lagrange == 1):
                cpi = solveHeatEquation_lagrange(GRID, dt)
            else:
                cpi = solveHeatEquation(GRID, dt)

            log.info('Escaped heat!')
            log.debug('Specific heat: ' + str(cpi) + ' [J Kg-1 K-1]')

            # Find new surface temperature
            #log.debug('Old surface temperature: ' + str(GRID.get_T_node(0)) + ' [K]')

            fun, surface_temperature, lw_radiation_in, lw_radiation_out, sensible_heat_flux, latent_heat_flux, \
                ground_heat_flux, sw_radiation_net, rho, Lv, Cs, q0, q2, qdiff, phi \
                = update_surface_temperature(GRID, alpha, z0, temperature_2m[t], relative_humidity[t], cloud_cover[t], air_pressure[t], solar_radiation[t], wind_speed[t])

            #log.debug('New surface temperature: ' + str(GRID.get_T_node(0)) + ' [K]')

            # Surface fluxes [m w.e.q.]
            if GRID.get_T_node(0) < zero_temperature:
                sublimation = max(latent_heat_flux / (1000.0 * lat_heat_sublimation), 0) * dt
                deposition = min(latent_heat_flux / (1000.0 * lat_heat_sublimation), 0) * dt
                evaporation = 0
                condensation = 0
            else:
                evaporation = max(latent_heat_flux / (1000.0 * lat_heat_vaporize), 0) * dt
                condensation = min(latent_heat_flux / (1000.0 * lat_heat_vaporize), 0) * dt
                sublimation = 0
                deposition = 0

            log.debug('Surface fluxes [m w.e.q.]:\nsub: ' + str("%.8f" % sublimation) + '\ndep:' + str("%.8f" % deposition) + '\neva:' + str("%.8f" % evaporation) + '\ncon:' + str("%.8f" % condensation))

            # -------------------------
            log.info('Coupled Surface-Subsurface Model...')
            # -------------------------

            # Melt energy in [m w.e.q.]
            melt_energy = max(0, sw_radiation_net + lw_radiation_in + lw_radiation_out - ground_heat_flux -
                              sensible_heat_flux - latent_heat_flux)  # W m^-2 / J s^-1 ^m-2
            melt = melt_energy * dt / (1000 * lat_heat_melting)  # m w.e.q. (ice)
            # TODO have a look into Benn and Evans (2010:Ch.2.2.1,p.23): How much energy is needed to melt or refreeze amounts of ice/water...

            log.debug('Melt [m w.e.q.]:  ' + str("%.14f" % melt) + '\nMelt energy [W m^-2 / J s^-1 ^m-2]:  ' + str("%.14f" % melt_energy)) 

            log.debug('\u03C1 sfc (kg m^-3): ' + str(GRID.get_rho_node(0)))
            log.debug('Layer heigt  sfc (m): ' + str(GRID.get_hlayer_node(0)))

            # Remove melt height from surface and store as runoff (R) TODO solve runoff in a better way
            runoff = GRID.remove_melt_energy(melt + sublimation + deposition + evaporation + condensation)

            log.debug('\u03C1 sfc (kg m^-3): ' + str(GRID.get_rho_node(0)))
            log.debug('Layer heigt  sfc (m): ' + str(GRID.get_hlayer_node(0)))

            # Merge first layer, if too small (for model stability)
            GRID.merge_new_snow(merge_snow_threshold)

            # Account layer temperature due to penetrating SW radiation - updates GRID
            log.debug('swnet: ' + str("%.6f" % sw_radiation_net))
            #log.debug('Old temperature: ' + str(GRID.get_T()) + ' (K)')

            penetrating_radiation(GRID, sw_radiation_net, dt)

            #log.debug('New temperature: ' + str(GRID.get_T()) + ' (K)')

            # TODO: Percolation, fluid retention (LWC) & refreezing of melt water
            # and rain - updates GRID
            # TODO have a look into Benn and Evans (2010:Ch.2.2.1,p.23): How much energy is needed to melt or refreeze amounts of ice/water...

            if rain[t] + melt > 0.:         
            
                log.debug('rain: ' + str(rain[t]))
                log.debug('melt: ' + str(melt))

                percolation_refreezing(GRID, rain[t], melt, runoff, dt)

                #if percofreeze == 1:
                #    percolation_refreezing(GRID, rain[t], melt, dt)
                #else:
                #    runoff = percolation(GRID, rain[t], melt, runoff, dt)

            else:
                log.debug('Nothing percolated...')

            '''
            # What is this nodes_melting = np.zeros(GRID.number_nodes) stuff in core_1D?

            # todo Percolation, fluid retention (liquid_water_content) & refreezing of melt water
            # and rain

            ### when freezing work:
            nodes_freezing, runoff = percolation(GRID, melt, dt)

            # sum subsurface refreezing and melting
            freezing = np.sum(nodes_freezing)
            melting = np.sum(nodes_melting)

            '''

        ''' Densification '''
        ''' TODO
        if rain[t] + melt + submelt == 0.:
            dry_densification
        else:
            wet densification
        '''
        if GRID.nnodes > 2:

            if (densification_scheme == 0):    
                #log.debug('Dry densification...')
                dh_firn_grid, dh_firn = dry_densification(GRID, t, dt)            
            elif (densification_scheme == 1):
                #log.debug('Wet densification...')
                dh_firn_grid, dh_firn = wet_densification(GRID, t)
            elif densification_scheme == 2:
                dh_firn_grid, dh_firn = test_densification(GRID, t, dt)
            else:
                if (t % 10 == 0):
                    log.info('No densification...')
                #else:
                #   log.warning('Something`s wrong with densification config.')            
                for i in range(GRID.nnodes):
                    dh_firn_grid[i] = 0.
                dh_firn = 0
        
        else:
            for i in range(GRID.nnodes):
                dh_firn_grid[i] = 0.
            dh_firn = 0.

        ''' merge grid '''
        GRID.update_grid(merging_level)
        
        ''' calculate mass balance [m w.e.] '''
        #mass_balance = (snowfall[t]*0.25) - (melt + melting - freezing + sublimation + deposition + evaporation + condensation)
            
        '''save section'''
        # stack 2D arrays -- store timeseries TODO: external 2D variable store
        if t == tstart:
            ''' initialize arrays'''
            dh_firn_grid_list, dh_firnall, Rhoall_list, layer_thickness = varInit(GRID, t,
                                                                  dh_firn,
                                                                  dh_firn_grid)
        else:
            ''' append time series variable to 2D arrays'''
            dh_firn_grid_list, dh_firnall, Rhoall_list, layer_thickness = varStore(GRID,
                                                                   t, dh_firn,
                                                                   dh_firnall,
                                                                   dh_firn_grid,
                                                                   dh_firn_grid_list,
                                                                   Rhoall_list, layer_thickness)

        log.info('Number of layers: ' + str(GRID.nnodes))
        log.info('Loop ends # ' + str(t) + '\n --------------')
        
    #expTimeseries(Liall, Loall, Hall, Lall, Ball, T0all, SWall, Alphaall,
    #             snowHeightall, dh_firnLayers_list, dh_firnall, Rhoall_list)

    #sh = all layers with density <550 ?

    #write_to_netcdf(dh_firn_grid_list, dh_firnall, Rhoall_list) #, sh)
    if save_csv == 1:
        write_to_csv(dh_firn_grid_list, dh_firnall, Rhoall_list, layer_thickness) # sh

    pltTimeseries(GRID, dh_firnall, snowfall[tstart:tend], 
                  dh_firn_grid_list,tstart,tend, temperature_2m[tstart:tend], 
                  rain[tstart:tend], snowfall_density[tstart:tend], snowfall_mmWE[tstart:tend])
    
    GRID.info()
    
    log.info('Sum of firn densification [m]: ' + str(np.sum(dh_firnall)))
    log.info('Sum of firn densification [m]: %f \n' % np.sum(dh_firnall))
    log.info('Loops done: ' + str(tend - tstart) + ' = ' + str(int((tend - tstart) * dt/3600)) + ' h = ' + str((tend - tstart) * dt/3600/24) + ' d')
    log.info('Modelled hours: ' + str(int((tend - tstart) * dt/3600)))
    log.info('Modelled days: ' + str(int((tend - tstart) * dt/3600/24)))

    if debug_level == 0:
        print ('Sum of firn densification [m]: ', str(np.sum(dh_firnall)))
    
    print ('\n ----> Thank you for travelling with C O S I P Y \__OvO__/ <------\n')
    print ('+++++ Which should be more the >> Coupled Firn Densification Python Model - COFiDeM or COFiDePyM or CoFiPyM << +++++\n')
