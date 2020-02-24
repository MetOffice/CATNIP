"""
Author: Grace Redmond
Date: 04/2019
"""


import cartopy.crs as ccrs
import iris
import numpy as np


def regular_point_to_rotated(cube, lon, lat):
    """
    Function to convert a regular lon lat point to
    the equivalent point on a rotated pole grid
    defined by the coordinate system of an input cube.
    Longitude can be either 0-360 or -180-180 degree.

    args
    ----
    cube: cube on rotated coord system
    lon: float of regular longitude point
    lat: float of regular latitude point

    Returns
    -------
    rot_lon: The equivalent longitude point on the grid of the input cube
    rot_lat: The equivalent latitude point on the grid of the input cube

    An example:

    >>> lat = 6.5
    >>> lon = 289 # on 0-360 degree
    >>> cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/rcm_monthly.pp', 'air_temperature')
    >>> rot_lon, rot_lat = regular_point_to_rotated(cube, lon, lat)
    >>> print("{:.3f}".format(rot_lon), "{:.3f}".format(rot_lat))
    -84.330 3.336
    >>> lat = 6.5
    >>> lon = -71 # on -180-180 degree
    >>> rot_lon, rot_lat = regular_point_to_rotated(cube, lon, lat)
    >>> print("{:.3f}".format(rot_lon), "{:.3f}".format(rot_lat))
    -84.330 3.336
    """

    # get name of y coord
    ycoord = cube.coord(axis='Y', dim_coords=True)
    # cartopy.crs.RotatedGeodetic object
    rot_pole = cube.coord(ycoord).coord_system.as_cartopy_crs()
    # "regular" lon/lat coord system
    ll = ccrs.Geodetic()
    # Transform the lon lat point into rotated coordinates.
    rot_lon, rot_lat = rot_pole.transform_point(lon, lat, ll)

    return rot_lon, rot_lat


def rotated_point_to_regular(cube, rot_lon, rot_lat):
    """
    Function to convert a rotated lon lat point to
    the equivalent real lon lat point. Rotation of input point
    defined by the coordinate system of the input cube.
    Longitude output in -180-180 degree format.

    args
    ----
    cube: cube on rotated coord system, used as reference grid for transformation.
    rot_lon: float of rotated longitude point
    rot_lat: float of rotated latitude point

    Returns
    -------
    reg_lon: The equivalent real longitude point.
    reg_lat: The equivalent real latitude point.

    An example:

    >>> cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/rcm_monthly.pp', 'air_temperature')
    >>> rot_lat = 3.34
    >>> rot_lon = -84.33
    >>> reg_lon, reg_lat = rotated_point_to_regular(cube, rot_lon, rot_lat)
    >>> print("{:.3f}".format(reg_lon), "{:.3f}".format(reg_lat))
    -71.003 6.502
    >>> rot_lat = 40
    >>> rot_lon = 370
    >>> reg_lon, reg_lat = rotated_point_to_regular(cube, rot_lon, rot_lat)
    >>> print("{:.3f}".format(reg_lon), "{:.3f}".format(reg_lat))
    116.741 82.265
    """

    # get name of y coord
    ycoord = cube.coord(axis='Y', dim_coords=True)
    # cartopy.crs.RotatedGeodetic object
    rot_pole = cube.coord(ycoord).coord_system.as_cartopy_crs()
    # "regular" lon/lat coord system
    ll = ccrs.Geodetic()
    # Transform the  rotated lon lat point into regular coordinates.
    reg_lon, reg_lat = ll.transform_point(rot_lon, rot_lat, rot_pole)

    return reg_lon, reg_lat


if __name__ == "__main__":
    import doctest
    doctest.testmod()
