"""
Written by gredmond
NOTE: that whilst this function works for model data,
there can be problems with obs data sets.
"""

import datetime
import iris


def common_timeperiod(cube1, cube2):
    """
    Takes in two cubes and finds the common time
    period between them. This period is then extracted
    from both cubes. Cubes with common time period are returned,
    along with strings of the start end end times of the
    common time period (format DD/MM/YYYY.) The input
    cubes must have a coordinate called 'time' which
    must have bounds.

    args
    ----
    cube1: cube that must have a coord called time.
    cube2: cube that must have a coord called time.

    Returns
    -------
    start_date_str: string of start date for the common period.
    end_date_str: string of end date for the common period.
    cube1_common: cube1 with the common time period between cube1 and cube2 extracted.
    cube2_common: cube2 with the common time period between cube1 and cube2 extracted.


    An example:

    >>> dir = "/project/ciid/projects/ciid_tools/stock_cubes/"
    >>> file_ = dir + "daily.19990801_19990823.pp"
    >>> cube1=iris.load_cube(file_)
    >>> file_ = dir + "daily.19990808_19990830.pp"
    >>> cube2=iris.load_cube(file_)
    >>> st, et, c1, c2 = common_timeperiod(cube1, cube2)
    Common time period:
    ('8/8/1999', '23/8/1999')
    >>> print(c1.coord('time')[0])
    DimCoord([1999-08-08 12:00:00], bounds=[[1999-08-08 00:00:00, 1999-08-09 00:00:00]], standard_name='time', calendar='360_day')
    >>> print(c2.coord('time')[0])
    DimCoord([1999-08-08 12:00:00], bounds=[[1999-08-08 00:00:00, 1999-08-09 00:00:00]], standard_name='time', calendar='360_day')
    >>> print(c1.coord('time')[-1])
    DimCoord([1999-08-22 12:00:00], bounds=[[1999-08-22 00:00:00, 1999-08-23 00:00:00]], standard_name='time', calendar='360_day')
    >>> print(c2.coord('time')[-1])
    DimCoord([1999-08-22 12:00:00], bounds=[[1999-08-22 00:00:00, 1999-08-23 00:00:00]], standard_name='time', calendar='360_day')
    """

    # Get time info for both cubes
    time_info1 = cube1.coord('time')
    start_time1 = time_info1.units.num2date(time_info1.bounds[0][0])
    end_time1 = time_info1.units.num2date(time_info1.bounds[-1][1])

    time_info2 = cube2.coord('time')
    start_time2 = time_info2.units.num2date(time_info2.bounds[0][0])
    end_time2 = time_info2.units.num2date(time_info2.bounds[-1][1])

    start_time = max([start_time1, start_time2])
    end_time = min([end_time1, end_time2])

    if start_time >= end_time:
        raise ValueError("No common time period. Start time ({}) is later than or the same as end time({})".format(str(start_time), str(end_time)))

    # string of start and end dates
    st_list = [str(start_time.day), str(start_time.month), str(start_time.year)]
    start_date_str = "/".join(st_list)
    et_list = [str(end_time.day), str(end_time.month), str(end_time.year)]
    end_date_str = "/".join(et_list)

    print("Common time period:")
    print((start_date_str, end_date_str))

    # create a constraint that covers the date range
    date_range = iris.Constraint(time=lambda cell: start_time <= cell.point <= end_time)

    # extract the date range
    cube1_common = cube1.extract(date_range)
    cube2_common = cube2.extract(date_range)

    # check cubes have the same time period
    # cube1_common
    time_info1c = cube1_common.coord('time')
    start_time1c = time_info1c.units.num2date(time_info1c.bounds[0][0])
    end_time1c = time_info1c.units.num2date(time_info1c.bounds[-1][1])
    # cube2_common
    time_info2c = cube2_common.coord('time')
    start_time2c = time_info2c.units.num2date(time_info2c.bounds[0][0])
    end_time2c = time_info2c.units.num2date(time_info2c.bounds[-1][1])

    # only warn, don't raise an error, cubes
    # might have different time frequencies
    # or calendars.
    if start_time1c != start_time2c:
        print("WARNING start_time of common time period cubes are NOT the same:")
        print(("Start time of common cube1 {}".format(str(start_time1c))))
        print(("Start time of common cube2 {}".format(str(start_time2c))))
    if end_time1c != end_time2c:
        print("WARNING end_time of common time period cubes are NOT the same:")
        print(("End time of common cube1 {}".format(str(end_time1c))))
        print(("End time of common cube2 {}".format(str(end_time2c))))

    return start_date_str, end_date_str, cube1_common, cube2_common

if __name__ == "__main__":
    import doctest
    doctest.testmod()
