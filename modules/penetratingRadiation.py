import logging
import math
import numpy as np
from constants import *


def penetrating_radiation(GRID, SWnet, dt):
    """ This methods calculates the surface energy balance """
    log = logging.getLogger(__name__)
    log.info('Penetrating radiation is running...')

    # Total height of first layer
    total_height = GRID.get_hlayer_node(0)
    #log.debug('total_height: ' + str(total_height))

    # Check, whether snow cover exits and penetrate SW radiation
    if GRID.get_rho_node(0) <= firn_ice_threshold:

        # Calc penetrating SW fraction
        Si = float(SWnet) * 0.1
        
        log.debug('penetrating SW fraction: ' + str(Si))

        # Loop over all internal layers
        for idx in range(1,GRID.nnodes-1):

            # Total height of overlying snowpack
            total_height = total_height + GRID.get_hlayer_node(idx)
            
            # Exponential decay of radiation
            Tmp = float(Si * math.exp(17.1 * -total_height))
            
            #log.debug(str(idx) + ' IF > total_height: ' + str(total_height))
            #log.debug(str(idx) + ' > Tmp: ' + str(Tmp))

            # Update temperature
            GRID.set_T_node(idx, np.minimum(zero_temperature ,float(GRID.get_T_node(idx) +
                                                 (Tmp / (GRID.get_rho_node(idx) *
                                                  spec_heat_air)) * (dt / GRID.get_hlayer_node(idx)))))
    else:
        Si = SWnet * 0.2
        for idx in range(1, GRID.nnodes-1):
            total_height = total_height + GRID.get_hlayer_node(idx)
            Tmp = float(Si * math.exp(2.5 * -total_height))
            
            #log.debug(str(idx) + ' ELSE > total_height: ' + str(total_height))
            #log.debug(str(idx) + ' > Tmp: ' + str(Tmp))
            
            GRID.set_T_node(idx, np.minimum(zero_temperature, float(GRID.get_T_node(idx) +
                                                 (Tmp / (GRID.get_rho_node(idx) *
                                                         spec_heat_air)) * (dt / GRID.get_hlayer_node(idx)))))

