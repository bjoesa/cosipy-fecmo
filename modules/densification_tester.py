#!/usr/bin/env python

'''
    Temperatur, Druck (Kompression/Längskontraktion) und Schmelzmetamorphose
'''

import numpy as np
import logging
from math import pi, exp

from constants import *
from config import cross_section_area


def test_densification(GRID, t, dt):

    ''' Vertical compression model after Fellin (2013, p. 74 & 78f) and Tipler & Mosca (2015, p. 358) '''
    
    log = logging.getLogger(__name__)
    log.info('Test Densification (#2) is running...!')
    
    # copy of firn layer heights
    hlayer_old = GRID.get_hlayer()
    rholayer_old = GRID.get_rho()
    tlayer_old = GRID.get_T()
    lwclayer_old = GRID.get_LWC()

    dh_list = []

    #log.info('Dichte: ' + str(GRID.get_rho()))

    for grdnode in range(0, GRID.nnodes-1, 1):    # (0, GRID.nnodes, 1):

        ''' Elastizitätsmodul nach [Tipler & Mosca (2015:358)] - wichtig für die Stauchung '''
        E_mpa = 0.1873 * exp(0.0149*GRID.get_rho_node(grdnode))     # MPa
        E_mod = E_mpa * 1000000                                     # convert MPa to N/m²
        #log.info('E-Modul [MPa][' + str(grdnode) + ']: ' + str(E_mpa))
        #log.info('E-Modul [Nm²]' + str(grdnode) + ']: ' + str(E_mod))

        ''' Erweitertes Kompressionsmodell: Setzung der Schneedecke nach [Fellin (2013:78f)] '''
        D = sum(hlayer_old)                            # Gesamtdicke 
        z = sum(hlayer_old[grdnode:len(hlayer_old)])   # Sockeldicke: Dicke des aktuellen + der darunter liegenden Schichten
        #log.info('Gesamtdicke: ' + str(D) + ' || Sockeldicke: ' + str(z) + ' || Diff.: ' + str(D - z) )

        ''' gewichtete mittlere Dichte aller Schichten oberhalb grdnode '''
        gewichtung_oben = 0.
        gewichtung_unten = 0.

        for i in range(0, grdnode + 1, 1):
            #log.info('inner loop: ' + str(i))
            #log.info('inner loop hlayer: ' + str(hlayer_old[i]))
            #log.info('inner loop rholayer: ' + str(rholayer_old[i]))
            daten =  rholayer_old[i] * hlayer_old[i]            # Dichte * Dicke
            #log.info('inner loop DATEN: ' + str(daten))
            gewicht = hlayer_old[i]
            #log.info('inner loop GEWICHT: ' + str(gewicht))
            gewichtung_oben += daten
            gewichtung_unten += gewicht

        #log.info('gew.ob.' + str(gewichtung_oben))
        #log.info('gew.un.' + str(gewichtung_unten))
        rho_s = gewichtung_oben / gewichtung_unten     # gewichtetes Mittel Dichte aller darüberliegenden Schichten
        gamma_s = gravity_acceleration * rho_s         # Wichte des Schnees
        #log.info('Wichte gamma_s: ' + str(gamma_s))
        sigma_z = gamma_s * (D - z)                    # Vertikalspannung
        #log.info('VERTIKALSPANNUNG sigma_z: ' + str(sigma_z))

        ''' Längenänderung '''
        stauchung = sigma_z / E_mod
        delta_length_fellin = stauchung * GRID.get_hlayer_node(grdnode)
        #log.info('Längenänderung (Fellin, 2013) [' + str(grdnode) + ']: ' + str(delta_length_fellin) + ' (m)')

        ''' Update height '''
        newheight_fellin = hlayer_old[grdnode] - delta_length_fellin
        GRID.set_hlayer_node(grdnode, newheight_fellin)
        #log.info('Old height [' + str(grdnode) + ']: %s' % hlayer_old[grdnode])
        #log.info('New height [' + str(grdnode) + ']: %s \n' % GRID.get_hlayer_node(grdnode))

        ''' Track dhdt firn of each lyr to prev. step '''
        dh_list.append(hlayer_old[grdnode] - GRID.get_hlayer_node(grdnode))
        #log.info('dense loop end\n')

        # Densification of pure glacier ice: Cuffey and Paterson (2010, p. 12) --> Trifft zunächst nicht auf 
        # Oberflächennahe (Firn-)Schichten zu...
    
    ''' Difference of cumulative layer height's '''
    dh_firn = sum(GRID.get_hlayer()) - sum(hlayer_old)

    #for i in range(len(dh_list)):
    #    log.info('dh node[' + str(i) + ']: ' + str(dh_list[i]))
    #log.info('dh list (sum): ' + str(sum(dh_list)))
    log.info('dh firn (sum): %.12f \n' % dh_firn)
    
    return dh_list, dh_firn


def tipler_densification(GRID, t, dt):

    ''' simple densification: young modulus (Tipler & Mosca, 2015) '''
    
    log = logging.getLogger(__name__)
    log.info('Kompression. Densification (#2) is running...!')
    
    # copy of firn layer heights
    hlayer_old = GRID.get_hlayer()
    rholayer_old = GRID.get_rho()
    tlayer_old = GRID.get_T()
    lwclayer_old = GRID.get_LWC()

    dh_list = []

    mi = 0.33               # Proportionalitätskonstante (Poissonzahl)

    for grdnode in range(0, GRID.nnodes-1, 1):    # (0, GRID.nnodes, 1):

        ''' Einfache (Eigen-)Kompression nach [Tipler & Mosca (2015:358)]
            Elastizitätsmodul E - wichtig für die Stauchung '''
        E_mpa = 0.1873 * exp(0.0149*GRID.get_rho_node(grdnode)) # MPa
        E_mod = E_mpa * 1000000                                     # convert MPa to N/m²
        log.info('E [MPa][' + str(grdnode) + ']: ' + str(E_mpa))
        log.info('E [Nm²]' + str(grdnode) + ']: ' + str(E_mod))

        ''' Kompressionsmodul - Widerstand des Körpers gegen die Kompression '''
        K_mod = E_mod/(3*(1-2*mi))                  # Kompressionsmodul
        k_press = (3*(1-2*mi))/E_mod                  # Kompressibilität (Kehrwert von K)
        log.info('K[' + str(grdnode) + ']: ' + str(K_mod))
        log.info('k[' + str(grdnode) + ']: ' + str(k_press))
        log.info('rho[' + str(grdnode) + ']: ' + str(GRID.get_rho_node(grdnode)))
                
        ''' Masse '''
        mass = GRID.get_rho_node(grdnode) * cross_section_area * GRID.get_hlayer_node(grdnode)
        F_G = mass * gravity_acceleration
        log.info('Mass[' + str(grdnode) + ']: ' + str(mass) + ' (kg)')
        log.info('Gewichtskraft['  + str(grdnode) + ']: ' + str(F_G) + ' (kg*m/s²)')
        
        ''' Fläche und Spannung '''
        A = (cross_section_area**2)/4 * pi      # (Querschnitts-)Fläche --> RUND !!
        sigma_D = F_G / A                       # Druckspannung in N/m²
        epsilon = sigma_D / E_mod                   # Verformung in längsrichtung: Stauchung [-]
        log.info('DRUCKSPANNUNG sigma_D [N/m²]: ' + str(sigma_D))
        log.info('epsilon: ' + str(epsilon))

        ''' Längenänderung '''
        delta_length = epsilon * GRID.get_hlayer_node(grdnode)
        log.info('Längenänderung[' + str(grdnode) + ']: ' + str(delta_length) + ' (m)')

        ''' Update height '''
        newheight = GRID.get_hlayer_node(grdnode) - delta_length
        GRID.set_hlayer_node(grdnode, newheight)
        log.info('New height[' + str(grdnode) + ']: ' + str(GRID.get_hlayer_node(grdnode)))

        ''' Track dhdt firn of each lyr to prev. step '''
        dh_list.append(hlayer_old[grdnode] - GRID.get_hlayer_node(grdnode))

    ''' Difference of cumulative layer height's '''
    dh_firn = sum(GRID.get_hlayer()) - sum(hlayer_old)

    for i in range(len(dh_list)):
        log.info('dh node[' + str(i) + ']: ' + str(dh_list[i]))

    log.info('dh list (sum): ' + str(sum(dh_list)))
    log.info('dh firn (sum): %f \n' % dh_firn)
    
    return dh_list, dh_firn
