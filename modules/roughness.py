from constants import firn_ice_threshold, roughness_fresh_snow, roughness_firn, roughness_ice

def updateRoughness(GRID, hours_since_snowfall):
    """ This method updates the roughness length (Moelg et al 2009, J.Clim.)"""

    # Check whether snow or ice   # TODO is snow = firn ?
    if (GRID.get_rho_node(0) <= firn_ice_threshold):
    
        # Roughness length
        sigma = min(roughness_fresh_snow + 0.026 * hours_since_snowfall, roughness_firn)
        
    else:
    
        # Roughness length, set to ice
        sigma = roughness_ice


    return sigma

