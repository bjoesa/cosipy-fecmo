#!/usr/bin/env python

import numpy as np
import logging

from core.node import *
from constants import *


class Grid:

    def __init__(self, hlayersList, rhoList, TList, LWCList, DEBUG):
        """ Initialize numerical grid 
        
        Input:         
        hlayersList : numpy array with the layer height
        rhoList     : numpy array with density values for each layer
        TList       : numpy array with temperature values for each layer
        LWCList     : numpy array with liquid water content for each layer
        DEBUG       : Debug level (0, 1, 2) """

        # Set class variables
        self.hlayersList = hlayersList
        self.rhoList = rhoList
        self.TList = TList
        self.LWCList = LWCList 
        self.DEBUG = DEBUG

        # Number of total nodes
        self.nnodes = len(hlayersList)
        
        # create logger
        log = logging.getLogger(__name__)

        # Print some information on initialized grid
        if (self.DEBUG == 0):
            pass
        
        elif (self.DEBUG == 10):
            # TODO this is the level with the most information braught the screen
            log.debug("Init grid with %d nodes \t" % self.nnodes)
            log.debug("Total domain depth is %4.2f m \n" % np.sum(hlayersList))
            
        elif (self.DEBUG >= 20):
            log.info("Init grid with %d nodes \t" % self.nnodes)
            log.info("Total domain depth is %4.2f m \n" % np.sum(hlayersList))
            
        else:
            print("Invalid debug level")
            pass

        # Do the grid initialization
        self.init_grid()


    def init_grid(self):
        """ Initialize the grid with according to the input data """

        # Init list with nodes
        self.grid = []

        # Fill the list with node instances and fill it with user defined data
        for idxNode in range(self.nnodes):
            self.grid.append(Node(self.hlayersList[idxNode], self.rhoList[idxNode], 
                self.TList[idxNode], self.LWCList[idxNode]))


    def add_node(self, hlayer, rho, T, LWC):
        """ Add a new node at the beginning of the node list (upper layer) """

        # Add new node
        self.grid.insert(0,Node(hlayer, rho, T, LWC))
        
        # Increase node counter
        self.nnodes += 1

    def add_node_idx(self, idx, hlayer, rho, T, LWC):
        """ Add a new node below node idx """

        # Add new node
        self.grid.insert(idx, Node(hlayer, rho, T, LWC))

        # Increase node counter
        self.nnodes += 1
    
    
    def remove_node(self, pos=None):
        """ Removes the node at position pos from the node list """

        # Remove node from list when there is at least one node
        if not self.grid:
            pass
        else:
            if pos is None:
                self.grid.pop(0)
            else:
                self.grid.pop(pos)
            
            # Decrease node counter
            self.nnodes -= 1



    def update_node(self, no, hlayer, rho, T, LWC):
        """ Update properties of a specific node """

        self.grid[no].set_hlayer(hlayer)
        self.grid[no].set_rho(rho)
        self.grid[no].set_T(T)
        self.grid[no].set_LWC(LWC)
        


    def update_grid(self, level):
        """ Merge the similar layers according to certain criteria. Users can 
        determine different levels: 
            
            level 0 :   Layers are never merged
            level 1 :   Layers are merged when density and T are similar
            level 2 :   Layers are merged when density and T are very similar 
            
        The iterative process starts from the upper grid point and goes through 
        all nodes. If two subsequent nodes are similar, the layers are merged. 
        In this case the next merging step starts again from the top. This loop
        is repeated until the last node is reached and all similar layers merged."""
        
        # create logger
        log = logging.getLogger(__name__)

        # Define the thresholds for merging levels
        if (level == 0):
            log.info("Merging level 0")
            merge = False
        elif (level == 1):
            log.info('Merging level 1')
            rhoThres = 5.
            TThres = 0.05
            merge = True
        elif (level == 2):
            log.info('Merging level 2')
            rhoThres = 10.
            TThres = 0.1
            merge = True
        else:
            log.info("Invalid merging level")
            pass

        # Auxilary variables
        idx = self.nnodes-1
                
        # Iterate over grid and check for similarity
        while merge: 
            
            if ((idx > 0) & (np.abs(self.grid[idx].get_rho() - self.grid[idx-1].get_rho()) <= rhoThres) &
                (np.abs(self.grid[idx-1].get_rho() - self.grid[idx-2].get_rho()) <=100.) &
                ((np.abs(self.grid[idx].get_T() - self.grid[idx-1].get_T()) <= TThres)) &
                (self.grid[idx].get_hlayer() + self.grid[idx-1].get_hlayer() <= 0.5)):
                #&
                #(self.grid[idx].get_rho() <= pore_closure)):
                #(self.grid[idx].get_rho() > 550.)):
                
                # Total height of both layer which are merged
                total_height = self.grid[idx].get_hlayer() + self.grid[idx-1].get_hlayer()

                # Add up height of the two layer
                hlayer_new = self.grid[idx].get_hlayer() + self.grid[idx-1].get_hlayer()                  
                
                # Get the new density, weighted by the layer heights
                rho_new = (self.grid[idx].get_hlayer()/total_height)*self.grid[idx].get_rho() + \
                        (self.grid[idx-1].get_hlayer()/total_height)*self.grid[idx-1].get_rho() 

                # specific heat of ice (i) and air (p) [J kg-1 K-1] TODO: NEED TO BE CORRECTED
                #spec_heat_air = c_p

                # First calculate total energy
                Q_new =  (self.grid[idx].get_hlayer() * spec_heat_air * self.grid[idx].get_rho() * self.grid[idx].get_T()) + \
                        (self.grid[idx-1].get_hlayer() * spec_heat_air*self.grid[idx-1].get_rho() * self.grid[idx-1].get_T())
                
                # Convert total energy to temperature according to the new density
                T_new = Q_new/(spec_heat_air*rho_new*hlayer_new)
                
                # Todo: CHECK IF RIGHT!!!!!
                LWC_new = self.grid[idx].get_LWC() + self.grid[idx].get_LWC()

                # Update node properties
                self.update_node(idx, hlayer_new, rho_new, T_new, LWC_new)

                # Remove the second layer
                self.remove_node(idx-1)
           
                # Move to next layer 
                idx -= 1

                # Write merging steps if debug level is set >= 10
                if (self.DEBUG <= 20):
                    log.info("Merging ....")
                    for i in range(self.nnodes):
                        log.debug('hlayer: ' + str(self.grid[i].get_hlayer()) + ' | tlayer: ' + str(self.grid[i].get_T()) + ' | rholayer: ' + str(self.grid[i].get_rho()))
                    log.debug("End merging .... \n")

            else:

                # Stop merging process, if iterated over entire grid
                if (idx == 0):
                    merge = False
                else:
                    idx -= 1


    def merge_new_snow(self, dh):
    
        # create logger
        log = logging.getLogger(__name__)
        
        """ Merge first layers according to certain criteria """

        if (self.grid[0].get_hlayer() <= dh):

                # Total height of both layer which are merged
                total_height = self.grid[0].get_hlayer() + self.grid[1].get_hlayer()

                # Add up height of the two layer
                hlayer_new = self.grid[0].get_hlayer() + self.grid[1].get_hlayer()                  
                
                # Get the new density, weighted by the layer heights
                rho_new = (self.grid[0].get_hlayer()/total_height)*self.grid[0].get_rho() + \
                        (self.grid[1].get_hlayer()/total_height)*self.grid[1].get_rho() 

                # TODO: NEED TO BE CORRECTED
                #spec_heat_air = c_p  # spec_heat_air

                # First calculate total energy
                Q_new =  (self.grid[0].get_hlayer() * spec_heat_air * self.grid[0].get_rho() * self.grid[0].get_T()) + \
                        (self.grid[1].get_hlayer() * spec_heat_air*self.grid[1].get_rho() * self.grid[1].get_T())
                
                # Convert total energy to temperature according to the new density
                T_new = Q_new/(spec_heat_air*rho_new*hlayer_new)
                
                # Todo: CHECK IF RIGHT!!!!!
                LWC_new = self.grid[0].get_LWC() + self.grid[1].get_LWC()

                # Update node properties
                self.update_node(1, hlayer_new, rho_new, T_new, LWC_new)

                # Remove the second layer
                self.remove_node(0)
           
                # Write merging steps if debug level is set >= 10
                if (self.DEBUG <= 20):
                    log.info("New Snow Merging ....")
                    for i in range(self.nnodes):
                        log.debug('hlayer: ' + str(self.grid[i].get_hlayer()) + ' | tlayer: ' + str(self.grid[i].get_T()) + ' | rholayer: ' + str(self.grid[i].get_rho()))
                    log.debug("End merging .... \n")


    def remove_melt_energy(self, melt):

        """ removes every iteration the surface layer if melt energy is large enough """

        # Convert melt (m w.e.q.) to m height
        dh = float(melt) / (self.get_rho_node(0)/1000.0)   # m (snow) - negative = melt
        
        runoff = 0

        if (dh != 0.0):
            remove = True
        else:
            remove = False

        while remove:
                
                # How much energy required to melt first layer
                meltRequired = self.get_hlayer_node(0) * (self.get_rho_node(0)/1000.0)

                # How much energy is left
                meltRest = melt - meltRequired

                # If not enough energy to remove first layer, first layers height is reduced by melt height
                if (meltRest <= 0):
                    self.set_hlayer_node(0,self.get_hlayer_node(0) - dh)
                    runoff += dh
                    remove = False

                # If entire layer is removed
                else:
                    runoff += self.get_hlayer_node(0)
                    self.remove_node(0)
                    melt = melt - meltRequired
                    remove = True
                    
        return runoff

    #-------------------------------
    # Setter functions
    #-------------------------------

    def set_T_node(self, idx, T):
        """ Set temperature of node idx """
        
        return self.grid[idx].set_T(T)
    
    def set_hlayer_node(self, idx, height):
        """ Set height of node idx """
        
        return self.grid[idx].set_hlayer(height)
    
    def set_LWC_node(self, idx, LWCnew):
        """ Set liquid water content of node idx """
        
        return self.grid[idx].set_LWC(LWCnew)

    def set_rho_node(self, idx, rho):
        """ Set density of node idx """

        return self.grid[idx].set_rho(rho)


    #-------------------------------
    # Getter functions
    #-------------------------------

    def get_T(self):
        """ Returns the temperature profile """
        T = []
        for idx in range(self.nnodes):
            T.append(self.grid[idx].get_T())
        
        return T


    def get_T_node(self, idx):
        """ Returns temperature of node idx """
        
        return self.grid[idx].get_T()
        

    
    def get_hlayer(self):
        """ Returns the heights of the layers """
        hlayer = []
        for idx in range(self.nnodes):
            hlayer.append(self.grid[idx].get_hlayer())
        
        return hlayer


    def get_hlayer_node(self, idx):
        """ Returns layer height of node idx """
        
        return self.grid[idx].get_hlayer()

    
    def get_rho_node(self, idx):
        """ Returns density of node idx """
        
        return self.grid[idx].get_rho()
        
    def get_rho(self):
        """ Returns the rho profile """
        rho = []
        for idx in range(self.nnodes):
            rho.append(self.grid[idx].get_rho())
        
        return rho

    def get_LWC_node(self, idx):
        """ Returns lwc of node idx """
        
        return self.grid[idx].get_LWC()
        
    def get_LWC(self):
        """ Returns the lwc profile """
        LWC = []
        for idx in range(self.nnodes):
            LWC.append(self.grid[idx].get_LWC())
        
        return LWC

    def info(self):
        """ Print some information on grid """
        
        # create logger
        log = logging.getLogger('Finished core.grid info ')
        log.info("Grid consists of %d nodes \t" , self.nnodes)
        
        tmp = 0
        for i in range(self.nnodes):
            tmp = tmp + self.grid[i].get_hlayer()

        log.info("Total domain depth is %4.2f m \n", tmp)

