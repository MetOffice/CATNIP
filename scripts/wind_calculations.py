"""
Author(s): Grace Redmond, Saeed Sadri, and UKCP code library
"""

import iris
import numpy as np


def windspeed(u_cube, v_cube):

    """
    This function calculates wind speed.

    args
    ----
    u_cube: cube of eastward wind
    v_cube: cube of northward wind

    Returns
    -------
    windspeed_cube: cube of wind speed in same units as input cubes.


    A simple example:

    >>> u_cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/gcm_monthly.pp', 'x_wind')
    >>> v_cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/gcm_monthly.pp', 'y_wind')
    >>> ws = windspeed(u_cube, v_cube)
    >>> ws.attributes['formula']
    'sqrt(u**2, v**2)'
    >>> print(np.min(ws.data),np.max(ws.data))
    0.010195612 13.077045
    >>> ws.standard_name
    'wind_speed'
    """

    if u_cube.units != getattr(v_cube, 'units', u_cube.units):
        raise ValueError("units do not match, {} and {}".format(u_cube.units, v_cube.units))

    # cube to put the windspeed in
    windspeed_cube = u_cube.copy()
    # adjust meta data
    windspeed_cube.standard_name = "wind_speed"
    if 'STASH' in windspeed_cube.attributes:
        windspeed_cube.attributes.pop('STASH', None)
    windspeed_cube.attributes['formula'] = "sqrt(u**2, v**2)"

    windspeed_cube.data = np.sqrt(u_cube.data**2 + v_cube.data**2)

    return windspeed_cube


def wind_direction(u_cube, v_cube, unrotate=True):

    """
    Adapted from UKCP common_analysis.py
    (http://fcm1/projects/UKCPClimateServices/browser/trunk/code/)

    This function calculates the direction of the wind vector,
    which is the "to" direction (e.g. Northwards)
    (i.e. NOT Northerly, the "from" direction!)
    and the CF Convensions say it should be measured
    clockwise from North. If the data is on rotated pole, the
    rotate_winds iris function is applied as a default, but this
    can be turned off.

    Note: If you are unsure whether your winds need to be
    unrotated you can use http://www-nwp/umdoc/pages/stashtech.html
    and navigate to the relevant UM version and stash code:
        -    Rotate=0 means data is relative to the model grid and DOES need to be unrotated.
        -    Rotate=1 means data is relative to the lat-lon grid and DOES NOT need unrotating.

    args
    ----
    u_cube: cube of eastward wind
    v_cube: cube of northward wind
    unrotate: boolean, defaults to True. If true and data is rotated pole, the winds are unrotated, if set to False, they are not.

    Returns
    -------
    angle_cube: cube of wind direction in degrees (wind direction 'to' not 'from')


    A simple example:

    >>> u_cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/rcm_monthly.pp', 'x_wind')
    >>> v_cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/rcm_monthly.pp', 'y_wind')
    >>> angle = wind_direction(u_cube, v_cube)
    data is on rotated coord system, un-rotating . . .
    >>> angle.attributes['formula']
    '(-(arctan2(v, u)*180/pi)+90)%360'
    >>> print(np.min(angle.data),np.max(angle.data))
    0.0181427 359.99008
    >>> angle.standard_name
    'wind_to_direction'
    >>> # Now take the same data and calculate the wind direction WITHOUT rotating
    ... angle_unrot = wind_direction(u_cube, v_cube, unrotate=False)
    >>> # Print the difference between wind direction data
    ... # where unrotate=True unrotate=False to illustrate
    ... # the importance of getting the correct unrotate option
    ... print(angle.data[0,100,:10] - angle_unrot.data[0,100,:10])
    [-26.285324 -26.203125 -26.120728 -26.038239 -25.955551 -25.872742
     -25.78981  -25.70668  -25.623428 -25.539993]
    """

    if u_cube.units != getattr(v_cube, 'units', u_cube.units):
        raise ValueError("units do not match, {} and {}".format(u_cube.units, v_cube.units))

    # check if data is on rotated pole, unrotate if necessary
    cs_str = str(u_cube.coord_system())
    if cs_str.find('Rotated') != -1:
        if unrotate:
            print('data is on rotated coord system, un-rotating . . .')
            target_cs = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
            u_cube, v_cube = iris.analysis.cartography.rotate_winds(u_cube, v_cube, target_cs)

    # create a cube for the output and adjust meta data
    angle_cube = u_cube.copy()
    angle_cube.units = "degree"
    angle_cube.standard_name = "wind_to_direction"
    angle_cube.long_name = "wind vector direction"
    angle_cube.var_name = "angle"
    if 'STASH' in angle_cube.attributes:
        angle_cube.attributes.pop('STASH', None)
    angle_cube.attributes["direction"] = "Angle of wind vector measured clockwise from Northwards"
    angle_cube.attributes["formula"] = "(-(arctan2(v, u)*180/pi)+90)%360"

    angle_cube.data = np.arctan2(v_cube.data, u_cube.data) * 180.0/np.pi
    # That gives the angle of the vector in degrees, anticlockwise from Eastwards.
    # (in the range -180 to +180)
    # But we want the bearing clockwise from Northwards (0,360), so:
    angle_cube.data = (-angle_cube.data + 90.0) % 360

    return angle_cube

if __name__ == "__main__":
    import doctest
    doctest.testmod()
