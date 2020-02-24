# written by gredmond, combination of a few very similar functions.

import iris
import iris.coord_categorisation as iccat


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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
