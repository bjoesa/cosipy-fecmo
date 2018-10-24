'''
    Export variables to timeline arrays and store to csv
''' 

import xarray as xr
import numpy as np
from datetime import date
from config import input_netcdf, output_netcdf, study_site

# for 2D export
import pandas as pd


def write_to_csv(dh_firn_grid_list, dh_firnall, Rhoall_list, layer_thickness):  #, sh):

    ''' store arrays after tend to textfile (result export to external file) '''

    #today = date.today()

    # TODO be sure with the transpose .T stuff ! or save both :)

    # thickness of layers at time step
    layer_thick_df = pd.DataFrame(layer_thickness, index=None, columns=None)
    layer_thick_df_col = layer_thick_df.T
    layer_thick_df.to_csv('output/layer_thickness_2D_row.csv', index=False, header=False)
    layer_thick_df_col.to_csv('output/layer_thickness_2D_col.csv', index=False, header=False)

    # export 2D density profiles (append list to list)
    Rhoall_df = pd.DataFrame(Rhoall_list, index=None, columns=None)
    Rhoall_df_col = Rhoall_df.T
    Rhoall_df.to_csv('output/density_profile_2D_row.csv', index=False, header=False)
    Rhoall_df_col.to_csv('output/density_profile_2D_col.csv', index=False, header=False)

    # export 2D dhdt_firn of every layer (append list to list)
    dh_firnLayers_df = pd.DataFrame(dh_firn_grid_list, index=None,
                                    columns=None)
    dh_firnLayers_df_col = dh_firnLayers_df.T
    dh_firnLayers_df.to_csv('output/dh_firn_2D_row.csv', index=False, header=False)
    dh_firnLayers_df_col.to_csv('output/dh_firn_2D_col.csv', index=False, header=False)

    # export sum dhdt firn per timestep
    f = open('output/dh_firn_1D.csv', 'w')
    f.write('dh_firnall[m]\n')
    for item in dh_firnall:
        f.write("{:.4f}\n".format(item))  # Python 3
    f.close()
    
    ## various one column arrays in one file, comma separated
    #output = ""
    #for r in zip(snowfall, rain, snowfall_density, snowfall_mmWE, precipitation, temperature):
    #    output += "{:.8f}".format(float(r[0])) + " , " + "{:.8f}".format(float(r[1])) + " , " + "{:.1f}".format(float(r[2])) + " , " + "{:.8f}".format(float(r[3])) + " , " + "{:.8f}".format(float(r[4])) + " , " + "{:.2f}\n".format(float(r[5]))
    #f2 = open('_test_env/precipitation_separated_input.csv', 'w')
    #f2.write('snowfall[m] , rain[mm] , snowfall_density[kgm3] , snowfall[mmWE] , total_precipitation[mm] , temperature[K]\n')
    #for item in output:
    #    f2.write(item)
    #f2.close()

