'''
    Splits total precipitation into snowfall [m] and rainfall [mmWE].
'''

import logging
import numpy as np
from math import tanh
from constants import zero_temperature


def split_precipitation(precipitation, temperature):
    
    '''
        splits total precipitation into snowfall [m] and rainfall [mmWE]
    '''
    
    log = logging.getLogger(__name__)
    log.info('Precipiation splitting is running...')
    
    snowfall_mmWE = []      # snowfall in mmWE
    snowfall = []                   # snowfall in meter
    rain = []                          # rain in mmWE
    snowfall_density = []     # in kg m³
    
    for i in range(0, len(temperature),1):
    
        if (zero_temperature + 2) >= temperature[i] > zero_temperature:
            # tangenz hyperbolicus to derive snowfall [mmWE]
            # snow/rain gradient - sinusoidal function - and 
            tanh_ = 0.5 * (-tanh((temperature[i] - (zero_temperature+1)) * 3) + 1)
            snow_temp = (precipitation[i] * tanh_)
            snowfall_mmWE.append(snow_temp)
            snowfall.append(snow_temp/400.)
            rain.append(precipitation[i] - snow_temp)
            snowfall_density.append(400.)
            
        elif zero_temperature >= temperature[i] > 270.:
            
            # only snowfall occurs; SWE[kg m²]/rho[kg m³] = sh [m]   |   kg m² == mmWE
            rain.append(0.)
            snowfall_mmWE.append(precipitation[i])
            snowfall.append(precipitation[i]/250.)
            snowfall_density.append(250.)
            
        elif 270. >= temperature[i] > 268.:
            
            rain.append(0.)
            snowfall_mmWE.append(precipitation[i])
            snowfall.append(precipitation[i]/200.)
            snowfall_density.append(200.)
            
        elif 268. >= temperature[i] > 266.:
            
            rain.append(0.)
            snowfall_mmWE.append(precipitation[i])
            snowfall.append(precipitation[i]/150.)
            snowfall_density.append(150.)
            
        elif 266. >= temperature[i]:
            # If temperature < 266 K, density is always 100
            
            rain.append(0.)
            snowfall_mmWE.append(precipitation[i])
            snowfall.append(precipitation[i]/100.)
            snowfall_density.append(100.)
            
            # TODO extend or change temperature/density relation is simply possible, just add a new elif 
            
        else:
            # If T > 275.15 all precipitation is rain - rain falls if temperature exceeds ~2°C
            rain.append(precipitation[i])
            snowfall_mmWE.append(0.)
            snowfall.append(0.)
            snowfall_density.append(0.)                                   # TODO or constants: water_density = 1000 kg m³?

    # csv export of time series
    ''' rain, snowfall, snowfall_density, snowfall_mmWE '''

    # f = open('input/snowfall_m_input.csv', 'w')
    # f.write('snowfall[m]\n')
    # for item in snowfall:
    #     f.write("{:.12f}\n".format(float(item)))  # Python 3
    # f.close()

    # f = open('input/rain.csv', 'w')
    # f.write('rain[mmWE]\n')
    # for item in rain:
    #     f.write("{:.12f}\n".format(float(item)))  # Python 3
    # f.close()

    # all in one file, comma separated
    output = ""
    for r in zip(snowfall, rain, snowfall_density, snowfall_mmWE, precipitation, temperature):
        output += "{:.8f}".format(float(r[0])) + "," + "{:.8f}".format(float(r[1])) + "," + "{:.1f}".format(float(r[2])) + "," + "{:.8f}".format(float(r[3])) + "," + "{:.8f}".format(float(r[4])) + "," + "{:.2f}\n".format(float(r[5]))
    f2 = open('input/precipitation_separated_input.csv', 'w')
    f2.write('snowfall[m],rain[mm],snowfall_density[kgm3],snowfall[mmWE],total_precipitation[mm],temperature[K]\n')
    for item in output:
        f2.write(item)
    f2.close()
    
    return rain, snowfall, snowfall_density, snowfall_mmWE
    