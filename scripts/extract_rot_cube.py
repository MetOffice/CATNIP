import iris
from ascend import shape
import numpy as np
from add_aux_unrotated_coords import add_aux_unrotated_coords


def extract_rot_cube(cube, min_lat, min_lon, max_lat, max_lon):
    """
    Function etracts the specific region from the cube.

    args
    ----
    cube: cube on rotated coord system, used as reference grid for transformation.

    Returns
    -------
    min_lat: The minimum latitude point of the desired extracted cube.
    min_lon: The minimum longitude point of the desired extracted cube.
    max_lat: The maximum latitude point of the desired extracted cube.
    max_lon: The maximum longitude point of the desired extracted cube.

    An example:
    >>> cube = iris.load_cube('/project/ciid/projects/ciid_tools/stock_cubes/rcm_monthly.pp', 'air_temperature')
    >>> min_lat = 50
    >>> min_lon = -10
    >>> max_lat = 60
    >>> max_lon = 0
    >>> extracted_cube = extract_rot_cube(cube, min_lat, min_lon, max_lat, max_lon)
    >>> print(np.max(extracted_cube.coord('latitude').points))
    61.47165097005264
    >>> print(np.min(extracted_cube.coord('latitude').points))
    48.213032844268646
    >>> print(np.max(extracted_cube.coord('longitude').points))
    3.642576550089792
    >>> print(np.min(extracted_cube.coord('longitude').points))
    -16.385571344717235
    """
    # adding unrotated coords to the cube
    add_aux_unrotated_coords(cube)

    # use ASCEND package to cut the area out
    corners = [(min_lon, min_lat), (min_lon, max_lat),
               (max_lon, max_lat), (max_lon, min_lat)]
    rectangle = shape.create(corners, {'shape': 'rectangle'}, 'Polygon')
    extracted_cube = rectangle.extract_subcube(cube)


    return extracted_cube





if __name__ == "__main__":
    import doctest
    doctest.testmod()
