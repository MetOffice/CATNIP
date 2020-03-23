"""
Author: ssadri
"""

import iris

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
    >>> cube_list = iris.load('/project/ciid/projects/catnip/stock_cubes/rcm_monthly.pp')
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
