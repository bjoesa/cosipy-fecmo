import numpy as np
import logging
from constants import *
from core.inout import *
from scipy.optimize import minimize


def energy_balance(x, GRID, SWnet, rho, Cs, T2, u2, q2, p, Li, phi, lam):

    if x >= zero_temperature:
        Lv = lat_heat_vaporize
    else:
        Lv = lat_heat_sublimation

    # Saturation vapour pressure at the surface
    Ew0 = 6.112 * np.exp((17.67*(x-273.16)) / ((x-29.66)))

    # if x>=zero_temperature:
    #     Ew0 = 6.1078 * np.exp((17.269388*(x-273.16)) / ((x-35.86)))
    # else:
    #     Ew0 = 6.1078 * np.exp((21.8745584*(x-273.16)) / ((x-7.66)))

    # newest Saturation water pressure calculation - Anselm http://www.sisyphe.upmc.fr/~ducharne/documents/MEC558reportDiyin_LU.pdf
    # result is (hPa) and termpature in K!!!
    # Ew0 = 6.112 * np.exp((17.62*x)/(x+243.12))


    # Sensible heat flux
    H = rho * spec_heat_air * Cs * u2 * (x - T2) * phi

    # Mixing ratio at surface
    q0 = (100.0 * 0.622 * (Ew0 / (p - Ew0))) / 100.0

    # Latent heat flux
    L = rho * Lv * Cs * u2 * (q0 - q2) * phi

    # Outgoing longwave radiation
    Lo = -surface_emission_coeff * sigma * np.power(x, 4.0)

    # Ground heat flux # TODO list index of get_T_node(2) runs out of range if nnodes < 2 --> SOLVE !
    B = -lam * ((2.0 * GRID.get_T_node(1) - (0.5 * ((3.0 * x) + GRID.get_T_node(2)))) /\
               (GRID.get_hlayer_node(0)))

    # Return residual of energy balance
    return np.abs(SWnet+Li+Lo-H-L-B)


def update_surface_temperature(GRID, alpha, z0, T2, rH2, N, p, G, u2):
    """ This methods updates the surface temperature and returns the surface fluxes 
        """
        
    log = logging.getLogger(__name__)
    log.info('Surface Temperature is updated...')
    
    # Saturation vapour pressure (hPa)
    Ew = 6.112 * np.exp((17.67*(T2-273.16)) / ((T2-29.66)))
    # if T2>=zero_temperature:
    #    Ew = 6.1078 * np.exp((17.269388*(T2-273.16)) / ((T2-35.86)))
    # else:
    #    Ew = 6.1078 * np.exp((21.8745584*(T2-273.16)) / ((T2-7.66)))
    #
    # newest Saturation water pressure calculation - Anselm http://www.sisyphe.upmc.fr/~ducharne/documents/MEC558reportDiyin_LU.pdf
    # result is (hPa) and termpature in K!!!
    # Ew = 6.112 * np.exp((17.62*T2)/(T2+243.12))

    # Water vapour at 2 m (hPa)
    Ea = (rH2 * Ew) / 100.0

    # Incoming longwave radiation CORRECT
    eps_cs = 0.23 + 0.433 * np.power(Ea/T2,1.0/8.0)
    eps_tot = eps_cs * (1 - np.power(N,2)) + 0.984 * np.power(N,2)
    Li = eps_tot * sigma * np.power(T2,4.0)

    # Mixing Ratio at 2 m or calculate with other formula? 0.622*e/p = q
    q2 = (rH2 * 0.622 * (Ew / (p - Ew))) / 100.0
    
    # Air density 
    rho = (p*100.0) / (287.058 * (T2 * (1 + 0.608 * q2)))

    # Bulk Richardson number todo: Check if eq correct!
    Ri = (9.81 * (T2 - zero_temperature) * 2.0) / (T2 * np.power(u2, 2))

    # Stability correction
    if (Ri > 0.01) & (Ri <= 0.2):
        phi = np.power(1-5*Ri,2)
    elif Ri > 0.2:
        phi = 0
    else:
        phi = 1
    
    # Total net shortwave radiation
    SWnet = G * (1-alpha)

    # Bulk transfer coefficient todo: I think z0e-4 is wrong it must be z0e-3
    Cs = np.power(0.41,2.0) / np.power(np.log(2.0/(z0/1000)),2)

    # Get mean snow density
    if (GRID.get_rho_node(0) >= 830.):
        snowRhoMean = snow_ice_threshold
    else:
        snowRho = [idx for idx in GRID.get_rho() if idx <= 830.]
        snowRhoMean = sum(snowRho)/len(snowRho)

    # Calculate thermal conductivity [W m-1 K-1] from mean density
    lam = 0.021 + 2.5 * (snowRhoMean/1000.0)**2.0
    
    res = minimize(energy_balance, GRID.get_T_node(0), method='L-BFGS-B', bounds=((200.0, 273.16),),
                   tol=1e-8, args=(GRID, SWnet, rho, Cs, T2, u2, q2, p, Li, phi, lam))
 
    # Set surface temperature
    GRID.set_T_node(0, float(res.x))

    if res.x >= zero_temperature:
        Lv = lat_heat_vaporize
    else:
        Lv = lat_heat_sublimation

    # Sensible heat flux
    H = rho * spec_heat_air * Cs * u2 * (res.x - T2) * phi

    # Saturation vapour pressure at the surface
    Ew0 = 6.112 * np.exp((17.67*(res.x-273.16)) / ((res.x-29.66)))
    # if res.x>=zero_temperature:
    #    Ew0 = 6.1078 * np.exp((17.269388*(res.x-273.16)) / ((res.x-35.86)))
    # else:
    #    Ew0 = 6.1078 * np.exp((21.8745584*(res.x-273.16)) / ((res.x-7.66)))

    # newest Saturation water pressure calculation - Anselm http://www.sisyphe.upmc.fr/~ducharne/documents/MEC558reportDiyin_LU.pdf
    # result is (hPa) and termpature in K!!!
    # Ew0 = 6.112 * np.exp((17.62*T2)/(T2+243.12))

    # Mixing ratio at surface
    q0 = (100.0 * 0.622 * (Ew0/(p-Ew0))) / 100.0

    # Latent heat flux
    L = rho * Lv * Cs * u2 * (q0-q2) * phi

    # Outgoing longwave radiation
    Lo = -surface_emission_coeff * sigma * np.power(res.x, 4.0)

    # Ground heat flux
    B = -lam * ((2 * GRID.get_T_node(1) - (0.5 * ((3 * res.x) + GRID.get_T_node(2)))) /\
                (GRID.get_hlayer_node(0)))

    #print(rho,"             ",GRID.get_node_temperature(2)-273.16, "                ",L)
    qdiff = q0-q2

    return res.fun, res.x, Li, Lo, H, L, B, SWnet, rho, Lv, Cs, q0, q2, qdiff, phi


