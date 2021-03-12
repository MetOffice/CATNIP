# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# (C) British Crown Copyright 2017-2020 Met Office.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

import iris
import iris.analysis
import numpy as np
from six import string_types, integer_types
import iris.coord_categorisation as iccat
import doctest
import os.path

import catnip.config as conf
import iris.exceptions
from dask import array as da


def _get_xy_noborder(mask):
    """
    make  a function that returns the indices
    of where the mask is valid. If the mask is all True (all masked)
    raises a ValueError

    args
    ----
    mask: mask from numpy array

    Returns
    -------
    x1, x2, y1, y2: int giving space where the data is valid

    """

    if np.all(mask):
        raise ValueError("All values masked - can't get indices")
    ys, xs = np.where(~mask)
    x1 = min(xs)
    x2 = max(xs) + 1
    y1 = min(ys)
    y2 = max(ys) + 1

    return x1, x2, y1, y2


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

    Notes
    -----

    See below for an example that should be run with python3:

    >>> file = os.path.join(conf.DATA_DIR, 'mslp.daily.rcm.viet.nc')
    >>> cube = iris.load_cube(file)
    >>> print([coord.name() for coord in cube.coords()])
    ['time', 'grid_latitude', 'grid_longitude']
    >>> auxcube = add_aux_unrotated_coords(cube)
    >>> print([coord.name() for coord in auxcube.coords()])
    ['time', 'grid_latitude', 'grid_longitude', 'latitude', 'longitude']
    >>> print(auxcube.coord('latitude')) # doctest: +NORMALIZE_WHITESPACE
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
             6.03505439,  6.02650532]]), standard_name=None, \
units=Unit('degrees'), long_name='latitude')
    >>> print(auxcube.shape)
    (360, 136, 109)
    >>> print(auxcube.coord('latitude').shape)
    (136, 109)
    >>> print(auxcube.coord('longitude').shape)
    (136, 109)

    """

    if not isinstance(cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    # get cube's coordinate system
    cs = cube.coord_system()

    if str(cs).find("Rotated") == -1:
        raise TypeError(
            "The cube is not on a rotated pole, coord system is {}".format(str(cs))
        )

    auxcube = cube.copy()
    # get coord names
    # Longitude
    xcoord = auxcube.coord(axis="X", dim_coords=True)
    # Latitude
    ycoord = auxcube.coord(axis="Y", dim_coords=True)

    # read in the grid lat/lon points from the cube
    glat = auxcube.coord(ycoord).points
    glon = auxcube.coord(xcoord).points

    # create a rectangular grid out of an array of
    # glon and glat values, shape will be len(glat)xlen(glon)
    x, y = np.meshgrid(glon, glat)

    # get the cube dimensions which corresponds to glon and glat
    x_dim = auxcube.coord_dims(xcoord)[0]
    y_dim = auxcube.coord_dims(ycoord)[0]

    # define two new variables to hold the unrotated coordinates
    rlongitude, rlatitude = iris.analysis.cartography.unrotate_pole(
        x, y, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude
    )

    # create two new auxillary coordinates to hold
    # the values of the unrotated coordinates
    reg_long = iris.coords.AuxCoord(rlongitude, long_name="longitude", units="degrees")
    reg_lat = iris.coords.AuxCoord(rlatitude, long_name="latitude", units="degrees")

    # add two auxilary coordinates to the cube holding
    # regular(unrotated) lat/lon values
    auxcube.add_aux_coord(reg_long, [y_dim, x_dim])
    auxcube.add_aux_coord(reg_lat, [y_dim, x_dim])

    return auxcube


def add_bounds(cube, coord_names, bound_position=0.5):
    """
        Simple function to check whether a
        coordinate in a cube has bounds, and
        add them if it doesn't.

        args
        ----
        cube: iris cube
        coord_names: string or list of strings containing the name/s
                     of the coordinates you want to add bounds to.
        bound_position: Optional, the desired position of the bounds relative to
                        the position of the points. Default is 0.5.

        Returns
        -------
        cube: cube with bounds added

        Notes
        -----
        Need to be careful that it is appropriate
        to add bounds to the data, e.g. if data
        are instantaneous, time bounds are not
        appropriate.

        An example:


        >>> file = os.path.join(conf.DATA_DIR, 'mslp.daily.rcm.viet.nc')
        >>> cube = iris.load_cube(file)
        >>> bcube = add_bounds(cube, 'time')
        time coordinate already has bounds, none will be added
        >>> bcube = add_bounds(cube, 'grid_latitude')
        grid_latitude bounds added
        >>> bcube = add_bounds(cube, ['grid_latitude','grid_longitude'])
        grid_latitude bounds added
        grid_longitude bounds added
        """

    # check if the input is an Iris cube
    if not isinstance(cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    # check if the coordinate name input is a string
    if not isinstance(coord_names, (string_types, list)):
        raise TypeError("Input coordinate must be a string")

    bcube = cube.copy()

    # find names of dim coords
    c_names = [c.name() for c in bcube.coords()]

    # if coord_names is a single string, it will be split,
    # by the loop this statement checks for that case and
    # puts stash into a tuple to prevent splitting.
    if isinstance(coord_names, string_types):
        coord_names = tuple([coord_names])

    for coord in coord_names:

        # check if coord is a string
        if not isinstance(coord, string_types):
            raise TypeError(
                "Coordinate {} must be a string, it is currently a {}".format(
                    str(coord), type(coord)
                )
            )

        # check coord is a coordinate of the cube
        if coord not in c_names:
            raise AttributeError(
                "{} is not a coordinate, available coordinates are: {}".format(
                    coord, c_names
                )
            )

        # check if the coord already has bounds
        if bcube.coord(coord).has_bounds():
            print(
                ("{} coordinate already has bounds, none will be added".format(coord))
            )

        # add bounds to coord
        else:
            bcube.coord(coord).guess_bounds(bound_position=bound_position)
            print(("{} bounds added".format(coord)))

    return bcube


def add_coord_system(cube):
    """
    A cube must have a coordinate system in order to be regridded.

    This function checks whether a cube has a coordinate system. If
    the cube has no coordinate system, the standard the ellipsoid
    representation wgs84 (ie. the one used by GPS) is added.

    Note: It will not work for rotated pole data without a
    coordinate system.

    args
    ----
    cube: iris cube

    Returns
    -------
    cube: The copy of the input cube with coordinate system added,
    if the cube didn't have one already.

    Notes
    -----

    A simple example:

    >>> file = os.path.join(conf.DATA_DIR, 'gtopo30_025deg.nc')
    >>> cube = iris.load_cube(file)
    >>> print(cube.coord('latitude').coord_system)
    None
    >>> cscube = add_coord_system(cube)
    Coordinate system  GeogCS(6371229.0) added to cube
    >>> print(cscube.coord('latitude').coord_system)
    GeogCS(6371229.0)
    """

    # Note: wgs84 is the World Geodetic System, and a standard coord
    # system in iris. In GeogCS(6371229.0), 6371229 is the Earth's
    # radius in m. See:
    # https://scitools.org.uk/iris/docs/v1.9.0/html/iris/iris/coord_systems.html

    # check if the input is an Iris cube
    if not isinstance(cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    cscube = cube.copy()
    cs = cscube.coord_system()

    if cs is not None:
        if str(cs).find("Rotated") == 0:
            # not possible to add a coord system for
            # rotated pole cube without knowing the
            # rotation. Give error message.
            raise TypeError("Error, no coordinate system for rotated pole cube")
    else:
        coord_names = [coord.name() for coord in cscube.coords(dim_coords=True)]
        wgs84_cs = iris.coord_systems.GeogCS(6371229.0)
        if "latitude" in coord_names:
            cscube.coord("latitude").coord_system = wgs84_cs
        if "longitude" in coord_names:
            cscube.coord("longitude").coord_system = wgs84_cs
        print("Coordinate system  GeogCS(6371229.0) added to cube")

    return cscube


def add_time_coord_cats(cube):
    """
    This function takes in an iris cube, and adds a range of
    numeric co-ordinate categorisations to it. Depending
    on the data, not all of the coords added will be relevant.

    args
    ----
    cube: iris cube that has a coordinate called 'time'

    Returns
    -------
    Cube: cube that has new time categorisation coords added

    Notes
    -----
    test

    A simple example:

    >>> file = os.path.join(conf.DATA_DIR, 'mslp.daily.rcm.viet.nc')
    >>> cube = iris.load_cube(file)
    >>> coord_names = [coord.name() for coord in cube.coords()]
    >>> print((', '.join(coord_names)))
    time, grid_latitude, grid_longitude
    >>> ccube = add_time_coord_cats(cube)
    >>> coord_names = [coord.name() for coord in ccube.coords()]
    >>> print((', '.join(coord_names)))
    time, grid_latitude, grid_longitude, day_of_month, day_of_year, month, \
month_number, season, season_number, year
    >>> # print every 50th value of the added time cat coords
    ... for c in coord_names[3:]:
    ...     print(ccube.coord(c).long_name)
    ...     print(ccube.coord(c).points[::50])
    ...
    day_of_month
    [ 1 21 11  1 21 11  1 21]
    day_of_year
    [  1  51 101 151 201 251 301 351]
    month
    ['Jan' 'Feb' 'Apr' 'Jun' 'Jul' 'Sep' 'Nov' 'Dec']
    month_number
    [ 1  2  4  6  7  9 11 12]
    season
    ['djf' 'djf' 'mam' 'jja' 'jja' 'son' 'son' 'djf']
    season_number
    [0 0 1 2 2 3 3 0]
    year
    [2000 2000 2000 2000 2000 2000 2000 2000]

    """

    # most errors pop up when you try to add a coord that has
    # previously been added, or the cube doesn't contain the
    # necessary attribute.

    ccube = cube.copy()

    # numeric
    try:
        iccat.add_day_of_year(ccube, "time")
    except AttributeError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    except ValueError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    try:
        iccat.add_day_of_month(ccube, "time")
    except AttributeError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    except ValueError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    try:
        iccat.add_month_number(ccube, "time")
    except AttributeError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    except ValueError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    try:
        iccat.add_season_number(ccube, "time")
    except AttributeError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    except ValueError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    try:
        iccat.add_year(ccube, "time")
    except AttributeError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    except ValueError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    # strings
    try:
        iccat.add_month(ccube, "time")
    except AttributeError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    except ValueError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    try:
        iccat.add_season(ccube, "time")
    except AttributeError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))
    except ValueError as err:
        print(("add_time_coord_cats: {}, skipping . . . ".format(err)))

    return ccube


def extract_rot_cube(cube, min_lat, min_lon, max_lat, max_lon):
    """
    Function etracts the specific region from the cube.
    args
    ----
    cube: cube on rotated coord system, used as reference grid for transformation.
    Returns
    -------
    min_lat: The minimum latitude point of the desired extracted cube.
    min_lon: The minimum longitude point of the desired extracted cube.
    max_lat: The maximum latitude point of the desired extracted cube.
    max_lon: The maximum longitude point of the desired extracted cube.
    An example:
    >>> file = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
    >>> cube = iris.load_cube(file, 'air_temperature')
    >>> min_lat = 50
    >>> min_lon = -10
    >>> max_lat = 60
    >>> max_lon = 0
    >>> extracted_cube = extract_rot_cube(cube, min_lat, min_lon, max_lat, max_lon)
    >>> max_lat_cube =  np.max(extracted_cube.coord('latitude').points)
    >>> print(f'{max_lat_cube:.3f}')
    61.365
    >>> min_lat_cube = np.min(extracted_cube.coord('latitude').points)
    >>> print(f'{min_lat_cube:.3f}')
    48.213
    >>> max_lon_cube = np.max(extracted_cube.coord('longitude').points)
    >>> print(f'{max_lon_cube:.3f}')
    3.643
    >>> min_lon_cube = np.min(extracted_cube.coord('longitude').points)
    >>> print(f'{min_lon_cube:.3f}')
    -16.292
    """

    # adding unrotated coords to the cube
    cube = add_aux_unrotated_coords(cube)

    # mask the cube using the true lat and lon
    lats = cube.coord("latitude").points
    lons = cube.coord("longitude").points
    select_lons = (lons >= min_lon) & (lons <= max_lon)
    select_lats = (lats >= min_lat) & (lats <= max_lat)
    selection = select_lats & select_lons
    selection = da.broadcast_to(selection, cube.shape)
    cube.data = da.ma.masked_where(~selection, cube.core_data())

    # grab a single 2D slice of X and Y and take the mask
    lon_coord = cube.coord(axis="X", dim_coords=True)
    lat_coord = cube.coord(axis="Y", dim_coords=True)
    for yx_slice in cube.slices(["grid_latitude", "grid_longitude"]):
        cmask = yx_slice.data.mask
        break

    # now cut the cube down along X and Y coords
    x1, x2, y1, y2 = _get_xy_noborder(cmask)
    idx = len(cube.shape) * [slice(None)]

    idx[cube.coord_dims(cube.coord(axis="x", dim_coords=True))[0]] = slice(x1, x2, 1)
    idx[cube.coord_dims(cube.coord(axis="y", dim_coords=True))[0]] = slice(y1, y2, 1)

    extracted_cube = cube[tuple(idx)]

    return extracted_cube


def remove_forecast_coordinates(iris_cube):
    """A function to remove the forecast_period and
    forecast_reference_time coordinates from the UM PP files

    args
    ----
    iris_cube: input iris_cube

    Returns
    -------
    iris_cube: iris cube without the forecast_period and forecast_reference_time
    coordinates

    Notes
    -----

    See below for examples:

    >>> cube_list_fcr = iris.cube.CubeList()
    >>> file = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
    >>> cube_list = iris.load(file)
    >>> for cube in cube_list:
    ...     cube_fcr = remove_forecast_coordinates(cube)
    ...     cube_list_fcr.append(cube_fcr)
    Removed the forecast_period coordinate from Heavyside function \
on pressure levels cube
    Removed the forecast_reference_time coordinate from Heavyside \
function on pressure levels cube
    Removed the forecast_period coordinate from air_temperature cube
    Removed the forecast_reference_time coordinate from air_temperature cube
    Removed the forecast_period coordinate from relative_humidity cube
    Removed the forecast_reference_time coordinate from relative_humidity cube
    Removed the forecast_period coordinate from specific_humidity cube
    Removed the forecast_reference_time coordinate from specific_humidity cube
    Removed the forecast_period coordinate from x_wind cube
    Removed the forecast_reference_time coordinate from x_wind cube
    Removed the forecast_period coordinate from y_wind cube
    Removed the forecast_reference_time coordinate from y_wind cube

    Now check if the forecast coordinates have been removed

    >>> for cube in cube_list_fcr:
    ...     cube_nfc = remove_forecast_coordinates(cube)
    'Expected to find exactly 1 forecast_period coordinate, but found none.'
    'Expected to find exactly 1 forecast_reference_time coordinate, but found none.'
    'Expected to find exactly 1 forecast_period coordinate, but found none.'
    'Expected to find exactly 1 forecast_reference_time coordinate, but found none.'
    'Expected to find exactly 1 forecast_period coordinate, but found none.'
    'Expected to find exactly 1 forecast_reference_time coordinate, but found none.'
    'Expected to find exactly 1 forecast_period coordinate, but found none.'
    'Expected to find exactly 1 forecast_reference_time coordinate, but found none.'
    'Expected to find exactly 1 forecast_period coordinate, but found none.'
    'Expected to find exactly 1 forecast_reference_time coordinate, but found none.'
    'Expected to find exactly 1 forecast_period coordinate, but found none.'
    'Expected to find exactly 1 forecast_reference_time coordinate, but found none.'
"""

    try:
        iris_cube.remove_coord("forecast_period")
        print(
            (
                "Removed the forecast_period coordinate from {} cube".format(
                    iris_cube.name()
                )
            )
        )
    except iris.exceptions.CoordinateNotFoundError as coord_not_found:
        print("{}".format(coord_not_found))
    try:
        iris_cube.remove_coord("forecast_reference_time")
        print(
            (
                "Removed the forecast_reference_time coordinate from {} cube".format(
                    iris_cube.name()
                )
            )
        )
    except iris.exceptions.CoordinateNotFoundError as coord_not_found:
        print("{}".format(coord_not_found))

    return iris_cube


def rim_remove(cube, rim_width):
    """ Return IRIS cube with rim removed.

    args
    ----
    cube: input iris cube
    rim_width: integer, number of grid points to remove from edge of lat and long

    Returns
    -------
    rrcube: rim removed cube

    Notes
    -----

    See below for examples:

    >>> cube_list_rr = iris.cube.CubeList()
    >>> file = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
    >>> cube_list = iris.load(file)
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
    >>> file = os.path.join(conf.DATA_DIR, 'rcm_mslp_monthly.pp')
    >>> mslp_cube = iris.load_cube(file)
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
    # check if the input is an Iris cube
    if not isinstance(cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    # check whether rim_width is an integer
    if not isinstance(rim_width, (integer_types)):
        raise TypeError("Please provide a positive integer for rim_width")
    if rim_width <= 0:
        raise IndexError("Please provide a positive integer > 0 for rim_width")

    # check whether this cube has already had it's rim removed
    if "rim_removed" in cube.attributes:
        print("WARNING - This cube has already had it's rim removed")

    # Longitude
    xcoord = cube.coord(axis="X", dim_coords=True)
    # Latitude
    ycoord = cube.coord(axis="Y", dim_coords=True)

    # make sure specified rim_width is going to work
    if len(xcoord.points) <= (rim_width * 2) or len(ycoord.points) <= (rim_width * 2):
        raise IndexError("length of lat or lon coord is < rim_width*2")

    # Remove rim from Longitude
    rrcube = cube.subset(xcoord[rim_width : -1 * rim_width])
    # Remove rim from Latitude
    rrcube = rrcube.subset(ycoord[rim_width : -1 * rim_width])
    # add meta data that rim has been removed
    rrcube.attributes["rim_removed"] = "{} point rim removed".format(rim_width)

    print(("Removed {} size rim from {}".format(rim_width, cube.name())))

    return rrcube


if __name__ == "__main__":
    doctest.testmod()
