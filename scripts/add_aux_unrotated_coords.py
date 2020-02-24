"""
Author: Saeed Sadri
Additional content: Grace Redmond
"""

import iris
import iris.analysis
import numpy as np


def add_aux_unrotated_coords(cube):
    """
    This function takes a cube that is on a rotated pole
    coordinate system and adds to it, two addtional
    auxillary coordinates to hold the unrotated coordinate
    values.

    args
    ----
    cube: iris cube on an rotated pole coordinate system

    Returns
    -------
    cube: input cube with auxilliary coordinates of unrotated
    latitude and longitude


    See below for an example that should be run with python3:


    >>> import iris
    >>> cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/mslp.daily.rcm.viet.nc')
    >>> print([coord.name() for coord in cube.coords()])
    ['time', 'grid_latitude', 'grid_longitude']
    >>> add_aux_unrotated_coords(cube)
    >>> print([coord.name() for coord in cube.coords()])
    ['time', 'grid_latitude', 'grid_longitude', 'latitude', 'longitude']
    >>> print(cube.coord('latitude'))
    AuxCoord(array([[35.32243855, 35.33914928, 35.355619  , ..., 35.71848081,
            35.70883111, 35.69893388],
           [35.10317609, 35.11986604, 35.13631525, ..., 35.49871728,
            35.48908   , 35.47919551],
           [34.88390966, 34.90057895, 34.91700776, ..., 35.27895246,
            35.26932754, 35.25945571],
           ...,
           [ 6.13961446,  6.15413611,  6.16844578, ...,  6.48307389,
             6.47472284,  6.46615667],
           [ 5.92011032,  5.93461779,  5.94891347, ...,  6.26323044,
             6.25488773,  6.24633011],
           [ 5.70060768,  5.71510098,  5.72938268, ...,  6.04338876,
             6.03505439,  6.02650532]]), standard_name=None, units=Unit('degrees'), long_name='latitude')
    >>> print(cube.shape)
    (360, 136, 109)
    >>> print(cube.coord('latitude').shape)
    (136, 109)
    >>> print(cube.coord('longitude').shape)
    (136, 109)

    """

    # get cube's coordinate system
    cs = cube.coord_system()
    if str(cs).find('Rotated') == -1:
        raise TypeError('The cube is not on a rotated pole, coord system is {}'.format(str(cs)))

    # get coord names
    # Longitude
    xcoord = cube.coord(axis='X', dim_coords=True)
    # Latitude
    ycoord = cube.coord(axis='Y', dim_coords=True)

    # read in the grid lat/lon points from the cube
    glat = cube.coord(ycoord).points
    glon = cube.coord(xcoord).points

    # create a rectangular grid out of an array of
    # glon and glat values, shape will be len(glat)xlen(glon)
    x, y = np.meshgrid(glon, glat)

    # get the cube dimensions which corresponds to glon and glat
    x_dim = cube.coord_dims(xcoord)[0]
    y_dim = cube.coord_dims(ycoord)[0]

    # define two new variables to hold the unrotated coordinates
    rlongitude, rlatitude = iris.analysis.cartography.unrotate_pole(x, y, cs.grid_north_pole_longitude,
                                                                    cs.grid_north_pole_latitude)

    # create two new auxillary coordinates to hold
    # the values of the unrotated coordinates
    reg_long = iris.coords.AuxCoord(rlongitude, long_name='longitude',
                                    units='degrees')
    reg_lat = iris.coords.AuxCoord(rlatitude, long_name='latitude',
                                   units='degrees')

    # add two auxilary coordinates to the cube holding
    # regular(unrotated) lat/lon values
    cube.add_aux_coord(reg_long, [y_dim, x_dim])
    cube.add_aux_coord(reg_lat, [y_dim, x_dim])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
