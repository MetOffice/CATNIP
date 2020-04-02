"""
Created on March, 2020
Authors: Grace Redmond, Saeed Sadri, Hamish Steptoe
"""

import iris
import iris.analysis
import numpy as np
from six import string_types
import iris.coord_categorisation as iccat
from ascend import shape


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

        >>> cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/mslp.daily.rcm.viet.nc')
        >>> add_bounds(cube, 'time')
        time coordinate already has bounds, none will be added
        >>> add_bounds(cube, 'grid_latitude')
        grid_latitude bounds added
        >>> add_bounds(cube, ['grid_latitude','grid_longitude'])
        grid_latitude coordinate already has bounds, none will be added
        grid_longitude bounds added
        """

        # find names of dim coords
        c_names = [c.name() for c in cube.coords()]

        # if coord_names is a single string, it will be split,
        # by the loop this statement checks for that case and
        # puts stash into a tuple to prevent splitting.
        if isinstance(coord_names, string_types):
            coord_names = tuple([coord_names])

        for coord in coord_names:

            # check if coord is a string
            if not isinstance(coord, string_types):
                raise TypeError('Coordinate {} must be a string, it is currently a {}'.format(str(coord), type(coord)))

            # check coord is a coordinate of the cube
            if coord not in c_names:
                raise AttributeError('{} is not a coordinate, available coordinates are: {}'.format(coord, c_names))

            # check if the coord already has bounds
            if cube.coord(coord).has_bounds():
                print(('{} coordinate already has bounds, none will be added'.format(coord)))

            # add bounds to coord
            else:
                cube.coord(coord).guess_bounds(bound_position=bound_position)
                print(('{} bounds added'.format(coord)))


def add_coord_system(cube):
    '''
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
    cube: The input cube with coordinate system added, if the
          cube didn't have one already.


    A simple example:

    >>> file='/project/ciid/obs_datasets/asia/APHRODITE/gtopo30_025deg.nc'
    >>> cube = iris.load_cube(file)
    >>> print(cube.coord('latitude').coord_system)
    None
    >>> add_coord_system(cube)
    Coordinate system  GeogCS(6371229.0) added to cube
    <iris 'Cube' of height / (1) (latitude: 281; longitude: 361)>
    >>> print(cube.coord('latitude').coord_system)
    GeogCS(6371229.0)
    '''

    # Note: wgs84 is the World Geodetic System, and a standard coord
    # system in iris. In GeogCS(6371229.0), 6371229 is the Earth's
    # radius in m. See:
    # https://scitools.org.uk/iris/docs/v1.9.0/html/iris/iris/coord_systems.html

    coord_names = [coord.name() for coord in cube.coords(dim_coords=True)]

    if 'latitude' in coord_names:
        # if there is no coord-system, add one
        if cube.coord('latitude').coord_system is None:
            wgs84_cs = iris.coord_systems.GeogCS(6371229.0)
            cube.coord('latitude').coord_system = wgs84_cs
            cube.coord('longitude').coord_system = wgs84_cs
            print('Coordinate system  GeogCS(6371229.0) added to cube')
            return cube
        else:
            return cube
    # if cube is rotated, coord will be called grid_latitude
    elif 'grid_latitude' in coord_names:
        if cube.coord('grid_latitude').coord_system:
            return cube
    # not possible to add a coord system for
    # rotated pole cube without knowing the
    # rotation. Give error message.
    else:
        print('Error, no coordinate system for rotated pole cube')
        print((repr(cube)))
        pass


def add_time_coord_cats(cube):
    '''
    This function takes in an iris cube, and adds a range of
    numeric co-ordinate categorisations to it. Depending
    on the data, not all of the coords added will be relevant.

    args
    ----
    cube: iris cube that has a coordinate called 'time'

    Returns
    -------
    Cube: cube that has new time categorisation coords added

    A simple example:
    >>> cube_file = '/project/ciid/projects/ciid_tools/stock_cubes/mslp.daily.rcm.viet.nc'
    >>> cube = iris.load_cube(cube_file)
    >>> coord_names = [coord.name() for coord in cube.coords()]
    >>> print((', '.join(coord_names)))
    time, grid_latitude, grid_longitude
    >>> add_time_coord_cats(cube)
    >>> coord_names = [coord.name() for coord in cube.coords()]
    >>> print((', '.join(coord_names)))
    time, grid_latitude, grid_longitude, day_of_month, day_of_year, month, month_number, season, season_number, year
    >>> # print every 50th value of the added time cat coords
    ... for c in coord_names[3:]:
    ...     print(cube.coord(c).long_name)
    ...     print(cube.coord(c).points[::50])
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
    '''

    # most errors pop up when you try to add a coord that has
    # previously been added, or the cube doesn't contain the
    # necessary attribute.

    # numeric
    try:
        iccat.add_day_of_year(cube, 'time')
    except AttributeError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    except ValueError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    try:
        iccat.add_day_of_month(cube, 'time')
    except AttributeError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    except ValueError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    try:
        iccat.add_month_number(cube, 'time')
    except AttributeError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    except ValueError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    try:
        iccat.add_season_number(cube, 'time')
    except AttributeError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    except ValueError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    try:
        iccat.add_year(cube, 'time')
    except AttributeError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    except ValueError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    # strings
    try:
        iccat.add_month(cube, 'time')
    except AttributeError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    except ValueError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    try:
        iccat.add_season(cube, 'time')
    except AttributeError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))
    except ValueError as err:
        print(('add_time_coord_cats: {}, skipping . . . '.format(err)))


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
    >>> cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/rcm_monthly.pp', 'air_temperature')
    >>> min_lat = 50
    >>> min_lon = -10
    >>> max_lat = 60
    >>> max_lon = 0
    >>> extracted_cube = extract_rot_cube(cube, min_lat, min_lon, max_lat, max_lon)
    >>> print(np.max(extracted_cube.coord('latitude').points))
    61.47165097005264
    >>> print(np.min(extracted_cube.coord('latitude').points))
    48.213032844268646
    >>> print(np.max(extracted_cube.coord('longitude').points))
    3.642576550089792
    >>> print(np.min(extracted_cube.coord('longitude').points))
    -16.385571344717235
    """
    # adding unrotated coords to the cube
    add_aux_unrotated_coords(cube)

    # use ASCEND package to cut the area out
    corners = [(min_lon, min_lat), (min_lon, max_lat),
               (max_lon, max_lat), (max_lon, min_lat)]
    rectangle = shape.create(corners, {'shape': 'rectangle'}, 'Polygon')
    extracted_cube = rectangle.extract_subcube(cube)


    return extracted_cube


def remove_forecast_coordinates(iris_cube):
    """A function to remove the forecast_period and forecast_reference_time coordinates from the UM PP files

    args
    ----
    iris_cube: input iris_cube

    Returns
    -------
    iris_cube: iris cube without the forecast_period and forecast_reference_time coordinates


    See below for examples:

    >>> cube_list_fcr = iris.cube.CubeList()
    >>> cube_list = iris.load('/project/ciid/projects/ciid_tools/stock_cubes/rcm_monthly.pp')
    >>> for cube in cube_list:
    ...     cube_fcr = remove_forecast_coordinates(cube)
    ...     cube_list_fcr.append(cube_fcr)
    Removed the forecast_period coordinate from Heavyside function on pressure levels cube
    Removed the forecast_reference_time coordinate from Heavyside function on pressure levels cube
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
        iris_cube.remove_coord('forecast_period')
        print(('Removed the forecast_period coordinate from {} cube'.format(iris_cube.name())))
    except iris.exceptions.CoordinateNotFoundError as coord_not_found:
        print('{}'.format(coord_not_found))
    try:
        iris_cube.remove_coord('forecast_reference_time')
        print(('Removed the forecast_reference_time coordinate from {} cube'.format(iris_cube.name())))
    except iris.exceptions.CoordinateNotFoundError as coord_not_found:
        print('{}'.format(coord_not_found))

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


    See below for examples:

    >>> cube_list_rr = iris.cube.CubeList()
    >>> cube_list = iris.load('/project/ciid/projects/ciid_tools/stock_cubes/rcm_monthly.pp')
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
    >>> mslp_cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/rcm_mslp_monthly.pp')
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
    if len(xcoord.points) <= (rim_width * 2) or len(ycoord.points) <= (rim_width * 2):
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