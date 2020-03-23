"""
Written by gredmond
NOTE: that whilst this function works for model data,
there can be problems with obs data sets.
"""

import iris


def get_date_range(cube):
    """
    Takes a cube and calculates the time period spanned by the cube.
    It returns a string of the start and end date, and an iris
    constraint that spans the time period of the cube.

    args
    ----
    cube: cube which must include a dimension coordinate called 'time'

    Returns
    -------
    start_date_str: string of the first time in the cube as a dd/mm/yyyy date
    end_date_str: string of the last time in the cube as a dd/mm/yyyy date
    date_range: iris constraint that spans the range between the
                first and last date



    See below for an example, this is from a CMIP5 abrupt4xC02 run:

    >>> cube_file='/project/ciid/projects/catnip/stock_cubes/FGOALS-g2_ua@925_nov.nc'
    >>> cube = iris.load_cube(cube_file)
    >>> start_str, end_str, dr_constraint = get_date_range(cube)
    0490-11-01 00:00:00
    0747-12-01 00:00:00
    >>> print(start_str)
    1/11/490
    >>> print(end_str)
    1/12/747
    """

    # Get RCM time info and construct a constraint for driving data loading
    time_info = cube.coord('time')
    start_time = time_info.units.num2date(time_info.bounds[0][0])
    end_time = time_info.units.num2date(time_info.bounds[-1][1])

    # string of start and end dates
    st_list = [str(start_time.day), str(start_time.month), str(start_time.year)]
    start_date_str = "/".join(st_list)
    et_list = [str(end_time.day), str(end_time.month), str(end_time.year)]
    end_date_str = "/".join(et_list)
    print(start_time)
    print(end_time)

    # create a constraint that covers the date range
    date_range = iris.Constraint(time=lambda cell: start_time <= cell.point <= end_time)
    return start_date_str, end_date_str, date_range

if __name__ == "__main__":
    import doctest
    doctest.testmod()
