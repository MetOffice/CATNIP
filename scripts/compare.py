"""
Author:Chris Kent's work, extended by Grace Redmond
Date:04/2019
"""

import numpy as np

def compare_coords(c1, c2):
    """
    Compare two iris coordinates - checks names, shape,
    point values, bounds and coordinate system.

    args
    ----
    c1: iris coordinate from a cube
    c2: iris coordinate from a cube

    An example:

    >>> import iris
    >>> data_dir = '/project/ciid/projects/catnip/stock_cubes'
    >>> cube1 = iris.load_cube(data_dir + '/gcm_monthly.pp', 'air_temperature')
    >>> cube2 = iris.load_cube(data_dir + '/FGOALS-g2_ua@925_nov.nc')
    >>>
    >>> compare_coords(cube1.coord('latitude'), cube2.coord('latitude'))
    long_name values differ: None and latitude
    var_name values differ: None and lat
    Point dtypes differ: float32 and float64
    One has bounds, the other doesn't
    """

    namelist = "long_name", "standard_name", "var_name"
    for aname in namelist:
        if getattr(c1, aname) != getattr(c2, aname):
            print("{} values differ: {} and {}".format(aname,
                                                       getattr(c1, aname),
                                                       getattr(c2, aname)))

    if c1.shape != c2.shape:
        print("Shapes do not match: {} and {}".format(str(c1.shape),
                                                      str(c2.shape)))

    if not np.array_equal(c1.points, c2.points):
        print("Point values are different")

    if c1.points.dtype != c2.points.dtype:
        print("Point dtypes differ: {} and {}".format(str(c1.points.dtype),
                                                      str(c2.points.dtype)))
    havebounds = [c1.has_bounds(), c2.has_bounds()]

    if np.sum(havebounds) == 1:
        print("One has bounds, the other doesn't")
    elif np.sum(havebounds) == 2:
        if not np.array_equal(c1.bounds, c2.bounds):
            print("Bound values do not match")

    if c1.units != c2.units:
        print("Coords have different units: {} and {}".format(str(c1.units),
                                                              str(c2.units)))

    if c1.coord_system or c2.coord_system:
        if c1.coord_system != c2.coord_system:
            print("Coord_system's differ: {} and {}".format(str(c1.coord_system),
                                                            str(c2.coord_system)))


def compare_cubes(cube1, cube2):

    """
    Compares two cubes for  names, data, coordinates.
    Does not yet include attributes
    Results are printed to the screen

    args
    ----
    cube1: iris cube
    cube2: iris cube

    An example:

    >>> import iris
    >>> data_dir = '/project/ciid/projects/catnip/stock_cubes'
    >>> cube1 = iris.load_cube(data_dir + '/gcm_monthly.pp', 'x_wind')
    >>> cube2 = iris.load_cube(data_dir + '/FGOALS-g2_ua@925_nov.nc')
    >>> compare_cubes(cube1, cube2) # doctest: +NORMALIZE_WHITESPACE
    ~~~~~ Cube name and data checks ~~~~~
    long_name values differ: None and Eastward Wind
    standard_name values differ: x_wind and eastward_wind
    var_name values differ: None and ua
    Cube dimensions differ: 2 and 3
    Data dtypes differ: float32 and float64
    Data types differ: <class 'numpy.ndarray'> and <class 'numpy.ma.core.MaskedArray'>
    ~~~~~ Coordinate checks ~~~~~
    WARNING - Dimensions coords differ on the following coord(s): ['time']
    Checking matching dim coords
    -- longitude vs longitude --
    long_name values differ: None and longitude
    var_name values differ: None and lon
    Point values are different
    Point dtypes differ: float32 and float64
    One has bounds, the other doesn't
    -- latitude vs latitude --
    long_name values differ: None and latitude
    var_name values differ: None and lat
    Shapes do not match: (144,) and (145,)
    Point values are different
    Point dtypes differ: float32 and float64
    One has bounds, the other doesn't
    WARNING - Dimensions coords differ on the following coord(s):
        ['air_pressure', 'forecast_period', 'forecast_reference_time',
        'height', 'month_number', 'time', 'year']
    Cubes have no matching aux coords
    """

    print("~~~~~ Cube name and data checks ~~~~~")
    namelist = "long_name", "standard_name", "var_name"
    for aname in namelist:
        if getattr(cube1, aname) != getattr(cube2, aname):
            print("{} values differ: {} and {}".format(aname,
                                                       getattr(cube1, aname),
                                                       getattr(cube2, aname)))

    if cube1.ndim != cube2.ndim:
        print("Cube dimensions differ: {} and {}".format(str(cube1.ndim),
                                                         str(cube2.ndim)))
    if cube1.units != cube2.units:
        print("Cube units differ: {} and {}".format(str(cube1.units),
                                                    str(cube2.units)))
    if cube1.data.dtype != cube2.data.dtype:
        print("Data dtypes differ: {} and {}".format(str(cube1.data.dtype),
                                                     str(cube2.data.dtype)))
    if type(cube1.data) != type(cube2.data):
        print("Data types differ: {} and {}".format(str(type(cube1.data)),
                                                    str(type(cube2.data))))

    if len(list(set(dir(cube1.data)) - set(dir(cube2.data)))):
        print("Difference in dir(cube.data)")

    print("~~~~~ Coordinate checks ~~~~~")
    dimcoords1 = set([coord.name() for coord in cube1.coords(dim_coords=True)])
    dimcoords2 = set([coord.name() for coord in cube2.coords(dim_coords=True)])

    # dim coords that are present in both cubes
    dim_coords = dimcoords1.intersection(dimcoords2)

    # dim coords that are not present in both cubes
    diff_coords = dimcoords1.symmetric_difference(dimcoords2)
    if diff_coords:
        print("WARNING - Dimensions coords differ on"
              " the following coord(s): {}".format(str(sorted(diff_coords))))

    if dim_coords:
        print("Checking matching dim coords")
        for c in dim_coords:
            print("-- {} vs {} --".format(c, c))
            compare_coords(cube1.coord(c), cube2.coord(c))
    else:
        print("Cubes have no matching dim coords")

    auxcoords1 = set([coord.name() for coord in cube1.aux_coords])
    auxcoords2 = set([coord.name() for coord in cube2.aux_coords])

    # aux coords that are present in both cubes
    aux_coords = auxcoords1.intersection(auxcoords2)

    # dim coords that are not present in both cubes
    diffa_coords = auxcoords1.symmetric_difference(auxcoords2)
    if diffa_coords:
        print("WARNING - Dimensions coords differ on"
              " the following coord(s): {}".format(str(sorted(diffa_coords))))

    if aux_coords:
        print("Checking matching aux coords")
        for ca in aux_coords:
            print("-- {} vs {} -- ".format(ca, ca))
            compare_coords(cube1.coord(ca), cube2.coord(ca))
    else:
        print("Cubes have no matching aux coords")


if __name__ == "__main__":
    import doctest
    doctest.testmod()
