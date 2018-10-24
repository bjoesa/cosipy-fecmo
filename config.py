#!/usr/bin/env python

'''
 This is the COSIPY configuration (init) file.
 Please make your changes here.
'''

'''
    DENSIFICATION TEST ENVIRONMENT
    swith off all other modules for test purposes
    off == 0
'''
switch_for_test = 0
cross_section_area = 1              # GRID node area [m²]

''' i/o data '''
input_netcdf = './input/cosipy_vestfonna_456masl_79.981_19.563_mar_3h_2000-2014.nc'
output_netcdf = 'output/output_example-1D.nc'
study_site = 'vestfonna'

''' lookup / infos '''
debug_level = 20                    # Control logging: which level should be saved to logfile? 10 (high), 20, 30 (low)
                                
''' time frame '''
# C:\Users\Bjoern Lukas\Documents\SynologyDrive\\skripte\firn_modelling\cosipy-bit\fdm-dev\_test_env\variable_description.txt
tstart = 29224                      # iteration to start       29224
tend = 32144                        # iteration to stop        32144
dt = 3*3600                         # length of timestamp per iteration in seconds

''' Densification scheme '''
densification_scheme = 2            # [0] dry (cold, Herron & Langway, 1980) [default] or 
                                    # [1] wet (multi-temperature/ temperate) densification or
                                    # [2] apply densification test module
                                    # [3] apply no densification at all

''' Albedo scheme '''
albedo_scheme = 0                   # [0] Eva/default; [1] new developed

''' Percolation scheme '''
#percofreeze = 0                    # The default is a basic test version (0). An advanced Percolation, liquid water content and refreezing scheme is in production (1)

''' Heat equation scheme ''' 
lagrange = 1                        # default = 0 = off = anselms code; 1 = lagrange on = tobias code
                                    
''' layer structure '''

temperature_bottom = 268            # bottom temperature [K] - at pore closure

merging_level = 1                   # Merge layers with similar properties:
                                    # 0 = False
                                    # 1 = 5. [kg m^-3] and 0.05 [K]
                                    # 2 = 10. and 0.1

merge_snow_threshold = 0.02         # Minimal height of layer [m]:
                                    # thin layers rise computational needs
                                    # of upwind schemes (e.g. heatEquation)

#number_layers = 10                 # number of inital layers TODO avoid variable

''' snow profile properties (e.g. taken from snow pit) '''
rho_top = 250.                          # surface layer density
#rho_bottom = 600.                      # density of snow/firn transition layer

initial_snow_layer_heights = 0.1        # Initial splitting of snow layering heights
initial_glacier_layer_heights = 1.0     # Initial firn and glacier ice layer heights
initial_glacier_height = 7.0            # total domain height (snow+firn)  # from Fürst et al. 2017 ?  --> TODO expect variation in distributed model runs !

''' modelling specifics '''
c_stab = 0.2                        # Courant–Friedrichs–Lewy (CFL) condition for the heatEquation and percolation (TODO does it make sense to have both in one variable?)
''' TODO
In which direction one should go when it is to warm resp. not enough snow? >0.3 ???? 0.5 is even slow!
for Eva's input, 0.3 ends up in endless while loops 
(curr_t is increased to slow, because dt_use is very small)
solution: increase time steps (dt_use) and avoid heatEqatuibn while loops when rho[0] == 917 and reduce densification speed at desnities > 830
OR 
one has to raise merging level (hardly an effect, neither on speed, nor on layering)
'''

''' Save results '''
save_csv = 1
#save_ncf = 0  # TODO establish - see export.py and _test_env/ or nc_handler

''' plot results '''
plots = 1                           # save plots of e.g. firn compaction change rate, density profiles, layer heights, temperature profiles
showplot = 0                        # show up plots after last run?
