"""
Author: Hamish Steptoe
Edited and added to by: Grace Redmond
"""

import iris


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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
