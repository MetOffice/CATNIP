"""
Created on Oct, 2018
"""
import numpy as np

try:
    from improver.psychrometric_calculations.psychrometric_calculations import WetBulbTemperature
except:
    raise ImportError('No module named improver found. You must create a  '
                      '~/.local/lib/python3.6/site-packages/improver.pth file '
                      'containing the line /home/h05/gredmond/improver-master/lib '
                      'and try again.')

def calculate_dewpoint(P, Q, T):

    """ A function to calculate the dew point temperature, it
    expects three iris cubes P, Q, T. Stash codes needed are
    00001, 03237, 03236.

    args
    ----
    T: 1.5m temperature cube
    Q: 1.5m specific humidity cube
    P: P star cube

    Returns
    -------
    TD: 1.5m dew point temperature cube

    Notes
    -----
    Based on the UM routine /home/h04/precis/um/vn4.5/source/umpl/DEWPNT1A.dk
    which uses /home/h04/precis/um/vn4.5/source/umpl/QSAT2A.dk
    Constants:
        -   LC       is the latent heat of condensation of water at 0 deg C.
        -   RL1      is the latent heat of evaporation
        -   TM       is the temperature at which fresh waster freezes
        -   EPSILON  is the ratio of molecular weights of water and dry air
        -   R        the gas constant for dry air (J/kg/K)
        -   RV       gas constant for moist air (J/kg/K)

    This test compares dewpoint calculated by the
    calculate_dewpoint function, to dewpoint directly
    output from the UM i.e. uses the fortran routine

    >>> import iris
    >>> file1='/project/ciid/projects/ciid_tools/stock_cubes/dewpointtest_pt1.pp'
    >>> file2='/project/ciid/projects/ciid_tools/stock_cubes/dewpointtest_pt2.pp'
    >>> P=iris.load_cube(file2, 'surface_air_pressure')
    >>> T=iris.load_cube(file1, 'air_temperature')
    >>> Q=iris.load_cube(file1, 'specific_humidity')
    >>>
    >>> DEWPOINT=iris.load_cube(file1, 'dew_point_temperature')
    >>> TD = calculate_dewpoint(P, Q, T)
    WARNING dewpoint temp. > air temp ---> setting TD = T
    >>>
    >>> diff = DEWPOINT - TD
    >>> print(np.max(diff.data))
    0.37731934
    >>> print(np.min(diff.data))
    -0.31027222
    >>> print(np.mean(diff.data))
    2.934921e-05
    >>> print(np.std(diff.data))
    0.0058857435

 """

    # Set constants
    LC = 2.501E6
    RL1 = -2.73E3
    TM = 273.15
    EPSILON = 0.62198
    R = 287.05
    RV = R/EPSILON

    if not P.units == 'Pa':
        raise ValueError('P star must be in units of Pa not {}'.format(P.units))
    if not T.units == 'K':
        raise ValueError('1.5m temperature must be in units of K not {}'.format(T.units))
    if not Q.units == '1':
        raise ValueError('1.5m specific humidity must be in units of 1 not {}'.format(Q.units))

    # Set up output cube for dewpoint data
    TD = T.copy()
    TD.rename('dew_point_temperature')
    TD.attributes.pop('STASH', None)

    # Convert pressure from Pa to hPa
    P1 = P.data/100.00

    # Calculate RL - The latent heat of evaporation.
    RL = LC + RL1 * (T.data - TM)

    #  Calculate Vapour pressure
    V_PRES = Q.data * P1 / (EPSILON + Q.data)

    # Calculate saturation mixing ratio (Q0)
    # Uses the _calculate_mixing_ratio improver library function with ~gredmond's water/supercooled water
    # look up table to compute the mixing ratio given temperature and pressure.
    # See https://github.com/metoppv/improver/blob/master/lib/improver/psychrometric_calculations/psychrometric_calculations.py
    # Expects pressure in Pa, temperature in K
    cmr = WetBulbTemperature()  # Create an instance of class
    Q0 = cmr._calculate_mixing_ratio(T, P)

    # Calculate dew point
    # Make sure vapour pressure is positive before calculating
    where_pos = np.where(V_PRES > 0)
    ES0 = (Q0.data[where_pos] * P1[where_pos])/(EPSILON + Q0.data[where_pos])
    RT = (1/T.data[where_pos]) - (RV * np.log(V_PRES[where_pos]/ES0))/RL[where_pos]
    TD.data[where_pos] = 1.0/RT
    where_td_gt_t = np.where(TD.data > T.data)
    if where_td_gt_t[0].shape[0] > 0:
        print('WARNING dewpoint temp. > air temp ---> setting TD = T')
        TD.data[where_td_gt_t] = T.data[where_td_gt_t]

    # Check for any 0 or negative vaules of vapour pressure and set to NaN
    where_neg = np.where(V_PRES <= 0)
    if where_neg[0].shape[0] > 0:
        print('WARNING. Neg or zero Q in dewpoint calc. ---> setting TD = NaN')
        TD.data[where_neg] = float('nan')

    return TD

if __name__ == "__main__":
    import doctest
    doctest.testmod()
