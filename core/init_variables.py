#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    Module to initialize (varInit) and to append to 2D time series arrays
'''

import numpy as np


def varInit(GRID, t, tend, dh_firn, dh_firnLayers):

    ''' initialize arrays'''

    dh_firnall = dh_firn

    dh_firnLayers_array = np.array(dh_firnLayers)
    dh_firnLayers_list = [[] for i in range(tend)]  # initial list size
    dh_firnLayers_list[t] = dh_firnLayers_array

    Rhoall_array = np.array(GRID.get_rho())
    Rhoall_list = [[] for i in range(tend)]  # initial list size
    Rhoall_list[t] = Rhoall_array

    return dh_firnLayers_list, dh_firnall, Rhoall_list


def varStore(GRID, t, dh_firn, dh_firnall, dh_firnLayers, dh_firnLayers_list,
             Rhoall_list):

    ''' append vars to arrays'''

    # density profile
    Rhoall_array = np.array(GRID.get_rho())
    Rhoall_list[t] = Rhoall_array  # appends rho profile to initialized list

    # sum of dhdt per time step
    dh_firnall = np.append(dh_firnall, dh_firn)

    # dhdt firn of each lyr to prev. step
    dh_firnLayers_array = np.array(dh_firnLayers)
    dh_firnLayers_list[t] = dh_firnLayers_array

    return dh_firnLayers_list, dh_firnall, Rhoall_list
