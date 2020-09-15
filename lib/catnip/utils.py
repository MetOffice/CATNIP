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

from __future__ import absolute_import, division, print_function, unicode_literals
import iris
import numpy as np
import datetime as dt
import doctest
import itertools
import sys
import re
from six import string_types
from datetime import datetime, timedelta
import os.path
import catnip.config as conf

# when all scitools versions with netcdftime are retired we can remove this
# try - except
try:
    from netcdftime import datetime as cdatetime
except ImportError:
    from cftime import datetime as cdatetime

# NOTE: The common_timeperiod() and get_date_range() functions works for model data
# but can be problems with obs data sets.


def common_timeperiod(cube1, cube2):
    """
    Takes in two cubes and finds the common time
    period between them. This period is then extracted
    from both cubes. Cubes with common time period are returned,
    along with strings of the start end end times of the
    common time period (format DD/MM/YYYY).

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

    Notes
    -----
    The input cubes must have a coordinate called 'time' which must have bounds.

    An example:

    >>> file1 = os.path.join(conf.DATA_DIR, 'daily.19990801_19990823.pp')
    >>> file2 = os.path.join(conf.DATA_DIR, 'daily.19990808_19990830.pp')
    >>> cube1=iris.load_cube(file1)
    >>> cube2=iris.load_cube(file2)
    >>> st, et, c1, c2 = common_timeperiod(cube1, cube2)
    >>> print(c1.coord('time')[0])
    DimCoord([1999-08-08 12:00:00], \
bounds=[[1999-08-08 00:00:00, 1999-08-09 00:00:00]], \
standard_name='time', calendar='360_day')
    >>> print(c2.coord('time')[0])
    DimCoord([1999-08-08 12:00:00], \
bounds=[[1999-08-08 00:00:00, 1999-08-09 00:00:00]], standard_name='time', \
calendar='360_day')
    >>> print(c1.coord('time')[-1])
    DimCoord([1999-08-22 12:00:00], bounds=\
[[1999-08-22 00:00:00, 1999-08-23 00:00:00]], standard_name='time', calendar='360_day')
    >>> print(c2.coord('time')[-1])
    DimCoord([1999-08-22 12:00:00], bounds=\
[[1999-08-22 00:00:00, 1999-08-23 00:00:00]], standard_name='time', calendar='360_day')
    """

    # Get time info for both cubes
    try:
        time_info1 = cube1.coord("time")
    except KeyError:
        raise KeyError("Cube1 does not contain time coordinate")

    try:
        start_time1 = time_info1.units.num2date(time_info1.bounds[0][0])
        end_time1 = time_info1.units.num2date(time_info1.bounds[-1][1])
    except TypeError:
        raise TypeError("Cube1 does not contain time bounds")

    try:
        time_info2 = cube2.coord("time")
    except KeyError:
        raise KeyError("Cube2 does not contain time coordinate")

    try:
        start_time2 = time_info2.units.num2date(time_info2.bounds[0][0])
        end_time2 = time_info2.units.num2date(time_info2.bounds[-1][1])
    except TypeError:
        raise TypeError("Cube2 does not contain time bounds")

    start_time = max([start_time1, start_time2])
    end_time = min([end_time1, end_time2])

    if start_time >= end_time:
        raise ValueError(
            "No common time period. Start time ({}) is later than or the "
            "same as end time({})".format(
                str(start_time), str(end_time)
            )
        )

    # string of start and end dates
    st_list = [str(start_time.day), str(start_time.month), str(start_time.year)]
    start_date_str = "/".join(st_list)
    et_list = [str(end_time.day), str(end_time.month), str(end_time.year)]
    end_date_str = "/".join(et_list)

    # create a constraint that covers the date range
    date_range = iris.Constraint(time=lambda cell: start_time <= cell.point <= end_time)

    # extract the date range
    cube1_common = cube1.extract(date_range)
    cube2_common = cube2.extract(date_range)

    # check cubes have the same time period
    # cube1_common
    time_info1c = cube1_common.coord("time")
    start_time1c = time_info1c.units.num2date(time_info1c.bounds[0][0])
    end_time1c = time_info1c.units.num2date(time_info1c.bounds[-1][1])
    # cube2_common
    time_info2c = cube2_common.coord("time")
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


def compare_coords(c1, c2):
    """
    Compare two iris coordinates - checks names, shape,
    point values, bounds and coordinate system.

    args
    ----
    c1: iris coordinate from a cube
    c2: iris coordinate from a cube

    Notes
    -----

    An example:

    >>> file1 = os.path.join(conf.DATA_DIR, 'gcm_monthly.pp')
    >>> file2 = os.path.join(conf.DATA_DIR, 'FGOALS-g2_ua@925_nov.nc')
    >>> cube1 = iris.load_cube(file1, 'air_temperature')
    >>> cube2 = iris.load_cube(file2)
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
            print(
                "{} values differ: {} and {}".format(
                    aname, getattr(c1, aname), getattr(c2, aname)
                )
            )

    if c1.shape != c2.shape:
        print("Shapes do not match: {} and {}".format(str(c1.shape), str(c2.shape)))

    if not np.array_equal(c1.points, c2.points):
        print("Point values are different")

    if c1.points.dtype != c2.points.dtype:
        print(
            "Point dtypes differ: {} and {}".format(
                str(c1.points.dtype), str(c2.points.dtype)
            )
        )
    havebounds = [c1.has_bounds(), c2.has_bounds()]

    if np.sum(havebounds) == 1:
        print("One has bounds, the other doesn't")
    elif np.sum(havebounds) == 2:
        if not np.array_equal(c1.bounds, c2.bounds):
            print("Bound values do not match")

    if c1.units != c2.units:
        print(
            "Coords have different units: {} and {}".format(
                str(c1.units), str(c2.units)
            )
        )

    if c1.coord_system or c2.coord_system:
        if c1.coord_system != c2.coord_system:
            print(
                "Coord_system's differ: {} and {}".format(
                    str(c1.coord_system), str(c2.coord_system)
                )
            )


def compare_cubes(cube1, cube2):

    """
    Compares two cubes for  names, data, coordinates.
    Does not yet include attributes
    Results are printed to the screen

    args
    ----
    cube1: iris cube
    cube2: iris cube

    Notes
    -----

    An example:

    >>> file1 = os.path.join(conf.DATA_DIR, 'gcm_monthly.pp')
    >>> file2 = os.path.join(conf.DATA_DIR, 'FGOALS-g2_ua@925_nov.nc')
    >>> cube1 = iris.load_cube(file1, 'x_wind')
    >>> cube2 = iris.load_cube(file2)
    >>> compare_cubes(cube1, cube2) # doctest: +NORMALIZE_WHITESPACE
    ~~~~~ Cube name and data checks ~~~~~
    long_name values differ: None and Eastward Wind
    standard_name values differ: x_wind and eastward_wind
    var_name values differ: None and ua
    Cube dimensions differ: 2 and 3
    Data dtypes differ: float32 and float64
    Data types differ: <class 'numpy.ndarray'> and <class 'numpy.ma.core.MaskedArray'>
    ~~~~~ Coordinate checks ~~~~~
    WARNING - Dimension coords differ on the following coord(s): ['time']
    Checking matching dim coords
    -- latitude vs latitude --
    long_name values differ: None and latitude
    var_name values differ: None and lat
    Shapes do not match: (144,) and (145,)
    Point values are different
    Point dtypes differ: float32 and float64
    One has bounds, the other doesn't
    -- longitude vs longitude --
    long_name values differ: None and longitude
    var_name values differ: None and lon
    Point values are different
    Point dtypes differ: float32 and float64
    One has bounds, the other doesn't
    WARNING - Aux and/or Scalar coords differ on the following coord(s): \
['air_pressure', 'forecast_period', 'forecast_reference_time', 'height', \
'month_number', 'time', 'year']
    Cubes have no matching aux or scalar coords

    """

    # check inputs are both cubes
    if not isinstance(cube1, iris.cube.Cube):
        raise TypeError("Input cube1 is not a cube")

    if not isinstance(cube2, iris.cube.Cube):
        raise TypeError("Input cube2 is not a cube")

    print("~~~~~ Cube name and data checks ~~~~~")
    namelist = "long_name", "standard_name", "var_name"
    for aname in namelist:
        if getattr(cube1, aname) != getattr(cube2, aname):
            print(
                "{} values differ: {} and {}".format(
                    aname, getattr(cube1, aname), getattr(cube2, aname)
                )
            )

    if cube1.ndim != cube2.ndim:
        print(
            "Cube dimensions differ: {} and {}".format(str(cube1.ndim), str(cube2.ndim))
        )
    if cube1.units != cube2.units:
        print("Cube units differ: {} and {}".format(str(cube1.units), str(cube2.units)))
    if cube1.data.dtype != cube2.data.dtype:
        print(
            "Data dtypes differ: {} and {}".format(
                str(cube1.data.dtype), str(cube2.data.dtype)
            )
        )
    if type(cube1.data) != type(cube2.data):
        print(
            "Data types differ: {} and {}".format(
                str(type(cube1.data)), str(type(cube2.data))
            )
        )

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
        print(
            "WARNING - Dimension coords differ on"
            " the following coord(s): {}".format(str(sorted(diff_coords)))
        )

    if dim_coords:
        print("Checking matching dim coords")
        for c in sorted(dim_coords):
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
        print(
            "WARNING - Aux and/or Scalar coords differ on"
            " the following coord(s): {}".format(str(sorted(diffa_coords)))
        )

    if aux_coords:
        print("Checking matching aux and scalar coords")
        for ca in sorted(aux_coords):
            print("-- {} vs {} -- ".format(ca, ca))
            compare_coords(cube1.coord(ca), cube2.coord(ca))
    else:
        print("Cubes have no matching aux or scalar coords")


def date_chunks(
    startdate, enddate, yearchunk, indatefmt="%Y/%m/%d", outdatefmt="%Y/%m/%d"
):
    """
    Make date chunks from min and max date range. Make contiguous pairs of
    date intervals to aid chunking of MASS retrievals. Where the date interval
    is not a multiple of `yearchunk`, intervals of less than `yearchunk`
    may be returned.


    args
    ----
        startdate (string): Starting date (min date)
        enddate (string): Ending date (max date)
        yearchunk (int): Year chunks to split the date interval into
        indatefmt (string, optional): String format for input dates.
                                      Defaults to yyyy/mm/dd
        outdatefmt (string, optional): String format for ouput dates.
                                       Defaults to yyyy/mm/dd

    Returns
    -------
    list: List of strings of date intervals

    Notes
    -----
    This function is only compatible with python 3.

    Raises:
        ValueError: If `enddate` (ie. max date) is less than or
                    equal to `startdate` (ie. min date)
        Excpetion: If `yearchunk` is not an integer
        Exception: If not using python 3

    Examples:
          >>> date_chunks('1851/1/1', '1899/12/31', 25)
          [('1851/01/01', '1875/12/26'), ('1875/12/26', '1899/12/31')]
          >>> date_chunks('1890/1/1', '1942/12/31', 25)
          [('1890/01/01', '1914/12/27'), ('1914/12/27', '1939/12/21'), \
('1939/12/21', '1942/12/31')]


    """
    # Check python version
    if sys.version_info[0] < 3:
        raise Exception("Only compatible with Python 3")
    # Check yearchunk is integer
    if not isinstance(yearchunk, int):
        raise Exception("yearchunk must be an integer")
    # Convert strings to datetime objects
    mindate = dt.datetime.strptime(startdate, indatefmt)
    maxdate = dt.datetime.strptime(enddate, indatefmt)
    # Check dates
    if maxdate <= mindate:
        raise ValueError("Max date ({}) is <= min date ({})".format(maxdate, mindate))
    if yearchunk < 0:
        raise ValueError("yearchunk must be an integer >= zero")
    # Find date steps
    dates = [
        mindate + dt.timedelta(days=x)
        for x in range(0, (maxdate - mindate).days, yearchunk * 365)
    ]
    dates = [dt.datetime.strftime(d, outdatefmt) for d in dates]
    # Add final end date
    dates.append(dt.datetime.strftime(maxdate, outdatefmt))
    # Make contiguous date interval pairs
    a, b = itertools.tee(dates)
    next(b, None)
    return list(zip(a, b))


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
    date_range: iris constraint that spans the range between the first and last date

    Notes
    -----

    See below for an example, this is from a CMIP5 abrupt4xC02 run:

    >>> file = os.path.join(conf.DATA_DIR, 'FGOALS-g2_ua@925_nov.nc')
    >>> cube = iris.load_cube(file)
    >>> start_str, end_str, dr_constraint = get_date_range(cube)
    >>> print(start_str)
    1/11/490
    >>> print(end_str)
    1/12/747
    """

    # check input is a cube
    if not isinstance(cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    if "time" not in [dim.name() for dim in cube.coords()]:
        raise AttributeError("Cube must have time coordinate:")

    # Get RCM time info and construct a constraint for driving data loading
    time_info = cube.coord("time")
    start_time = time_info.units.num2date(time_info.bounds[0][0])
    end_time = time_info.units.num2date(time_info.bounds[-1][1])

    # string of start and end dates
    st_list = [str(start_time.day), str(start_time.month), str(start_time.year)]
    start_date_str = "/".join(st_list)
    et_list = [str(end_time.day), str(end_time.month), str(end_time.year)]
    end_date_str = "/".join(et_list)

    # create a constraint that covers the date range
    date_range = iris.Constraint(time=lambda cell: start_time <= cell.point <= end_time)
    return start_date_str, end_date_str, date_range


def sort_cube(cube, coord):
    """
    Function to sort a cube by a coordinate. Taken from
    http://nbviewer.jupyter.org/gist/pelson/9763057

    args
    ----
    cube: Iris cube to sort
    coord: coord to sort by (string)

    Returns
    -------
    cube: a new cube sorted by the coord

    Notes
    -----
    See below for examples

    >>> cube = iris.cube.Cube([0, 1, 2, 3])
    >>> cube.add_aux_coord(iris.coords.AuxCoord([2, 1, 0, 3], long_name='test'), 0)
    >>> print(cube.data)
    [0 1 2 3]
    >>> cube = sort_cube(cube, 'test')
    >>> print(cube.data)
    [2 1 0 3]
    >>> print(cube.coord('test'))
    AuxCoord(array([0, 1, 2, 3]), standard_name=None, units=Unit('1'), long_name='test')
    """
    # check input
    coord_to_sort = cube.coord(coord)
    assert coord_to_sort.ndim == 1, "One dim coords only please."

    # create sorted indices of coord
    (dim,) = cube.coord_dims(coord_to_sort)
    index = [slice(None)] * cube.ndim
    index[dim] = np.argsort(coord_to_sort.points)

    # apply to cube and return
    return cube[tuple(index)]


def convert_from_um_stamp(datestamp, fmt):
    """
    Convert UM date stamp to normal python date.

    args
    ----
    datestamp: UM datestamp
    fmt: either 'YYMMM' or 'YYMDH'

    returns
    -------
    dt: datetime object of the input datestamp

    Notes
    -----
    Does not support 3 monthly seasons e.g. JJA as described in the
    Precis technical manual, page 119.


    >>> print (convert_from_um_stamp('k5bu0', 'YYMDH'))
    2005-11-30 00:00:00

    """
    # Check input
    if (len(datestamp) != 5) or (fmt not in ("YYMMM", "YYMDH")):
        raise ValueError("Problem with input arguments {} {}".format(datestamp, fmt))

    # First calculate decades since 1800
    d = _precis_d2(datestamp[0])

    # calculate year
    yr = 1800 + (d * 10) + int(datestamp[1])

    # calculate month and if necessary day and hour
    if fmt == "YYMMM":
        mon = datetime.strptime(datestamp[2:5], "%b").month
        dt = datetime(year=yr, month=mon, day=1)
    else:
        # This is a YYMDH so need to convert day and hour as well
        mon = _precis_d2(datestamp[2])
        if mon > 12:
            raise ValueError(
                "Month is {}, must be in 1..12, try fmt == YYMMM ".format(mon)
            )
        d = _precis_d2(datestamp[3])
        hr = _precis_d2(datestamp[4])
        dt = datetime(year=yr, month=mon, day=d, hour=hr)

    return dt


def convert_to_um_stamp(dt, fmt):
    """
    Convert python datetime object or netcdf datetime object
    into UM date stamp.
    http://www.metoffice.gov.uk/binaries/content/assets/mohippo/pdf/4/m/tech_man_v2.pdf#page=119

    args
    ----
    dt: Python datetime object to convert
    fmt: either 'YYMMM' or 'YYMDH'. Will not convert seasonal (e.g. JJA)


    returns
    -------
    um_str: string with UMdatestamp

    Notes
    -----
    See below for examples

    >>> dt = datetime(1981, 11, 2)
    >>> print (dt, convert_to_um_stamp(dt, 'YYMMM'))
    1981-11-02 00:00:00 i1nov
    >>> print (dt, convert_to_um_stamp(dt, 'YYMDH'))
    1981-11-02 00:00:00 i1b20
    >>> dt = cdatetime(1981, 2, 30)
    >>> print (dt, convert_to_um_stamp(dt, 'YYMMM'))
    1981-02-30 00:00:00 i1feb
    >>> print (dt, convert_to_um_stamp(dt, 'YYMDH'))
    1981-02-30 00:00:00 i12u0
    """

    if not isinstance(dt, datetime) and not isinstance(dt, cdatetime):
        raise ValueError("Datetime format incorrect: {}".format(type(dt)))

    if fmt not in ("YYMMM", "YYMDH"):
        raise ValueError("Problem with format type {}".format(fmt))

    # First convert years
    yy = _precis_yy(dt.year)

    if fmt == "YYMMM":
        # just need to format the month as 3 character string
        mon = dt.strftime("%b").lower()
        um_str = "{}{}".format(yy, mon)
    else:
        mon = _precis_d2(dt.month)
        d = _precis_d2(dt.day)
        hr = _precis_d2(dt.hour)
        um_str = "{}{}{}{}".format(yy, mon, d, hr)

    assert len(um_str) == 5, "um_str {} wrong length\ndt = {}".format(
        um_str, dt.strftime("%Y%m%d")
    )
    return um_str


def _precis_yy(y):
    """
    Convert year (int) into 2 character UM year

    args
    ----
    y: int


    returns
    -------
    YY: string 2 letter UM year character

    Notes
    -----
    See below for an example


    >>> print (_precis_yy(1973))
    h3

    """

    # use // operator to round down (integer division)
    decades = y // 10
    onedigityrs = y - (decades * 10)
    decades = _precis_d2(decades - 180)
    yy = "{}{}".format(decades, onedigityrs)

    return yy


def _precis_d2(c):
    """ Convert characters according to PRECIS table D2
    http://www.metoffice.gov.uk/binaries/content/assets/mohippo/pdf/4/m/tech_man_v2.pdf#page=119

    args
    ----
    c: character or number to convert
    Supply a character to convert from left to right in the table
    Supply an int to convert from right to left in the table

    returns
    -------
    conv: converted value: int if input is string, string if input is int

    Notes
    -----
    See below for examples

    >>> print (_precis_d2('1'))
    1
    >>> print (_precis_d2('c'))
    12
    >>> print (_precis_d2('s'))
    28

    Also does the reverse conversions:
    >>> print (_precis_d2(1))
    1
    >>> print (_precis_d2(12))
    c
    >>> print (_precis_d2(28))
    s

    """
    if isinstance(c, string_types):
        # Throw error if non alpha numeric string supplied
        if not c.isalnum():
            raise ValueError("Out of bounds argument {}".format(c))
        # Converting left to right
        try:
            # Try converting from integer
            conv = int(c)
        except ValueError:
            # It's a character, so use ord() function to convert
            # to correct number
            conv = ord(c) - 87
    else:
        # Throw error if too large or too small number supplied
        if c < 0 or c > 35:
            raise ValueError("Out of bounds argument {}".format(c))
        # Converting right to left
        if c <= 9:
            # Just convert to string
            conv = str(c)
        else:
            # Calculate correct letter to convert to using chr()
            conv = chr(c + 87)

    return conv


def um_file_list(runid, startd, endd, freq):
    """
    Give a (thoretical) list of UM date format files between 2 dates.
    Assuming no missing dates.

    args
    ----
    runid: model runid
    startd: start date(date)
    endd: end date(date)
    freq:
    Specifies frequency of data according to PRECIS technical manual
    table D1
    http://www.metoffice.gov.uk/binaries/content/assets/mohippo/pdf/4/m/tech_man_v2.pdf#page=118
    Currently only supports:
    pa: Timeseries of daily data spanning 1 month (beginning 0z on the 1st day)
    pj: Timeseries of hourly data spanning 1 day (0z - 24z)
    pm: Monthly average data for 1 month
    Not currently supported: ps, px, p1, p2, p3, p4, mY

    returns
    -------
    filelist: list of strings giving the filenames

    Notes
    -----
    See below for examples

    >>> runid = 'akwss'
    >>> startd = datetime(1980, 9, 1)
    >>> endd = datetime(1980, 9, 3)
    >>> freq = 'pa'
    >>> print (um_file_list(runid, startd, endd, freq)) # doctest: +NORMALIZE_WHITESPACE
    ['akwssa.pai0910.pp', 'akwssa.pai0920.pp', 'akwssa.pai0930.pp']

    >>> startd = datetime(1980, 9, 1)
    >>> endd = datetime(1980, 12, 31)
    >>> freq = 'pm'
    >>> print (um_file_list(runid, startd, endd, freq)) # doctest: +NORMALIZE_WHITESPACE
    ['akwssa.pmi0sep.pp', 'akwssa.pmi0oct.pp',
     'akwssa.pmi0nov.pp', 'akwssa.pmi0dec.pp']

    """

    # list to store the output
    filelist = []

    dt = startd
    # check if the value of the start year is <= end year
    if dt.year > endd.year:
        raise ValueError(
            "Start date {} must be <= end year {}".format(dt.year, endd.year)
        )

    while dt <= endd:
        # Monthly frequency
        if freq == "pm":
            fname = "{}a.pm{}.pp".format(runid, convert_to_um_stamp(dt, "YYMMM"))
            # Add a month to the date
            if dt.month == 12:
                dt = dt.replace(year=dt.year + 1, month=1)
            else:
                dt = dt.replace(month=dt.month + 1)

        # Daily frequency
        elif freq == "pa":
            # build file name string
            fname = "{}a.pa{}.pp".format(runid, convert_to_um_stamp(dt, "YYMDH"))
            # add a day to the date
            dt = dt + timedelta(days=1)

        # Hourly frequency
        elif freq == "pj":
            # build file name string
            fname = "{}a.pj{}.pp".format(runid, convert_to_um_stamp(dt, "YYMDH"))
            # add a day to the date
            dt = dt + timedelta(days=1)

        # Not recognized frequency
        else:
            raise ValueError("Unsupported freq {} supplied.".format(freq))

        # Add to list
        filelist.append(fname)

    return filelist


def umstash_2_pystash(stash):
    """
    Function to take um style stash codes e.g. 24, 05216 and convert them into
    'python' stash codes e.g.m01s00i024, m01s05i216

    args
    ----
    stash: a tuple, list or string of stash codes

    Returns
    -------
    stash_list: a list of python stash codes

    Notes
    -----

    Some basic examples:

    >>> sc = '24'
    >>> umstash_2_pystash(sc)
    ['m01s00i024']
    >>> sc = '24','16222','3236'
    >>> umstash_2_pystash(sc)
    ['m01s00i024', 'm01s16i222', 'm01s03i236']
    >>> sc = ['1','15201']
    >>> umstash_2_pystash(sc)
    ['m01s00i001', 'm01s15i201']

    Now test that it fails when appropriate:

    >>> sc = '-24'
    >>> umstash_2_pystash(sc) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    AttributeError: stash item -24 contains non-numerical characters. Numbers only
    >>> sc = '1234567'
    >>> umstash_2_pystash(sc) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    IndexError: stash item is 1234567. Stash items must be no longer than 5 characters
    >>> sc = 'aaa'
    >>> umstash_2_pystash(sc) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    AttributeError: stash item aaa contains non-numerical characters. Numbers only
    >>> sc = '24a'
    >>> umstash_2_pystash(sc) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    AttributeError: stash item 24a contains non-numerical characters. Numbers only
    >>> sc = 24, 25
    >>> umstash_2_pystash(sc) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: 24 must be a string
    """

    stash_list = []
    # if stash is only one variable, it will be considered a string
    # and split, this statement checks for that case and puts
    # stash into a tuple to prevent splitting.
    if isinstance(stash, string_types):
        stash = tuple([stash])
    for scode in stash:
        if not isinstance(scode, string_types):
            raise TypeError("{} must be a string".format(scode))
        if len(scode) > 5:
            raise IndexError(
                "stash item is {}. Stash items must be no longer than 5 characters"
                .format(scode)
            )
        if not scode.isdigit():
            raise AttributeError(
                "stash item {} contains non-numerical characters. Numbers only".format(
                    scode
                )
            )

        # to split 3223 in to sec=3 and item=223
        sec, item = re.match(r"(\d{2})(\d{3})", scode.zfill(5)).groups()
        # to create a string m01s02i223   (if sec=03, and item=223)
        stash_list.append("m01s{}i{}".format(sec, item))

    return stash_list


if __name__ == "__main__":
    doctest.testmod()
