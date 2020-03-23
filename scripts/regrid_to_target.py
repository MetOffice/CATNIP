"""
Author: Grace Redmond
Date: 04/2019
"""

import iris
import iris.analysis as ia


def regrid_to_target(cube, target_cube, method='linear', extrap='mask', mdtol=0.5):
    """
    Takes in two cubes, and regrids one onto the grid
    of the other. Optional arguments include the method
    of regridding, default is linear. The method of
    extrapolation (if it is required), the default is
    to mask the data, even if the source data is not
    a masked array. And, if the method is areaweighted,
    choose a missing data tolerance, default is 0.5.
    For full info, see https://scitools.org.uk/iris/docs/latest/userguide/interpolation_and_regridding.html

    Note: areaweighted is VERY picky, it will not allow you to regrid using
    this method if the two input cubes are not on the same coordinate system,
    and both input grids must also contain monotonic, bounded, 1D spatial coordinates.

    args
    ----
    cube: cube you want to regrid
    target_cube: cube on the target grid
    method: method of regridding, options are 'linear', 'nearest' and 'areaweighted'.
    extrap: extraopolation mode, options are 'mask', 'nan', 'error' and 'nanmask'
    mdtol: tolerated fraction of masked data in any given target grid-box, only used if method='areaweighted', between 0 and 1.

    Returns
    -------
    cube_reg: input cube on the grid of target_cube

    An example:

    >>> cube = iris.load_cube('/project/ciid/projects/catnip/stock_cubes/gcm_monthly.pp', 'air_temperature')
    >>> tgrid = iris.load_cube('/project/ciid/projects/catnip/stock_cubes/rcm_monthly.pp', 'air_temperature')
    >>> cube_reg = regrid_to_target(cube, tgrid)
    regridding from GeogCS(6371229.0) to RotatedGeogCS(39.25, 198.0, ellipsoid=GeogCS(6371229.0)) using method linear
    >>> print(cube.shape, tgrid.shape)
    (145, 192) (2, 433, 444)
    >>> print(cube_reg.shape)
    (433, 444)
    """

    target_cs = target_cube.coord(axis='x').coord_system
    orig_cs = cube.coord(axis='x').coord_system

    # get coord names for cube
    # Longitude
    xcoord = cube.coord(axis='X', dim_coords=True)
    # Latitude
    ycoord = cube.coord(axis='Y', dim_coords=True)
    # get coord names for target_cube
    # Longitude
    t_xcoord = target_cube.coord(axis='X', dim_coords=True)
    # Latitude
    t_ycoord = target_cube.coord(axis='Y', dim_coords=True)


    if method == 'linear':
        scheme = iris.analysis.Linear(extrapolation_mode=extrap)

    if method == 'nearest':
        scheme = iris.analysis.Nearest(extrapolation_mode=extrap)

    # areaweighted is VERY picky and often can't be used.
    if method == 'areaweighted':
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

    print("regridding from {} to {} using method {}".format(str(orig_cs), str(target_cs), method))

    cube_reg = cube.regrid(target_cube, scheme)

    return cube_reg


def set_regridder(cube, target_cube, method='linear', extrap='mask', mdtol=0.5):
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
    For full info, see https://scitools.org.uk/iris/docs/latest/userguide/interpolation_and_regridding.html

    Note: areaweighted is VERY picky, it will not allow you to regrid using
    this method if the two input cubes are not on the same coordinate system,
    and both input grids must also contain monotonic, bounded, 1D spatial coordinates.

    args
    ----
    cube: cube you want to regrid
    target_cube: cube on the target grid
    method: method of regridding, options are 'linear', 'nearest' and 'areaweighted'.
    extrap: extraopolation mode, options are 'mask', 'nan', 'error' and 'nanmask'
    mdtol: tolerated fraction of masked data in any given target grid-box, only used if method='areaweighted', between 0 and 1.

    Returns
    -------
    regridder: a cached regridder which can be used on any iris cube which has the same grid as cube.

    An example:

    >>> cube = iris.load_cube('/project/ciid/projects/catnip/stock_cubes/gcm_monthly.pp', 'air_temperature')
    >>> tgrid = iris.load_cube('/project/ciid/projects/catnip/stock_cubes/rcm_monthly.pp', 'air_temperature')
    >>> regridder = set_regridder(cube, tgrid)
    >>> cube2 = iris.load_cube('/project/ciid/projects/catnip/stock_cubes/gcm_monthly.pp', 'cloud_area_fraction')
    >>> print(cube2.shape)
    (145, 192)
    >>> regridder(cube2)
    <iris 'Cube' of cloud_area_fraction / (1) (grid_latitude: 433; grid_longitude: 444)>
    """

    target_cs = target_cube.coord(axis='x').coord_system
    orig_cs = cube.coord(axis='x').coord_system

        # get coord names for cube
    # Longitude
    xcoord = cube.coord(axis='X', dim_coords=True)
    # Latitude
    ycoord = cube.coord(axis='Y', dim_coords=True)
    # get coord names for target_cube
    # Longitude
    t_xcoord = target_cube.coord(axis='X', dim_coords=True)
    # Latitude
    t_ycoord = target_cube.coord(axis='Y', dim_coords=True)

    if method == 'linear':
        regridder = iris.analysis.Linear(extrapolation_mode=extrap).regridder(cube, target_cube)

    if method == 'nearest':
        regridder = iris.analysis.Nearest(extrapolation_mode=extrap).regridder(cube, target_cube)

    if method == 'areaweighted':
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
