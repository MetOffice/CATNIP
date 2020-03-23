"""
This function was written by tcrocker and added
to (error handling) by gredmond
"""

import iris
from six import integer_types

def rim_remove(cube, rim_width):
    """ Return IRIS cube with rim removed.

    args
    ----
    cube: input iris cube
    rim_width: integer, number of grid points to remove from edge of lat and long

    Returns
    -------
    rrcube: rim removed cube


    See below for examples:
 
    >>> cube_list_rr = iris.cube.CubeList()
    >>> cube_list = iris.load('/project/ciid/projects/catnip/stock_cubes/rcm_monthly.pp')
    >>> for cube in cube_list:
    ...     cube_rr = rim_remove(cube, 8)
    ...     cube_list_rr.append(cube_rr)    
    ... 
    Removed 8 size rim from Heavyside function on pressure levels
    Removed 8 size rim from air_temperature
    Removed 8 size rim from relative_humidity
    Removed 8 size rim from specific_humidity
    Removed 8 size rim from x_wind
    Removed 8 size rim from y_wind
    >>> mslp_cube = iris.load_cube('/project/ciid/projects/catnip/stock_cubes/rcm_mslp_monthly.pp')
    >>> 
    >>> mslp_cube_rr = rim_remove(mslp_cube, 8)
    Removed 8 size rim from air_pressure_at_sea_level
    >>> 
    >>> print(len(mslp_cube.coord('grid_latitude').points))
    432
    >>> print(len(mslp_cube.coord('grid_longitude').points))
    444
    >>> print(len(mslp_cube.coord('grid_latitude').points))
    432
    >>> print(len(mslp_cube.coord('grid_longitude').points))
    444
    >>> 
    >>> mslp_cube_rrrr = rim_remove(mslp_cube_rr, 8)
    WARNING - This cube has already had it's rim removed
    Removed 8 size rim from air_pressure_at_sea_level


    Now test for failures:

    >>> mslp_cube_rr = rim_remove(cube, 8.2) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: Please provide a positive integer for rim_width
    >>> mslp_cube_rr = rim_remove(cube, -5) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    IndexError: Please provide a positive integer > 0 for rim_width
    >>> mslp_cube_rr = rim_remove(cube, 400) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    IndexError: length of lat or lon coord is < rim_width*2
    >>> mslp_cube_rr = rim_remove(cube, 0) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    IndexError: Please provide a positive integer > 0 for rim_width
    >>> mslp_cube_rr = rim_remove(cube, 'a') # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: Please provide a positive integer for rim_width
    """
    # check whether rim_width is an integer
    if not isinstance(rim_width, (integer_types)):
        raise TypeError('Please provide a positive integer for rim_width')
    if rim_width <= 0:
        raise IndexError('Please provide a positive integer > 0 for rim_width')

    # check whether this cube has already had it's rim removed
    if 'rim_removed' in cube.attributes:
        print("WARNING - This cube has already had it's rim removed")

    # Longitude
    xcoord = cube.coord(axis='X', dim_coords=True)
    # Latitude
    ycoord = cube.coord(axis='Y', dim_coords=True)

    # make sure specified rim_width is going to work
    if len(xcoord.points) <= (rim_width*2) or len(ycoord.points) <= (rim_width*2):
        raise IndexError("length of lat or lon coord is < rim_width*2")

    # Remove rim from Longitude
    rrcube = cube.subset(xcoord[rim_width:-1 * rim_width])
    # Remove rim from Latitude
    rrcube = rrcube.subset(ycoord[rim_width:-1 * rim_width])
    # add meta data that rim has been removed
    rrcube.attributes['rim_removed'] = '{} point rim removed'.format(rim_width)

    print(('Removed {} size rim from {}'.format(rim_width, cube.name())))

    return rrcube

if __name__ == "__main__":
    import doctest
    doctest.testmod()
