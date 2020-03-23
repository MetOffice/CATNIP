"""
Author: Grace Redmond
"""

import iris


def seas_time_stat(cube, seas_mons=[[3, 4, 5], [6, 7, 8], [9, 10, 11], [12, 1, 2]],
                   metric='mean', pc=[], years=[], ext_area=[]):
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

    >>> # load a rcm cube
    ... cube = iris.load_cube('/project/ciid/projects/catnip/stock_cubes/mslp.daily.rcm.viet.nc')
    >>> seas_min_cubelist = seas_time_stat(cube, metric='min', years=[2000,2000])
    Calculating min for 2000-2000 mam
    Calculating min for 2000-2000 jja
    Calculating min for 2000-2000 son
    Calculating min for 2000-2000 djf
    >>> seas_mean_cubelist = seas_time_stat(cube, seas_mons=[[1,2],[6,7,8],[6,7,8,9],[10,11]], ext_area=[340, 350, 0,10])
    WARNING - the cube is on a rotated pole, the area you extract might not be where you think it is! You can use regular_point_to_rotated to check your ext_area lat and lon
    Calculating mean for 2000-2001 jf
    Calculating mean for 2000-2001 jja
    Calculating mean for 2000-2001 jjas
    Calculating mean for 2000-2001 on
    >>> # now load a gcm cube
    ... cube2 = iris.load_cube('/project/ciid/projects/catnip/stock_cubes/FGOALS-g2_ua@925_nov.nc')
    >>> seas_pc_cubelist = seas_time_stat(cube2, seas_mons=[[11]], metric='percentile', pc=95, ext_area=[340, 350, 0,10])
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
              time: 2000-07-16 00:00:00, bound=(2000-06-01 00:00:00, 2000-09-01 00:00:00)
         Attributes:
              Conventions: CF-1.5
              STASH: m01s16i222
              source: Data from Met Office Unified Model
         Cell methods:
              mean: time (1 hour)
              mean: time
    """

    # check the cube contains a coordinate called time
    coord_names = [coord.name() for coord in cube.coords(dim_coords=True)]
    if 'time' in coord_names:
        
        # if the start and end years are not defined by the user
        # default to using the whole time span of the cube
        if not years:
            time_info = cube.coord('time')
            if not cube.coord('time').has_bounds():
                raise Exception("Coordinate 'time' does not have bounds. Add bounds using the add_bounds function.")
            years = [time_info.units.num2date(time_info.bounds[0][0]).year,
                     time_info.units.num2date(time_info.bounds[-1][1]).year]

        if ext_area:
            # check the coordinate system of the cube
            cs_str= str(cube.coord_system())
            if cs_str.find('Rotated') != -1:
                print('WARNING - the cube is on a rotated pole, the area you extract might not be where you think it is! You can use regular_point_to_rotated to check your ext_area lat and lon')
            if len(ext_area) != 4:
                raise IndexError("area to extract must contain 4 values, currently contains {}".format(str(len(ext_area))))
            else:
                if 'grid_latitude' in coord_names:
                    cube = cube.intersection(grid_longitude=(ext_area[0], ext_area[1]),
                                             grid_latitude=(ext_area[2], ext_area[3]))
                elif 'latitude' in coord_names:
                    cube = cube.intersection(longitude=(ext_area[0], ext_area[1]),
                                             latitude=(ext_area[2], ext_area[3]))
                else:
                    raise IndexError("Neither latitude nor grid_latitude coordinates in cube, can't extract area")

        # dictionary of month number to month letter, used to make strings
        # of season names e.g. 'jja'
        month_dict = {1: 'j', 2: 'f', 3: 'm', 4: 'a', 5: 'm', 6: 'j',
                      7: 'j', 8: 'a', 9: 's', 10: 'o', 11: 'n', 12: 'd'}
        month_fullname_dict = {1: 'jan', 2: 'feb', 3: 'mar', 4: 'apr', 5: 'may', 6: 'jun',
                      7: 'jul', 8: 'aug', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dec'}


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

            print(('Calculating {} for {}-{} {}'.format(metric, str(years[0]),
                                                        str(years[1]), season_string)))

            # set up an iris constraint for the season
            season_constraint = iris.Constraint(time=lambda cell: cell.point.month in season)
            # year constraint
            year_constraint = iris.Constraint(time=lambda cell: years[0]
                                              <= cell.point.year <= years[1])
            # extract the data matching the season and year constraints
            season_cube = cube.extract(year_constraint & season_constraint) 
            
            # make sure season_cube exists
            if season_cube is None:
                raise Exception("Cube constriants of seas_mons and/or years do not match data in the input cube")

            # calculate a time mean
            if metric == 'mean':
                cube_stat = season_cube.collapsed('time', iris.analysis.MEAN)
            # calculate standard deviation (D.O.F=1)
            if metric == 'std_dev':
                cube_stat = season_cube.collapsed('time', iris.analysis.STD_DEV)
            # calculate minimum
            if metric == 'min':
                cube_stat = season_cube.collapsed('time', iris.analysis.MIN)
            # calculate maximum
            if metric == 'max':
                cube_stat = season_cube.collapsed('time', iris.analysis.MAX)
            # calculate percentile
            if metric == 'percentile':
                if not pc:
                    raise ValueError('percentile to calculate, pc, is not set.')
                if isinstance(pc, int):
                    cube_stat = season_cube.collapsed('time', iris.analysis.PERCENTILE,
                                                      percent=pc)
                else:
                    raise TypeError(' pc must be an integer, it is currently {} of type {}'.format(pc, type(pc)))

            # add a coord describing the season
            aux_seas = iris.coords.AuxCoord(season_string, long_name='season',
                                            units='no_unit')
            cube_stat.add_aux_coord(aux_seas)

            aux_seas_fullname = iris.coords.AuxCoord(season_fullname_string, long_name='season_fullname',
                                            units='no_unit')
            cube_stat.add_aux_coord(aux_seas_fullname)

            # add seasonal statistic of cube to cube list
            cube_list.append(cube_stat)

        return cube_list

    else:
        raise Exception("No coordinate called 'time' in cube")

if __name__ == "__main__":
    import doctest
    doctest.testmod()
