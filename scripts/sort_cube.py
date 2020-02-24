import numpy as np

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


    e.g.

    >>> import iris
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
    assert coord_to_sort.ndim == 1, 'One dim coords only please.'

    # create sorted indices of coord
    dim, = cube.coord_dims(coord_to_sort)
    index = [slice(None)] * cube.ndim
    index[dim] = np.argsort(coord_to_sort.points)

    # apply to cube and return
    return cube[tuple(index)]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
