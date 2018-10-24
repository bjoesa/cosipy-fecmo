#!/usr/bin/env python

import numpy as np
import logging
from constants import *


def dry_densification(GRID, t):
    
    hlayer_old = GRID.get_hlayer()                                             # copy of firn layer heights t[-1]
    dh_list = []

    for grdnode in range(0, GRID.nnodes, 1):

        if (t % 10 == 0):
            print ('++ DRY ++', 'Node (dens. loop):', grdnode)
            print (GRID.get_rho_node(grdnode))
            print (GRID.get_hlayer_node(grdnode))
            print (GRID.get_T_node(grdnode))
            print (GRID.get_LWC_node(grdnode))
            
        dh_list.append(hlayer_old[grdnode] - GRID.get_hlayer_node(grdnode))    # track dhdt firn of each lyr to prev. step

    dh_firn = sum(GRID.get_hlayer()) - sum(hlayer_old)                         # difference of cumulative layer height's
    
    return dh_list, dh_firn


def wet_densification(GRID, t):
    
    dh_list = []

    for grdnode in range(0, GRID.nnodes, 1):

        if (t % 20 == 0):
            print ('++ WET ++ WET ++', 'Node (dens. loop):', grdnode)
            print ('Nothing will happen so far, module is in construction.')
            
        dh_list.append(0)

    dh_firn = 0
    
    return dh_list, dh_firn


def test_densification(GRID, t, dt):

    ''' Densification module '''
    
    log = logging.getLogger(__name__)
    log.info('Test Densification (#2) is running...')
    log.debug('  rho sfc:    ' + str(GRID.get_rho_node(0)))
    log.debug('  hgt sfc:    ' + str(GRID.get_hlayer_node(0)))
    log.debug('  lwc sfc:    ' + str(GRID.get_LWC_node(0)))
    log.debug('  temp sfc: ' + str(GRID.get_T_node(0)))
    
    hlayer_old = GRID.get_hlayer()                                             # copy of firn layer heights t[-1]
    rholayer_old = GRID.get_rho()
    tlayer_old = GRID.get_T()
    lwclayer_old = GRID.get_LWC()

    dh_list = []

    ''' Densify grid per node ''' 
    for grdnode in range(0, GRID.nnodes-1, 1):    # (0, GRID.nnodes, 1):

        log.info('rho[' + str(grdnode) + ']: ' + str(GRID.get_rho_node(grdnode)))
                
        ''' find constant for densification mechanism (HL, 376) '''
        if (grdnode == 0):
            a = (GRID.get_hlayer_node(grdnode) * (GRID.get_rho_node(grdnode))) * 0.5
        else:
            a = (GRID.get_hlayer_node(grdnode) * grdnode) * \
            (np.mean(GRID.get_rho()[0:grdnode]))

        #log.debug('a ' + str(a))

        ''' change of overburden pressure and density '''
        if (GRID.get_rho_node(grdnode) < snow_firn_threshold):
            rhotmp = GRID.get_rho_node(grdnode) + K0 * \
                     (np.exp(-E0 / (R * GRID.get_T_node(grdnode)))) \
                     * a * ((ice_density - GRID.get_rho_node(grdnode)) / ice_density)
                     
            log.debug('rho < 550: ' + str(rhotmp))
            
            GRID.set_rho_node(grdnode, rhotmp)
            
        elif (snow_firn_threshold <= GRID.get_rho_node(grdnode) < firn_ice_threshold):
            rhotmp = GRID.get_rho_node(grdnode) + K1 * \
                     (np.exp(-E1 / (R * GRID.get_T_node(grdnode)))) \
                     * a * ((ice_density - GRID.get_rho_node(grdnode)) / ice_density)
            
            log.debug('550 <= rho < 830: ' + str(rhotmp))
            
            GRID.set_rho_node(grdnode, rhotmp)

        elif (firn_ice_threshold <= GRID.get_rho_node(grdnode) < ice_density):
            # rhotmp = GRID.get_rho_node(grdnode) + K1 * \
                     # (np.exp(-E1 / (R * GRID.get_T_node(grdnode)))) \
                     # * a * ((ice_density - GRID.get_rho_node(grdnode)) / ice_density)
                     
            auflast = sum(hlayer_old[0:grdnode])
            log.debug('auflast [m]: ' + str(auflast/10*0.001) + ' at grdnode #: ' + str(grdnode))
            
            # TODO this is a very simple model to slow down the densification process below pore closure layers 
            rhotmp = GRID.get_rho_node(grdnode) + (dt / 3600 * (auflast/10) * 0.001)
            #rhotmp = GRID.get_rho_node(grdnode) + (dt / 3600 * GRID.get_hlayer_node(grdnode) * 0.001)
            log.debug('830 <= rho < 917: ' + str(rhotmp))
            GRID.set_rho_node(grdnode, rhotmp)

            # TODO decelerate densification process
            ''' process > 830 = compression of the bubbles until its ice (HL, )
            'at greater depths the density of even the most air-rich ice hardly differs from the
            density of pure ice, and accordingly the rate of change of density
            with depth is infinitesimal' (Shumskiy, 1960:570). '''

        elif (GRID.get_rho_node(grdnode) >= ice_density):
            log.warning('Density of layer ' + str(grdnode)+ ' > 917: ' + str(GRID.get_rho_node(grdnode)))
            GRID.set_rho_node(grdnode, ice_density)
            
        else:
            pass
        
        log.debug('rho[' + str(grdnode) + ']' + str(GRID.get_rho_node(grdnode)))

        ''' update h, T and LWC '''
        if (GRID.get_rho_node(grdnode) < ice_density):

            ''' update h '''
            # calc firn compaction layer height ratio
            newheight = (rholayer_old[grdnode] / GRID.get_rho_node(grdnode)) * \
               GRID.get_hlayer_node(grdnode)

            log.debug('New height:' + str(newheight))
            log.debug('Old height:' + str(hlayer_old[grdnode]))

            GRID.set_hlayer_node(grdnode, newheight)

            ''' T is updated in subsurface MB model '''
            #newtemp = tlayer_old[grdnode]
            #GRID.set_T_node(grdnode, newtemp)

            ''' LWC is updated in subsurface MB model '''
            #newlwc = lwclayer_old[grdnode]
            #GRID.set_LWC_node(grdnode, newlwc)

            #GRID.update_node(grdnode, newheight, rhotmp, newtemp, newlwc)
            # TODO integrate in density solvers above

        else:
            pass

        

        dh_list.append(hlayer_old[grdnode] - GRID.get_hlayer_node(grdnode))    # track dhdt firn of each lyr to prev. step

    ''' Prepare for return '''
    dh_firn = sum(GRID.get_hlayer()) - sum(hlayer_old)                         # difference of cumulative layer height's

    log.debug('dh firn: ' + str(dh_firn))

    for i in range(len(dh_list)):
        log.debug('dh list ' + str(dh_list[i]))

    log.debug('dh list sum: ' + str(sum(dh_list)))
    
    return dh_list, dh_firn
