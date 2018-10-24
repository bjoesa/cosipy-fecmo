import numpy as np
import logging

from constants import *
from config import *


def percolation_refreezing(GRID, rain, melt_water, runoff, t):
    """ Percolation and refreezing of melt water through the snow- and firn pack

    t  ::  dt integration time/ length time step
    melt_water :: melt

    """
    
    log = logging.getLogger(__name__)
    log.info('Percolation is running...')

    curr_t = 0
    Tnew = 0

    Q = 0  # initial runoff [m w.e.]

    # Get height of snow layers
    hlayers = GRID.get_hlayer()

    # Check stability criteria for diffusion
    dt_stab = c_stab * min(GRID.get_hlayer()) / percolation_velocity

    # upwind scheme to adapt liquid water content of entire GRID
    while curr_t < t:

        # Get a copy of the GRID liquid water content profile
        LWCtmp = np.copy(GRID.get_LWC())

        # Select appropriate time step
        dt_use = min(dt_stab, t - curr_t)

        # set liquid water content of top layer (idx, LWCnew)
        GRID.set_LWC_node(0, (float(melt_water) / t) * dt_use)

        # Loop over all internal grid points
        for idxNode in range(1, GRID.nnodes - 1, 1):
            # Grid spacing
            hk = ((hlayers[idxNode] / 2.0) + (hlayers[idxNode - 1] / 2.0))
            hk1 = ((hlayers[idxNode + 1] / 2.0) + (hlayers[idxNode] / 2.0))

            # Lagrange coefficients
            ak = hk1 / (hk * (hk + hk1))
            bk = (hk1 - hk) / (hk * hk1)
            ck = hk / (hk1 * (hk + hk1))

            # Calculate new liquid water content 
            # TODO: Division by zero might occur. Why? 
            # RuntimeWarning: overflow encountered in double_scalars.
            if LWCtmp[idxNode] > 0:  # if, to avoid division by 0
                LWCnew = LWCtmp[idxNode] - (percolation_velocity * dt_use) * \
                                       (ak * LWCtmp[idxNode - 1] + bk
                                        * LWCtmp[idxNode] + ck
                                        * LWCtmp[idxNode + 1])
            else:
                LWCnew = LWCtmp[idxNode]

            # Update GRID with new liquid water content
            GRID.set_LWC_node(idxNode, LWCnew)


        # Add the time step to current time
        curr_t = curr_t + dt_use

    #print 'percolated'.upper()

    '''
    percolation, saturated/unsaturated, retention, refreezing, runoff
    '''

    # for idxNode in range(0,GRID.nnodes-1,1):
    #
    #     # absolute irreducible water content
    #     LWCmin = GRID.get_LWC_node(idxNode)*LWCfrac
    #
    #     if GRID.get_LWC_node(idxNode) > LWCmin:
    #         percofreeze = True
    #         print idxNode, 'refreeze', GRID.get_T_node(idxNode)
    #     else:
    #         percofreeze = False
    #
    #     while percofreeze:
    #
    #         percofreeze = False
    #
    #         # how much water the layer can hold?
    #
    #         # how much water must/can be shifted to next layer?
    #
    #         # if T<zeroT, how much water refreezes until T>zeroT
    #
    #         # todo How to accouont for rain and its added water, melt and energy?
    #         # percolation and refreezing module in COSIMA matlab

'''
refreezing wird an die Methode aus GRID.removeMeltEnergy() angelehnt
refreezing setzt energie frei!
refreezing in layers < 273.16 K aber neue Energie beachten!

remove certain amount of refreezing meltwater (subFreeze [m w.e.]) from the LWC[idxnode] ([m w.e.])
and add node with density p_ice [kg m^-3] below the reduced node (which then is impermeable)
'''

