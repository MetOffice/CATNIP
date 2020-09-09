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

import numpy as np
from scipy.stats.distributions import t
import iris
import cartopy.crs as ccrs
import doctest
import os.path
import catnip.config as conf


def linear_regress(xi, yi):
    """
    Solves y = mx + c by returning the
    least squares solution to a linear matrix
    equation. Expects two numpy arrays of dimension 1.

    args
    ----
    xi: numpy array of dimension 1
    yi: dependant variable, numpy array of dimension 1

    Returns
    -------
    grad: gradient i.e. m in y = mx + c
    intcp: intercept i.e. c in y = mx + c
    xpts: the min and max value of xi, used to plot line of best fit
    ypts: the min and max of the y solutions to line of best fit for plotting

    Notes
    ------
    TODO: use sklearn to perform regression


    A simple example:

    >>> x = np.array([1, 4, 2, 7, 0, 6, 3, 3, 1, 9])
    >>> y = np.array([5, 6, 2, 9, 1, 4, 7, 8, 2, 6])
    >>> grad, intcp, xp, yp, sum_res = linear_regress(x, y)
    >>> print('gradient', "{:.2f}".format(grad))
    gradient 0.54
    >>> print('intercept', "{:.2f}".format(intcp))
    intercept 3.07
    """

    if np.shape(xi) != np.shape(yi):
        raise ValueError(
            "The input fields do not have the same shape, \
            {} and {}".format(
                str(np.shape(xi)), str(np.shape(yi))
            )
        )

    elif np.ndim(xi) != 1 or np.ndim(yi) != 1:
        raise ValueError(
            "xi and yi must have dinemsion 1, not xi \
            {} and yi {}".format(
                str(np.ndim(xi)), str(np.ndim(yi))
            )
        )
    else:
        # Return the least-squares solution to a linear matrix equation
        regression = np.linalg.lstsq(
            np.vstack([xi, np.ones(len(xi))]).T, yi, rcond=None
        )

        # Get the slope and the intercept
        grad, intcp = regression[0]

        # sum of residuals: squared Euclidean 2-norm for each column in yi - xi*x
        sum_res = regression[1]

        xmin, xmax = np.min(xi), np.max(xi)
        xpts = [xmin, xmax]
        ypts = grad * np.array(xpts) + intcp

    return grad, intcp, xpts, ypts, sum_res


def ci_interval(xi, yi, alpha=0.05):

    """
    Calculates  Confidence interval (default 95%) parameters for two
    numpy arrays of dimension 1. Returns include the gradient
    and intercept of the confidence interval.

    It also returns vectors for confidence interval plotting:
    -  the high/low confidence interval of the slope
    -  the high low curves of confidence interval of yi.

    args
    ----
    xi: numpy array of dimension 1
    yi: dependant variable, numpy array of dimension 1
    alpha: required confidence interval (e.g. 0.05 for 95%). Default is 0.05.

    Returns
    -------
    slope_conf_int: Gradient of confidence interval
    intcp_conf_int: Intercept (calculated using mean(yi)) of confidence interval
    xpts: the min and max value of xi.
    slope_lo_pts: for plotting, min and max y value of lower bound of CI of slope
    slope_hi_pts: for plotting, min and max y value of upper bound of CI of slope
    xreg: x values spanning xmin to xmax linearly spaced, for plotting against
          yi CI curve.
    y_conf_int_lo: for plotting, lower bound of CI region for yi
    y_conf_int_hi: for plotting, upper bound of CI region for yi

    Notes
    -----
    Parameters have been calculated using von Storch & Zwiers
    Statisical Analysis in Climate Research
    Sect.8.3.7 and 8.3.10

    A simple example:

    >>> x = np.array([1, 4, 2, 7, 0, 6, 3, 3, 1, 9])
    >>> y = np.array([5, 6, 2, 9, 1, 4, 7, 8, 2, 6])
    >>> slope_conf_int, intcp_conf_int, xpts, slope_lo_pts, slope_hi_pts, \
            xreg, y_conf_int_lo, y_conf_int_hi = ci_interval(x, y)
    Calculating the 95.0% confidence interval
    >>> print('CI gradient', "{:.2f}".format(slope_conf_int))
    CI gradient 0.62
    >>> print('CI intercept', "{:.2f}".format(intcp_conf_int))
    CI intercept 2.81

    """

    if xi.shape != yi.shape:
        raise ValueError(
            "The input fields do not have the same shape, \
            {} and {}".format(
                str(xi.shape), str(yi.shape)
            )
        )

    print(("Calculating the {}% confidence interval".format(str((1 - alpha) * 100))))
    # number of points
    n = len(xi)
    # degrees of freedom
    dof = n - 2  # assuming 2 parameters
    # student-t value for the dof and confidence level
    # Note, ppf - Percent point function (inverse of cdf - percentiles).
    t_val = t.ppf(1.0 - alpha / 2.0, dof)

    # Return the least-squares solution to a linear matrix equation
    slope, intcp, xp, yp, sum_res = linear_regress(xi, yi)

    # If yi is 1-dimensional, sum_res is a (1,) shape array.
    # Use this to calculate confidence intervals for plotting.
    if sum_res.shape == (1,):
        # standard error
        sd_err = np.sqrt(sum_res / (dof))[0]
        # calculate the sum of the squares of the difference
        # between each x and the mean x value
        sxx = np.sum((xi - np.mean(xi)) ** 2)
        if sxx == 0.0:
            raise ValueError("Sum of squares of difference is 0")

        # CI of slope: Formulated from vonStorch & Zwiers Sect.8.3.7
        slope_conf_int = (t_val * sd_err) / np.sqrt(sxx)
        # lower bound of slope using CI interval
        slope_lo = slope - slope_conf_int
        # upper bound of slope using CI interval
        slope_hi = slope + slope_conf_int
        xmin, xmax = np.min(xi), np.max(xi)
        # for plotting CI slope you want
        xpts = xmin, xmax
        slope_lo_pts = np.mean(yi) + slope_lo * ([xmin, xmax] - np.mean(xi))
        slope_hi_pts = np.mean(yi) + slope_hi * ([xmin, xmax] - np.mean(xi))

        # get regularly spaced np array of x points
        xreg = np.linspace(xmin, xmax, 101)
        # Population yi CI: Formulated from vonStorch & Zwiers Sect.8.3.10
        # CI for the mean of the response variable
        yfact = np.sqrt((1.0 / n) + (((xreg - np.mean(xi)) ** 2) / sxx))
        # 95% CI
        ymean_conf_int = (t_val * sd_err) * yfact
        # get the lines for plotting ymean CI
        y_conf_int_hi = (slope * xreg) + intcp + ymean_conf_int
        y_conf_int_lo = (slope * xreg) + intcp - ymean_conf_int

        # Intercept CI, using population y CI at x=0
        # Note, this isn't meaningful if x=0 is not physically meaningful
        yfact0 = np.sqrt((1.0 / n) + ((np.mean(xi) ** 2) / sxx))
        intcp_conf_int = (t_val * sd_err) * yfact0

        # if we need the high and low values of the intercept we
        # could add the following vaariables to the return statement
        # intcp_lo = intcp - intcp_conf_int
        # intcp_hi = intcp + intcp_conf_int

        return (
            slope_conf_int,
            intcp_conf_int,
            xpts,
            slope_lo_pts,
            slope_hi_pts,
            xreg,
            y_conf_int_lo,
            y_conf_int_hi,
        )


def regrid_to_target(cube, target_cube, method="linear", extrap="mask", mdtol=0.5):
    """
    Takes in two cubes, and regrids one onto the grid
    of the other. Optional arguments include the method
    of regridding, default is linear. The method of
    extrapolation (if it is required), the default is
    to mask the data, even if the source data is not
    a masked array. And, if the method is areaweighted,
    choose a missing data tolerance, default is 0.5.
    For full info, see
    https://scitools.org.uk/iris/docs/latest/userguide/interpolation_and_regridding.html

    args
    ----
    cube: cube you want to regrid
    target_cube: cube on the target grid
    method: method of regridding, options are 'linear', 'nearest' and 'areaweighted'.
    extrap: extraopolation mode, options are 'mask', 'nan', 'error' and 'nanmask'
    mdtol: tolerated fraction of masked data in any given target grid-box, only used
           if method='areaweighted', between 0 and 1.

    Returns
    -------
    cube_reg: input cube on the grid of target_cube

    Notes
    -----
    areaweighted is VERY picky, it will not allow you to regrid using this method
    if the two input cubes are not on the
    same coordinate system, and both input grids must also contain monotonic,
    bounded, 1D spatial coordinates.

    An example:

    >>> file1 = os.path.join(conf.DATA_DIR, 'gcm_monthly.pp')
    >>> file2 = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
    >>> cube = iris.load_cube(file1, 'air_temperature')
    >>> tgrid = iris.load_cube(file2, 'air_temperature')
    >>> cube_reg = regrid_to_target(cube, tgrid)
    regridding from GeogCS(6371229.0) to \
RotatedGeogCS(39.25, 198.0, ellipsoid=GeogCS(6371229.0)) using method linear
    >>> print(cube.shape, tgrid.shape)
    (145, 192) (2, 433, 444)
    >>> print(cube_reg.shape)
    (433, 444)
    """

    if not isinstance(cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    if not isinstance(target_cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    target_cs = target_cube.coord(axis="x").coord_system
    orig_cs = cube.coord(axis="x").coord_system

    # get coord names for cube
    # Longitude
    xcoord = cube.coord(axis="X", dim_coords=True)
    # Latitude
    ycoord = cube.coord(axis="Y", dim_coords=True)
    # get coord names for target_cube
    # Longitude
    t_xcoord = target_cube.coord(axis="X", dim_coords=True)
    # Latitude
    t_ycoord = target_cube.coord(axis="Y", dim_coords=True)

    if method == "linear":
        scheme = iris.analysis.Linear(extrapolation_mode=extrap)

    if method == "nearest":
        scheme = iris.analysis.Nearest(extrapolation_mode=extrap)

    # areaweighted is VERY picky and often can't be used.
    if method == "areaweighted":
        if not cube.coord(xcoord).has_bounds():
            print("Input cube to be regrided does not have lon bounds, guessing . . . ")
            cube.coord(xcoord).guess_bounds()
        if not cube.coord(ycoord).has_bounds():
            print("Input cube to be regrided does not have lat bounds, guessing . . . ")
            cube.coord(ycoord).guess_bounds()

        if not target_cube.coord(t_xcoord).has_bounds():
            print("Input target_cube does not have lon bounds, guessing . . . ")
            target_cube.coord(t_xcoord).guess_bounds()
        if not target_cube.coord(t_ycoord).has_bounds():
            print("Input target_cube does not have lat bounds, guessing . . . ")
            target_cube.coord(t_ycoord).guess_bounds()

        if target_cs != orig_cs:
            raise ValueError("The input cubes must have the same coordinate system")
        scheme = iris.analysis.AreaWeighted(mdtol=mdtol)

    print(
        "regridding from {} to {} using method {}".format(
            str(orig_cs), str(target_cs), method
        )
    )

    cube_reg = cube.regrid(target_cube, scheme)

    return cube_reg


def set_regridder(cube, target_cube, method="linear", extrap="mask", mdtol=0.5):
    """
    Takes in two cubes, and sets up a regridder, mapping
    one cube to another. The most computationally expensive
    part of regridding is setting up the re-gridder, if you
    have a lot of cubes to re-grid, this will save time.
    Optional arguments include the method of regridding,
    default is linear.The method of extrapolation (if
    it is required), the default is to mask the data,
    even if the source data is not a masked array. And,
    if the method is areaweighted, choose a missing data
    tolerance, default is 0.5.


    Note: areaweighted is VERY picky, it will not allow you to regrid using
    this method if the two input cubes are not on the same coordinate system,
    and both input grids must also contain monotonic, bounded, 1D spatial coordinates.

    args
    ----
    cube: cube you want to regrid
    target_cube: cube on the target grid
    method: method of regridding, options are 'linear', 'nearest' and 'areaweighted'.
    extrap: extraopolation mode, options are 'mask', 'nan', 'error' and 'nanmask'
    mdtol: tolerated fraction of masked data in any given target grid-box,
           only used if method='areaweighted', between 0 and 1.

    Returns
    -------
    regridder: a cached regridder which can be used on any iris cube which has
               the same grid as cube.


    Notes
    -----
    See:
    https://scitools.org.uk/iris/docs/latest/userguide/interpolation_and_regridding.html
    for more information

    An example:

    >>> file1 = os.path.join(conf.DATA_DIR, 'gcm_monthly.pp')
    >>> file2 = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
    >>> cube = iris.load_cube(file1, 'air_temperature')
    >>> tgrid = iris.load_cube(file2, 'air_temperature')
    >>> regridder = set_regridder(cube, tgrid)
    >>> cube2 = iris.load_cube(file1, 'cloud_area_fraction')
    >>> print(cube2.shape)
    (145, 192)
    >>> regridder(cube2)
    <iris 'Cube' of cloud_area_fraction / (1) (grid_latitude: 433; grid_longitude: 444)>
    """

    if not isinstance(cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    if not isinstance(target_cube, iris.cube.Cube):
        raise TypeError("Target_cube is not of type cube")

    target_cs = target_cube.coord(axis="x").coord_system
    orig_cs = cube.coord(axis="x").coord_system

    # get coord names for cube
    # Longitude
    xcoord = cube.coord(axis="X", dim_coords=True)
    # Latitude
    ycoord = cube.coord(axis="Y", dim_coords=True)
    # get coord names for target_cube
    # Longitude
    t_xcoord = target_cube.coord(axis="X", dim_coords=True)
    # Latitude
    t_ycoord = target_cube.coord(axis="Y", dim_coords=True)

    if method == "linear":
        regridder = iris.analysis.Linear(extrapolation_mode=extrap).regridder(
            cube, target_cube
        )

    if method == "nearest":
        regridder = iris.analysis.Nearest(extrapolation_mode=extrap).regridder(
            cube, target_cube
        )

    if method == "areaweighted":
        if not cube.coord(xcoord).has_bounds():
            print("Input cube to be regrided does not have lon bounds, guessing . . . ")
            cube.coord(xcoord).guess_bounds()
        if not cube.coord(ycoord).has_bounds():
            print("Input cube to be regrided does not have lat bounds, guessing . . . ")
            cube.coord(ycoord).guess_bounds()

        if not target_cube.coord(t_xcoord).has_bounds():
            print("Input target_cube does not have lon bounds, guessing . . . ")
            target_cube.coord(t_xcoord).guess_bounds()
        if not target_cube.coord(t_ycoord).has_bounds():
            print("Input target_cube does not have lat bounds, guessing . . . ")
            target_cube.coord(t_ycoord).guess_bounds()

        if target_cs != orig_cs:
            raise ValueError("The input cubes must have the same coordinate system")

        regridder = iris.analysis.AreaWeighted(mdtol=mdtol).regridder(cube, target_cube)

    return regridder


def seas_time_stat(
    cube,
    seas_mons=[[3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 1, 2]],
    metric="mean",
    pc=[],
    years=[],
    ext_area=[],
):
    """
    Takes in a cube and calculates a seasonal metric. Defaults to
    mean of 'mam','jja','son' and 'djf' over the whole time span
    of the cube. However, the user can specify seasons by month
    number i.e. ond=[10,11,12], the start and end years, the metric
    calculated and a lat lon region to extract for the calculation.

    args
    ----
    cube: Input cube that must contain a coordinate called 'time'
    seas_mons: list of seasons to calculate the metric over,
             defaults to seas_mons=[[3,4,5],[6,7,8],[9,10,11],[12,1,2]].
    metric: string, optional argument, defaults to 'mean', but can
          be 'mean', 'std_dev', 'min', 'max' or 'percentile'
    pc: optional argument, percentile level to calculate,
       must be an integer and must be set if metric='percentile'.
    years: list of start and end year, default is
           the whole time span of the cube.
    ext_area: optional argument, if set expects a list of
            the form [lonmin, lonmax, latmin, latmax].

    Returns
    -------
    cube_list: a cube list containing one cube per
             season of the calculated metric

    Notes
    -----
    The main draw back is that the function does not take
    account for seasons that span more than one year
    i.e. djf, and will calculate the metric over all months
    that meet the season criteria. For calculation
    where continuous seasons are important
    iris.aggregated_by is better.

    See an example:

    >>> file1 = os.path.join(conf.DATA_DIR, 'mslp.daily.rcm.viet.nc')
    >>> file2 = os.path.join(conf.DATA_DIR, 'FGOALS-g2_ua@925_nov.nc')
    >>> # load a rcm cube
    ... cube = iris.load_cube(file1)
    >>> seas_min_cubelist = seas_time_stat(cube, metric='min', years=[2000,2000])
    Calculating min for 2000-2000 mam
    Calculating min for 2000-2000 jja
    Calculating min for 2000-2000 son
    Calculating min for 2000-2000 djf
    >>> seas_mean_cubelist = seas_time_stat(cube, \
                                            seas_mons=\
[[1,2],[6,7,8],[6,7,8,9],[10,11]], ext_area=[340, 350, 0,10])
    WARNING - the cube is on a rotated pole, the area you extract might not be \
where you think it is! You can use regular_point_to_rotated to check your ext_area \
lat and lon
    Calculating mean for 2000-2001 jf
    Calculating mean for 2000-2001 jja
    Calculating mean for 2000-2001 jjas
    Calculating mean for 2000-2001 on
    >>> # now load a gcm cube
    ... cube2 = iris.load_cube(file2)
    >>> seas_pc_cubelist = seas_time_stat(cube2, seas_mons=[[11]], \
metric='percentile', pc=95, ext_area=[340, 350, 0,10])
    Calculating percentile for 490-747 n
    >>> # print an example of the output
    ... print(seas_mean_cubelist[1])
    air_pressure_at_sea_level / (Pa)    (grid_latitude: 46; grid_longitude: 23)
         Dimension coordinates:
              grid_latitude                           x                   -
              grid_longitude                          -                   x
         Scalar coordinates:
              season: jja
              season_fullname: junjulaug
              time: 2000-07-16 00:00:00, \
bound=(2000-06-01 00:00:00, 2000-09-01 00:00:00)
         Attributes:
              Conventions: CF-1.5
              STASH: m01s16i222
              source: Data from Met Office Unified Model
         Cell methods:
              mean: time (1 hour)
              mean: time
    """

    if not isinstance(cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    # check the cube contains a coordinate called time
    coord_names = [coord.name() for coord in cube.coords(dim_coords=True)]

    if "time" not in coord_names:
        raise iris.exceptions.CoordinateNotFoundError(
            "No coordinate called 'time' in cube"
        )

    else:
        # if the start and end years are not defined by the user
        # default to using the whole time span of the cube
        if not years:
            time_info = cube.coord("time")
            if not cube.coord("time").has_bounds():
                raise Exception(
                    "Coordinate 'time' does not have bounds. "
                    "Add bounds using the add_bounds function."
                )
            years = [
                time_info.units.num2date(time_info.bounds[0][0]).year,
                time_info.units.num2date(time_info.bounds[-1][1]).year,
            ]

        if ext_area:
            # check the coordinate system of the cube
            cs_str = str(cube.coord_system())
            if cs_str.find("Rotated") != -1:
                print(
                    "WARNING - the cube is on a rotated pole, the area you "
                    "extract might not be where you think it is! You can use "
                    "regular_point_to_rotated to check your ext_area lat and lon"
                )
            if len(ext_area) != 4:
                raise IndexError(
                    "area to extract must contain 4 values, "
                    "currently contains {}".format(str(len(ext_area)))
                )
            else:
                if "grid_latitude" in coord_names:
                    cube = cube.intersection(
                        grid_longitude=(ext_area[0], ext_area[1]),
                        grid_latitude=(ext_area[2], ext_area[3]),
                    )
                elif "latitude" in coord_names:
                    cube = cube.intersection(
                        longitude=(ext_area[0], ext_area[1]),
                        latitude=(ext_area[2], ext_area[3]),
                    )
                else:
                    raise IndexError(
                        "Neither latitude nor grid_latitude coordinates in "
                        "cube, can't extract area"
                    )

        # dictionary of month number to month letter, used to make strings
        # of season names e.g. 'jja'
        month_dict = {
            1: "j",
            2: "f",
            3: "m",
            4: "a",
            5: "m",
            6: "j",
            7: "j",
            8: "a",
            9: "s",
            10: "o",
            11: "n",
            12: "d",
        }
        month_fullname_dict = {
            1: "jan",
            2: "feb",
            3: "mar",
            4: "apr",
            5: "may",
            6: "jun",
            7: "jul",
            8: "aug",
            9: "sep",
            10: "oct",
            11: "nov",
            12: "dec",
        }

        cube_list = iris.cube.CubeList()

        # loop round the seasons
        for season in seas_mons:
            # make strings of the season
            seas_str = []
            seas_fullname_str = []
            for month_num in season:
                month_letter = month_dict[month_num]
                seas_str.append(month_letter)
                month_name = month_fullname_dict[month_num]
                seas_fullname_str.append(month_name)
            season_string = "".join(seas_str)
            season_fullname_string = "".join(seas_fullname_str)

            print(
                (
                    "Calculating {} for {}-{} {}".format(
                        metric, str(years[0]), str(years[1]), season_string
                    )
                )
            )

            # set up an iris constraint for the season
            season_constraint = iris.Constraint(
                time=lambda cell: cell.point.month in season
            )
            # year constraint
            year_constraint = iris.Constraint(
                time=lambda cell: years[0] <= cell.point.year <= years[1]
            )
            # extract the data matching the season and year constraints
            season_cube = cube.extract(year_constraint & season_constraint)

            # make sure season_cube exists
            if season_cube is None:
                raise Exception(
                    "Cube constriants of seas_mons and/or years do not match "
                    "data in the input cube"
                )

            # calculate a time mean
            if metric == "mean":
                cube_stat = season_cube.collapsed("time", iris.analysis.MEAN)
            # calculate standard deviation (D.O.F=1)
            if metric == "std_dev":
                cube_stat = season_cube.collapsed("time", iris.analysis.STD_DEV)
            # calculate minimum
            if metric == "min":
                cube_stat = season_cube.collapsed("time", iris.analysis.MIN)
            # calculate maximum
            if metric == "max":
                cube_stat = season_cube.collapsed("time", iris.analysis.MAX)
            # calculate percentile
            if metric == "percentile":
                if not pc:
                    raise ValueError("percentile to calculate, pc, is not set.")
                if isinstance(pc, int):
                    cube_stat = season_cube.collapsed(
                        "time", iris.analysis.PERCENTILE, percent=pc
                    )
                else:
                    raise TypeError(
                        " pc must be an integer, it is currently {} of type {}".format(
                            pc, type(pc)
                        )
                    )

            # add a coord describing the season
            aux_seas = iris.coords.AuxCoord(
                season_string, long_name="season", units="no_unit"
            )
            cube_stat.add_aux_coord(aux_seas)

            aux_seas_fullname = iris.coords.AuxCoord(
                season_fullname_string, long_name="season_fullname", units="no_unit"
            )
            cube_stat.add_aux_coord(aux_seas_fullname)

            # add seasonal statistic of cube to cube list
            cube_list.append(cube_stat)

    return cube_list


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

    Notes
    -----


    An example:

    >>> file = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
    >>> lat = 6.5
    >>> lon = 289 # on 0-360 degree
    >>> cube = iris.load_cube(file, 'air_temperature')
    >>> rot_lon, rot_lat = regular_point_to_rotated(cube, lon, lat)
    >>> print("{:.3f}".format(rot_lon), "{:.3f}".format(rot_lat))
    -84.330 3.336
    >>> lat = 6.5
    >>> lon = -71 # on -180-180 degree
    >>> rot_lon, rot_lat = regular_point_to_rotated(cube, lon, lat)
    >>> print("{:.3f}".format(rot_lon), "{:.3f}".format(rot_lat))
    -84.330 3.336
    """

    if not isinstance(cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    # get name of y coord
    ycoord = cube.coord(axis="Y", dim_coords=True)
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

    Notes
    -----

    An example:

    >>> file = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
    >>> cube = iris.load_cube(file, 'air_temperature')
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

    if not isinstance(cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    # get name of y coord
    ycoord = cube.coord(axis="Y", dim_coords=True)
    # cartopy.crs.RotatedGeodetic object
    rot_pole = cube.coord(ycoord).coord_system.as_cartopy_crs()
    # "regular" lon/lat coord system
    ll = ccrs.Geodetic()
    # Transform the  rotated lon lat point into regular coordinates.
    reg_lon, reg_lat = ll.transform_point(rot_lon, rot_lat, rot_pole)

    return reg_lon, reg_lat


def windspeed(u_cube, v_cube):

    """
    This function calculates wind speed.

    args
    ----
    u_cube: cube of eastward wind
    v_cube: cube of northward wind

    Returns
    -------
    windspeed_cube: cube of wind speed in same units as input cubes.


    A simple example:

    >>> file = os.path.join(conf.DATA_DIR, 'gcm_monthly.pp')
    >>> u_cube = iris.load_cube(file, 'x_wind')
    >>> v_cube = iris.load_cube(file, 'y_wind')
    >>> ws = windspeed(u_cube, v_cube)
    >>> ws.attributes['formula']
    'sqrt(u**2, v**2)'
    >>> print(np.min(ws.data),np.max(ws.data))
    0.010195612 13.077045
    >>> ws.standard_name
    'wind_speed'
    """

    if not isinstance(u_cube, iris.cube.Cube) or not isinstance(v_cube, iris.cube.Cube):
        raise TypeError("Input is not a cube")

    if u_cube.units != getattr(v_cube, "units", u_cube.units):
        raise ValueError(
            "units do not match, {} and {}".format(u_cube.units, v_cube.units)
        )

    # cube to put the windspeed in
    windspeed_cube = u_cube.copy()
    # adjust meta data
    windspeed_cube.standard_name = "wind_speed"
    if "STASH" in windspeed_cube.attributes:
        windspeed_cube.attributes.pop("STASH", None)
    windspeed_cube.attributes["formula"] = "sqrt(u**2, v**2)"

    windspeed_cube.data = np.sqrt(u_cube.data ** 2 + v_cube.data ** 2)

    return windspeed_cube


def wind_direction(u_cube, v_cube, unrotate=True):

    """
    Adapted from UKCP common_analysis.py
    (http://fcm1/projects/UKCPClimateServices/browser/trunk/code/)

    This function calculates the direction of the wind vector,
    which is the "to" direction (e.g. Northwards)
    (i.e. NOT Northerly, the "from" direction!)
    and the CF Convensions say it should be measured
    clockwise from North. If the data is on rotated pole, the
    rotate_winds iris function is applied as a default, but this
    can be turned off.

    Note: If you are unsure whether your winds need to be
    unrotated you can use http://www-nwp/umdoc/pages/stashtech.html
    and navigate to the relevant UM version and stash code:
        -    Rotate=0 means data is relative to the model grid and DOES need to
             be unrotated.
        -    Rotate=1 means data is relative to the lat-lon grid and
             DOES NOT need unrotating.

    args
    ----
    u_cube: cube of eastward wind
    v_cube: cube of northward wind
    unrotate: boolean, defaults to True. If true and data is rotated pole,
              the winds are unrotated, if set to False, they are not.

    Returns
    -------
    angle_cube: cube of wind direction in degrees (wind direction 'to' not 'from')


    A simple example:

    >>> file = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
    >>> u_cube = iris.load_cube(file, 'x_wind')
    >>> v_cube = iris.load_cube(file, 'y_wind')
    >>> angle = wind_direction(u_cube, v_cube)
    data is on rotated coord system, un-rotating . . .
    >>> angle.attributes['formula']
    '(-(arctan2(v, u)*180/pi)+90)%360'
    >>> print(np.min(angle.data),np.max(angle.data))
    0.0181427 359.99008
    >>> angle.standard_name
    'wind_to_direction'
    >>> # Now take the same data and calculate the wind direction WITHOUT rotating
    ... angle_unrot = wind_direction(u_cube, v_cube, unrotate=False)
    >>> # Print the difference between wind direction data
    ... # where unrotate=True unrotate=False to illustrate
    ... # the importance of getting the correct unrotate option
    ... print(angle.data[0,100,:10] - angle_unrot.data[0,100,:10])
    [-26.285324 -26.203125 -26.120728 -26.038239 -25.955551 -25.872742
     -25.78981  -25.70668  -25.623428 -25.539993]
    """

    if u_cube.units != getattr(v_cube, "units", u_cube.units):
        raise ValueError(
            "units do not match, {} and {}".format(u_cube.units, v_cube.units)
        )

    # check if data is on rotated pole, unrotate if necessary
    cs_str = str(u_cube.coord_system())
    if cs_str.find("Rotated") != -1:
        if unrotate:
            print("data is on rotated coord system, un-rotating . . .")
            target_cs = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
            u_cube, v_cube = iris.analysis.cartography.rotate_winds(
                u_cube, v_cube, target_cs
            )

    # create a cube for the output and adjust meta data
    angle_cube = u_cube.copy()
    angle_cube.units = "degree"
    angle_cube.standard_name = "wind_to_direction"
    angle_cube.long_name = "wind vector direction"
    angle_cube.var_name = "angle"
    if "STASH" in angle_cube.attributes:
        angle_cube.attributes.pop("STASH", None)
    angle_cube.attributes[
        "direction"
    ] = "Angle of wind vector measured clockwise from Northwards"
    angle_cube.attributes["formula"] = "(-(arctan2(v, u)*180/pi)+90)%360"

    angle_cube.data = np.arctan2(v_cube.data, u_cube.data) * 180.0 / np.pi
    # That gives the angle of the vector in degrees, anticlockwise from Eastwards.
    # (in the range -180 to +180)
    # But we want the bearing clockwise from Northwards (0,360), so:
    angle_cube.data = (-angle_cube.data + 90.0) % 360

    return angle_cube


if __name__ == "__main__":
    doctest.testmod()
