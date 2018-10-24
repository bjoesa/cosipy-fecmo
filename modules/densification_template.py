#!/usr/bin/env python

'''
    Temperatur, Druck (Kompression/Längskontraktion) und Schmelzmetamorphose
'''

import numpy as np
import logging
from constants import *


def test_densification(GRID, t, dt):
    
    log = logging.getLogger(__name__)
    log.info('Test Densification (#2) is running...!')
    
    hlayer_old = GRID.get_hlayer()                                             # copy of firn layer heights t[-1]
    rholayer_old = GRID.get_rho()
    tlayer_old = GRID.get_T()
    lwclayer_old = GRID.get_LWC()

    dh_list = []

    ''' Densify grid per node ''' 
    for grdnode in range(0, GRID.nnodes-1, 1):    # (0, GRID.nnodes, 1):

        log.info('rho[' + str(grdnode) + ']: ' + str(GRID.get_rho_node(grdnode)))
                
        ''' P H Y S I K : Temperatur, Druck und Schmelzmetamorphose '''
        

        
        log.info('rho[' + str(grdnode) + ']: ' + str(GRID.get_rho_node(grdnode)))

        ''' update h, T and LWC '''
        if (GRID.get_rho_node(grdnode) < ice_density):

            ''' update h '''
            # calc firn compaction layer height ratio
            newheight = (rholayer_old[grdnode] / GRID.get_rho_node(grdnode)) * \
               GRID.get_hlayer_node(grdnode)

            log.info('Old height[' + str(grdnode) + ']: ' + str(hlayer_old[grdnode]))
            log.info('New height[' + str(grdnode) + ']: ' + str(newheight))

            GRID.set_hlayer_node(grdnode, newheight)

            ''' T is updated in subsurface MB model '''
            #newtemp = tlayer_old[grdnode]
            #GRID.set_T_node(grdnode, newtemp)

            ''' LWC is updated in subsurface MB model '''
            #newlwc = lwclayer_old[grdnode]
            #GRID.set_LWC_node(grdnode, newlwc)

            #GRID.update_node(grdnode, newheight, rhotmp, newtemp, newlwc)
            # TODO integrate in density solvers above        

        # track dhdt firn of each lyr to prev. step
        dh_list.append(hlayer_old[grdnode] - GRID.get_hlayer_node(grdnode))    

    ''' Prepare for return '''
    
    # difference of cumulative layer height's
    dh_firn = sum(GRID.get_hlayer()) - sum(hlayer_old)

    for i in range(len(dh_list)):
        log.info('dh node[' + str(i) + ']: ' + str(dh_list[i]))

    log.info('dh list (sum): ' + str(sum(dh_list)))
    log.info('dh firn (sum): %f \n' % dh_firn)
    
    return dh_list, dh_firn
