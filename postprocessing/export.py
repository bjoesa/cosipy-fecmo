'''
    Export variables to timeline arrays and store to DataArray, csv AND/OR NetCDF
''' 

import xarray as xr
import numpy as np
from datetime import date
from config import input_netcdf, output_netcdf, study_site, tend, tstart

# for 2D export
import pandas as pd

''' 
    ----------------------------------------------------------
    INTERNAL ARRAY HANDLING AND EXPORT PREPARATION 
    ----------------------------------------------------------
'''

def varInit(GRID, t, dh_firn, dh_firnLayers):

    # TODO the size of the output array has to be adapted
    # TODO+ tend is wrong, should be more sth like len(tend - tstart)

    ''' initialize arrays (export preparation) '''
    t_range = tend - tstart
    dh_firnall = dh_firn

    dh_firnLayers_array = np.array(dh_firnLayers)
    dh_firnLayers_list = [[] for i in range(t_range)]  # initial list size
    dh_firnLayers_list[0] = dh_firnLayers_array

    Rhoall_array = np.array(GRID.get_rho())
    Rhoall_list = [[] for i in range(t_range)]  # initial list size
    Rhoall_list[0] = Rhoall_array

    layer_thick_now = np.array(GRID.get_hlayer())
    layer_thickness = [[] for i in range(t_range)]
    layer_thickness[0] = layer_thick_now

    return dh_firnLayers_list, dh_firnall, Rhoall_list, layer_thickness


def varStore(GRID, t, dh_firn, dh_firnall, dh_firnLayers, dh_firnLayers_list,
             Rhoall_list, layer_thickness):

    ''' append vars to arrays (export preparation) '''
    idx = t - tstart

    # density profile
    Rhoall_array = np.array(GRID.get_rho())
    Rhoall_list[idx] = Rhoall_array  # appends rho profile to initialized list

    # sum of dhdt per time step
    dh_firnall = np.append(dh_firnall, dh_firn)

    # dhdt firn of each lyr to prev. step
    dh_firnLayers_array = np.array(dh_firnLayers)
    dh_firnLayers_list[idx] = dh_firnLayers_array

    # thickness of each layer per time step
    layer_thick_now = np.array(GRID.get_hlayer())
    layer_thickness[idx] = layer_thick_now

    return dh_firnLayers_list, dh_firnall, Rhoall_list, layer_thickness

''' 
    ----------------------------------------------------------
    REAL EXPORT SECTION 
    ----------------------------------------------------------
'''

def write_to_csv(dh_firn_grid_list, dh_firnall, Rhoall_list, layer_thickness):  #, sh):

    ''' store arrays after tend to textfile (result export to external file) '''

    #today = date.today()
    output_name = 'output/' + str(study_site)
    end_row = '_row.csv'
    end_col = '_col.csv'
    # TODO be sure with the transpose .T stuff ! or save both :)

    # thickness of layers at time step
    layer_thick_df = pd.DataFrame(layer_thickness, index=None, columns=None)
    layer_thick_df_col = layer_thick_df.T
    n_thick = output_name + '_layer_thickness_2D'
    layer_thick_df.to_csv(str(n_thick+end_row), index=False, header=False)
    layer_thick_df_col.to_csv(str(n_thick+end_col), index=False, header=False)

    # export 2D density profiles (append list to list)
    Rhoall_df = pd.DataFrame(Rhoall_list, index=None, columns=None)
    Rhoall_df_col = Rhoall_df.T
    n_rhoall = output_name + '_density_profile_2D'
    Rhoall_df.to_csv(str(n_rhoall+end_row), index=False, header=False)
    Rhoall_df_col.to_csv(str(n_rhoall+end_col), index=False, header=False)

    # export 2D dhdt_firn of every layer (append list to list)
    dh_firnLayers_df = pd.DataFrame(dh_firn_grid_list, index=None,
                                    columns=None)
    dh_firnLayers_df_col = dh_firnLayers_df.T
    n_firnlayers = output_name + '_dh_firn_2D'
    dh_firnLayers_df.to_csv(str(n_firnlayers+end_row), index=False, header=False)
    dh_firnLayers_df_col.to_csv(str(n_firnlayers+end_col), index=False, header=False)

    # export sum dhdt firn per timestep
    n_dhdtfirn = output_name + '_dh_firn_1D.csv'
    f = open(n_dhdtfirn, 'w')
    f.write('dh_firnall[m]\n')
    for item in dh_firnall:
        f.write("{:.8f}\n".format(item))  # Python 3
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


def write_to_netcdf(dh_firn_grid_list, dh_firnall, Rhoall_list):  #, sh):

    ''' store arrays after tend to netcdf (result export to external file) '''

    today = date.today()

    # dhdt_firn of each lyr to/until prev. step
    dh_firn_grid_list = xr.DataArray(dh_firn_grid_list)
    # sum of firn at time step
    dh_firnall = xr.DataArray(dh_firnall)
    # density profile
    Rhoall_list = xr.DataArray(Rhoall_list)
    # snow height at time step
    #sh = xr.DataArray(sh)
    data = xr.Dataset({
                    'dh_firn_grid_alltime':dh_firn_grid_list,
                    'dh_firn_sum_timestep':dh_firnall,
                    'density_profile_timestep':Rhoall_list,
                    #'sh':sh
                    }
                    )
    data.attrs['TITLE'] = 'COSIPY 1D results'
    data.attrs['CREATION_DATE'] = str(today)
    data.attrs['STUDY_SITE'] = str(study_site.replace(' ','').lower())
    data.to_netcdf(output_netcdf, mode='w')


def write_output_1D(lw_in,lw_out,h,lh,g,tsk,sw_net,albedo,sh):

    ''' append climatic arrays after tend to netcdf (result export to external file) '''

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
    data.to_netcdf(output_netcdf, mode='a')
