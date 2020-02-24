#Author: Grace Redmond


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import iris.quickplot as qplt
import cartopy
import cartopy.feature as cfeat
import cartopy.crs as ccrs
import numpy as np
import iris

def vector_plot(u_cube, v_cube, unrotate=False, npts=30, num_plot=111, title=""):

    """
    A plotting function to produce a quick wind 
    vector plot. Output is a plot with windspeed
    contours and wind vectors. Optionally the 
    u and v components can be unrotated.

    Note: If you are unsure whether your winds need to be
    unrotated you can use http://www-nwp/umdoc/pages/stashtech.html
    and navigate to the relevant UM version and stash code:
        -    Rotate=0 means data is relative to the model grid and DOES need to be unrotated.
        -    Rotate=1 means data is relative to the lat-lon grid and DOES NOT need unrotating.

    args
    ----
    u_cube: iris 2D cube of u wind component
    v_cube: iris 2D cube of v wind component
    unrotate: if set to True will unrotate wind vectors, default is False.
    npts: integer, plot can look crowded, so plot vector arrow every npts (1=every point, 50=every 50th point), defaults to 30.
    num_plot: if subplots required the plot number e.g. 121 can be specified here. Defaults to 111.
    title: plot title, must be a string, defaults to blank.
    """

    # x and y coords
    try:
        x = u_cube.coord(axis='x')
    except iris.exceptions.CoordinateNotFoundError:
        print('Error: more than one x coord found')
    try:
        y = u_cube.coord(axis='y')
    except iris.exceptions.CoordinateNotFoundError:
        print('Error: more than one y coord found')

    # if the wind vectors need to be unrotated
    # they are in the statement below
    if unrotate:
        cs_str = str(u_cube.coord_system())
        if cs_str.find('Rotated') == -1:
            raise Exception("Will not unrotate data not on a rotated pole, unrotate must be set to False")
        else:
            print('unrotating wind vectors . . . ')
            target_cs = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
            u_cube, v_cube = iris.analysis.cartography.rotate_winds(u_cube, v_cube, target_cs)


    # Create a cube containing the wind speed
    windspeed_cube = (u_cube ** 2 + v_cube ** 2) ** 0.5

    # plot
    transform = x.coord_system.as_cartopy_projection()
    # use coord_system of input data to define plot projection
    ax = plt.subplot(num_plot, projection=transform)
    qplt.contourf(windspeed_cube, 20)
    ax.quiver(u_cube.coord(x.standard_name).points[::npts], v_cube.coord(y.standard_name).points[::npts], 
              u_cube.data[::npts,::npts], v_cube.data[::npts,::npts]) 
    #OTHER OPTIONS FOR QUIVER: scale = 1, headwidth = 3, width = 0.0015)
    ax.coastlines()
    ax.set_extent([x.points[0],x.points[-1],y.points[0],y.points[-1]],transform)
    plt.title(title)    
    print("plot {} created".format(title))


if __name__ == "__main__":

    import doctest
    doctest.testmod()

