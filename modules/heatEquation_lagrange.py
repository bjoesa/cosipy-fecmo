import numpy as np
import logging

from constants import *
from config import *


def solveHeatEquation_lagrange(GRID, t):
    """ Solves the heat equation on a non-uniform grid using

    dt  ::  integration timestep
    
    """
    log = logging.getLogger(__name__)
    log.info('Heat equation lagrange is running...')
  
    curr_t = 0
    Tnew = 0
    dt_use = 0

    # Get mean snow density
    if (GRID.get_rho_node(0) >= 830.):
        snowRhoMean = snow_ice_threshold      # TODO should it be 900 ?
    else:
        snowRho = [idx for idx in GRID.get_rho() if idx <= 830.]
        snowRhoMean = sum(snowRho)/len(snowRho)

    # Calculate specific heat depending on mean density
    c_pi = 152.2 + 7.122 * snowRhoMean 
    
    # Calculate thermal conductivity [W m-1 K-1] from mean density
    lam = 0.021 + 2.5 * (snowRhoMean/1000.0)**2.0

    # Calculate thermal diffusivity [m2 s-1]
    K = lam / (snowRhoMean * c_pi)
    
    hlayers = GRID.get_hlayer()

    # Check stability criteria for diffusion
    dt_stab = c_stab * (min(hlayers)**2.0) / (K)
    log.debug('dt_stab ' + str(dt_stab))
    
    while_counter = 0
   
    while curr_t < t:
   
        # Get a copy of the GRID temperature profile
        Ttmp = np.copy(GRID.get_T()) 

        # Loop over all internal grid points
        for idxNode in range(1,GRID.nnodes-1,1):

            # Grid spacing            
            hk = ((hlayers[idxNode]/2.0)+(hlayers[idxNode-1]/2.0))
            hk1 = ((hlayers[idxNode+1]/2.0)+(hlayers[idxNode]/2.0))
            
            #hk = ((hlayers[idxNode])+(hlayers[idxNode-1]))
            #hk1 = ((hlayers[idxNode+1])+(hlayers[idxNode]))

            # Lagrange coeffiecients
            ak = 2.0 / (hk*(hk+hk1))
            bk = -2.0 / (hk*hk1)
            ck = 2.0 / (hk1*(hk+hk1))

            # Select appropriate time step
            dt_use = min(dt_stab,t-curr_t)

            # Calculate new temperatures
            Tnew = Ttmp[idxNode] + (K * dt_use) * \
                (ak * Ttmp[idxNode-1] + bk * Ttmp[idxNode] + ck * Ttmp[idxNode+1]) 

            # Update GRID with new temperatures
            GRID.set_T_node(idxNode, Tnew) 

        # Add the time step to current time
        curr_t = curr_t + dt_use
        
        while_counter += 1
        
    log.info('while_counter ' + str(while_counter))
    
    return c_pi
