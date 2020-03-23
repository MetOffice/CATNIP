"""
Author: Grace Redmond
"""

import iris
from six import string_types


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

    >>> cube = iris.load_cube('/project/ciid/projects/catnip/stock_cubes/mslp.daily.rcm.viet.nc')
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

if __name__ == "__main__":
    import doctest
    doctest.testmod()
