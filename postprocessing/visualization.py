#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib.pylab as plt
import numpy as np
import logging
from os import path, makedirs, rename, listdir
import os
from config import *

def pltTimeseries(GRID, dh_firnall, snowfall, dh_firnLayers_list,tstart,tend,temperature, rain, snowfall_density, snowfall_mmWE):

    # create logger
    log = logging.getLogger(__name__)
    log.info('Plotting...')
    
    # Files of last run are saved as old, 
    if not path.exists('./output/plots'):
        log.debug('Path ./output/plots created.')
        makedirs('./output/plots')
    else:
        for filename in os.listdir("./output/plots"):
            if filename.endswith("_old.png"):
                os.remove('./output/plots/' + filename)
        
        for filename in os.listdir("./output/plots"):
            file_new = './output/plots/' + filename[:-4] + '_old.png'
            file_old = './output/plots/' + filename
            os.rename(file_old, file_new)
                
        log.debug('Path ./output/plots exists.')
        

    ''' Firn compaction in meter at every time step '''
    if (plots == 1):
        plt.plot(dh_firnall, '.',ms=3)
        plt.title('Firn compaction change rate (full column) [m]\nper time step (%s:%s)'%(tstart,tend))
        plt.grid(True)
        plt.ylabel("Change sum [m] at time step [idx]")
        plt.xlabel("Time step [idx]")
        
        steps = tend - tstart

        if (tstart > 0):
            stepper = int(tend/tstart)
            ranger = []

            if stepper < 100:
                stepper = stepper * 50
  
            for i in range(0,len(snowfall[:]), stepper):
                ranger.append(i)

            ranger.append(ranger[len(ranger)-1] + stepper)
            aranger = np.arange(tstart,tend,stepper)
            aranger = np.append(aranger,aranger[len(aranger)-1] + stepper)
            plt.xticks(ranger, aranger, rotation=90)
            
            plt.text(stepper, np.min(dh_firnall)*0.85, 'tstart: %s\ntend: %s\nsteps: %s' % (tstart,tend,steps),fontsize=8)
            
        else:
            plt.text(1, min(dh_firnall)*0.85, 'tstart: %s\ntend: %s\nsteps: %s' % (tstart,tend,steps),fontsize=8)
        
        plt.tight_layout()

        plt.savefig('output/plots/Column_firn_compaction_rate.png')

        if (showplot == 1):
            plt.show()

        plt.close()

    ''' Density profile of last (t_end) modelled profile '''
    if (plots == 1):
        y = range(1, GRID.nnodes+1)
        #print x
        plt.plot(GRID.get_rho(), y, '.', color='black', ms=10, label="Average density COSIPY [kg m^-3]")
        plt.plot(GRID.get_rho(), y, '-', color='black', linewidth=1.0, label="Average density COSIPY [kg m^-3]")
        plt.title('Last (step: %s) density profile $[kg\ m^{-3}]$'%(tend))
        plt.grid(True)
        plt.yticks(y)
        plt.ylabel("Depth node [idx]")
        plt.xlabel("Layer density $[kg\ m^{-3}]$")
        plt.ylim(GRID.nnodes + 1, 0)  # invert y-axis
        plt.xlim(xmin=100, xmax=1000)
        plt.axvline(250, color='g', linestyle='dashed', linewidth=1)
        plt.text(260,max(y)-2,'$250\ kg\ m^{-3}$',rotation=90,color='g')
        plt.axvline(550, color='r', linestyle='dashed', linewidth=1)
        plt.text(560,max(y)-2,'$550\ kg\ m^{-3}$',rotation=90,color='r')
        plt.axvline(830, color='b', linestyle='dashed', linewidth=1)
        plt.text(840,max(y)-2,'$830\ kg\ m^{-3}$',rotation=90,color='b')
        plt.axvline(917, color='y', linestyle='dashed', linewidth=1)
        plt.text(927,max(y)-2,'$917\ kg\ m^{-3}$',rotation=90,color='y')

        plt.savefig('output/plots/Layer_densities_tend.png')

        if (showplot == 1):
            plt.show()

        plt.close()
        
    ''' Layer heights (profile) of last (t_end) modelled time step/ profile '''
    if (plots == 1):
        x = range(1, GRID.nnodes+1)
        plt.xlim(0, GRID.nnodes+1)  # invert y-axis
        plt.xticks(x)

        plt.plot(x, GRID.get_hlayer(), '.', color='black', ms=10)
        plt.plot(x, GRID.get_hlayer(), '-', color='black', linewidth=1.0)
        plt.bar(x, GRID.get_hlayer())
        
        plt.title('Last (step: %s) layer heights profile [m]'%(tend))
        plt.ylabel("Height [m]")
        plt.xlabel("Depth node [idx]")
        plt.grid(True)

        plt.savefig('output/plots/Layer_heights_tend.png')

        if (showplot == 1):
            plt.show()

        plt.close()

    ''' Temperature profile of last (t_end) modelled profile '''
    if (plots == 1):
        y = range(1, GRID.nnodes+1)
        plt.plot(GRID.get_T(), y, '.', color='black', ms=10)
        plt.plot(GRID.get_T(), y, '-', color='black', linewidth=1.0)
        plt.title('Last (step: %s) temperature profile $[K]$'%(tend))
        plt.grid(True)
        plt.yticks(y)
        plt.ylabel("Depth node [idx]")
        plt.xlabel("Layer temperature $[K]$")
        plt.ylim(GRID.nnodes + 1, 0)  # invert y-axis
        mi = (round(float(min(GRID.get_T())),-1))-5
        ma = (round(float(max(GRID.get_T())),-1))+5
        plt.xlim(xmin=mi, xmax=ma)
        plt.axvline(273.15, color='b', linestyle='dashed', linewidth=1)
        
        plt.text(273.5,max(y)-1,'273.15 K',rotation=90,color='b')
        
        plt.savefig('output/plots/Layer_temperature_tend.png')

        if (showplot == 1):
            plt.show()

        plt.close()
        
    ''' Barplot of snowfall '''
    if (plots == 1):
        
        f, ax = plt.subplots(1)
        xdata = range(len(snowfall))
        ydata = snowfall[:]
        ax.plot(xdata, ydata)
        
        my_data = snowfall[:]
        sumsnow = sum(my_data)
        plt.title('Snowfall [m] (sum: (%s:%s): %s m)'%(tstart,tend,sumsnow))

        plt.ylabel("Single solid precipitation events [m]")
        plt.xlabel("Time step [idx]")   # , labelpad=30)
        
        steps = tend - tstart
        plt.text(min(xdata), max(ydata)*0.85, 'tstart: %s\ntend: %s\nsteps: %s\nsum: %s m'%(tstart,tend,steps,sumsnow),fontsize=8)

        if (tstart > 0):
            stepper = int(tend/tstart)
            ranger = []

            if stepper < 100:
                stepper = stepper * 50
  
            for i in range(0,len(snowfall[:]), stepper):
                ranger.append(i)

            ranger.append(ranger[len(ranger)-1] + stepper)
            aranger = np.arange(tstart,tend,stepper)
            aranger = np.append(aranger,aranger[len(aranger)-1] + stepper)
            plt.xticks(ranger, aranger, rotation=90)
            
        plt.tight_layout()

        plt.savefig('output/plots/snowfallplot.png')

        if (showplot == 1):
            plt.show(f)

        plt.close(f)
        
        # Air Temperature plot
        f, ax = plt.subplots(1)
        xdata = range(len(temperature))
        ydata = temperature[:]
        ax.plot(xdata, ydata)
        
        if np.max(ydata) >= 273.16:
            ax.axhline(273.15, color='b', linestyle='dashed', linewidth=1)
            plt.text(min(x),272,'273.15 K',color='black')

        my_data = temperature[:]
        meantemp = np.mean(my_data)
        plt.title('Air temperature (mean: (%s:%s): %s K)'%(tstart,tend,meantemp))

        plt.ylabel("[K]")
        plt.xlabel("Time step [idx]")   # , labelpad=30)
        
        steps = tend - tstart
        plt.text(min(xdata), max(ydata)*0.85, 'tstart: %s\ntend: %s\nsteps: %s\nmean: %s m'%(tstart,tend,steps,meantemp),fontsize=8)

        if (tstart > 0):
            stepper = int(tend/tstart)
            ranger = []

            if stepper < 100:
                stepper = stepper * 50
  
            for i in range(0,len(temperature[:]), stepper):
                ranger.append(i)

            ranger.append(ranger[len(ranger)-1] + stepper)
            aranger = np.arange(tstart,tend,stepper)
            aranger = np.append(aranger,aranger[len(aranger)-1] + stepper)
            plt.xticks(ranger, aranger, rotation=90)
            
        plt.tight_layout()

        plt.savefig('output/plots/air_temperature_plot.png')

        if (showplot == 1):
            plt.show(f)

        plt.close(f)

        
        # plot input with supplots (https://matplotlib.org/examples/pylab_examples/subplots_demo.html#pylab-examples-subplots-demo)
        xtemp = range(len(temperature))
        ytemp = temperature[:]
        
        xsnow = range(len(snowfall))
        ysnow = snowfall[:]
        
        f, axarr = plt.subplots(2, sharex=True)
        axarr[0].plot(xtemp, ytemp, 'r--')
        axarr[0].set_title('Input data (shared X axis)')
        axarr[0].set(ylabel='Air Temperature [K]')
        if np.max(ytemp) >= 273.16:
            axarr[0].axhline(273.15, color='b', linestyle='dashed', linewidth=1)
            axarr[0].text(min(x),272,'273.15 K',color='black')
        axarr[1].plot(xsnow, ysnow, 'b--')
        #plt.ylabel("Snowfall [m]")
        axarr[1].set(ylabel="Snowfall [m]")
        plt.xlabel("Time step [idx]") 
       
        plt.tight_layout()
        plt.savefig('output/plots/input_data_plot.png')
        
        if (showplot == 1):
            plt.show()
            
        plt.close()
        
        '''
        # plot additional input with supplots - order T, snowfall, rain, density, snowfall_mmWE
        xrain = range(len(rain))
        yrain = rain[:]
        
        xsnow = range(len(snowfall))
        ysnow = snowfall[:]
        
        xdens = range(len(snowfall_density))
        ydens = snowfall_density[:]
        
        xsfmm = range(len(snowfall_mmWE))
        ysfmm = snowfall_mmWE[:]
        
        xtemp = range(len(temperature))
        ytemp = temperature[:]        
        
        f, axarr = plt.subplots(5, sharex=True)
        axarr[0].set_title('Input data')
        
        axarr[0].plot(xtemp, ytemp, 'r--')
        axarr[0].set(ylabel='Air Temperature [K]')
        
        if np.max(ytemp) >= 273.16:
            axarr[0].axhline(273.15, color='b', linestyle='dashed', linewidth=1)
            axarr[0].text(min(x),272,'273.15 K',color='black')
            
        axarr[1].plot(xsnow, ysnow, 'b--')
        axarr[1].set(ylabel="Snowfall [m]")
        
        axarr[2].plot(xrain, yrain, 'b--')
        axarr[2].set(ylabel="Rain [mmWE]")
        
        axarr[3].plot(xdens, ydens, 'g--')
        axarr[3].set(ylabel="Density [kg m^{-3}]")
        
        axarr[4].plot(xsfmm, ysfmm, 'b--')
        axarr[4].set(ylabel="Snowfall [mmWE]")
        
        plt.xlabel("Time step [idx]") 
       
        plt.tight_layout(pad=1.08, h_pad=None, w_pad=None, rect=None)
        plt.savefig('output/plots/input_all_data_plot.png')
        
        if (showplot == 1):
            plt.show()
            
        plt.close()
        '''
        