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


import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import iris.quickplot as qplt
import doctest
import iris
from catnip.analysis import linear_regress, ci_interval
import numpy as np


def vector_plot(u_cube, v_cube, unrotate=False, npts=30, num_plot=111, title=""):
    """
    A plotting function to produce a quick wind
    vector plot. Output is a plot with windspeed
    contours and wind vectors. Optionally the
    u and v components can be unrotated.

    Note: If you are unsure whether your winds need to be
    unrotated you can use http://www-nwp/umdoc/pages/stashtech.html
    and navigate to the relevant UM version and stash code:
        -    Rotate=0 means data is relative to the model grid and DOES need
             to be unrotated.
        -    Rotate=1 means data is relative to the lat-lon grid and DOES NOT
             need unrotating.

    args
    ----
    u_cube: iris 2D cube of u wind component
    v_cube: iris 2D cube of v wind component
    unrotate: if set to True will unrotate wind vectors, default is False.
    npts: integer, plot can look crowded, so plot vector arrow every npts
          (1=every point, 50=every 50th point), defaults to 30.
    num_plot: if subplots required the plot number e.g. 121 can be specified
              here. Defaults to 111.
    title: plot title, must be a string, defaults to blank.
    """

    # x and y coords
    try:
        x = u_cube.coord(axis="x")
    except iris.exceptions.CoordinateNotFoundError:
        print("Error: more than one x coord found")
    try:
        y = u_cube.coord(axis="y")
    except iris.exceptions.CoordinateNotFoundError:
        print("Error: more than one y coord found")

    # if the wind vectors need to be unrotated
    # they are in the statement below
    if unrotate:
        cs_str = str(u_cube.coord_system())
        if cs_str.find("Rotated") == -1:
            raise Exception(
                "Will not unrotate data not on a rotated pole, "
                "unrotate must be set to False"
            )
        else:
            print("unrotating wind vectors . . . ")
            target_cs = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
            u_cube, v_cube = iris.analysis.cartography.rotate_winds(
                u_cube, v_cube, target_cs
            )

    # Create a cube containing the wind speed
    windspeed_cube = (u_cube ** 2 + v_cube ** 2) ** 0.5

    # plot
    transform = x.coord_system.as_cartopy_projection()
    # use coord_system of input data to define plot projection
    ax = plt.subplot(num_plot, projection=transform)
    qplt.contourf(windspeed_cube, 20)
    ax.quiver(
        u_cube.coord(x.standard_name).points[::npts],
        v_cube.coord(y.standard_name).points[::npts],
        u_cube.data[::npts, ::npts],
        v_cube.data[::npts, ::npts],
    )
    # OTHER OPTIONS FOR QUIVER: scale = 1, headwidth = 3, width = 0.0015)
    ax.coastlines()
    ax.set_extent([x.points[0], x.points[-1], y.points[0], y.points[-1]], transform)
    plt.title(title)
    print("plot {} created".format(title))


def plot_regress(
    x,
    y,
    best_fit=True,
    CI_region=True,
    CI_slope=False,
    alpha=0.05,
    num_plot=111,
    title="",
    xlabel="",
    ylabel="",
):
    """
    Produces an x and y scatter plot and calculates the correlation
    coefficient, as a default it will also plot the line of best fit
    (using linear regression), and the 95% confidence region.

    args
    ----
    x: numpy array of dimension 1
    y: dependant variable, numpy array of dimension 1
    best_fit: True or False depending on whether a line of best fit is
              required, default is set to True.
    CI_region: True or False depending on whether plotting the confidence
              region is required, default is set to True.
    CI_slope: True or False depending on whether the CI slope lines
               are required, default is set to False.
    alpha: required confidence interval (e.g. 0.05 for 95%). Default is 0.05.
    num_plot: polot/subplot position, default is 111.
    title: title of plot.
    xlabel: x axis label.
    ylabel: y axis label.

    Returns
    -------
    A scatter plot of x and y, can be visualised using
    plt.show() or saved using plt.savefig()
    """

    # Calculate the line of best fit, y = mx + c
    grad, intcp, xp, yp = linear_regress(x, y)

    # Calculate the confidence interval
    (
        slope_conf_int,
        intcp_conf_int,
        xpts,
        slope_lo_pts,
        slope_hi_pts,
        xreg,
        y_conf_int_lo,
        y_conf_int_hi,
    ) = ci_interval(x, y, alpha)

    # calculate the correlation coefficient for x and y
    corr = "{:.3f}".format(np.corrcoef(x, y)[0][1])
    print(("Correlation coefficent for x and y: " + corr))

    print(("Plotting . . . " + title))
    plt.subplot(num_plot)
    plt.scatter(x, y)
    if best_fit:
        plt.plot(xp, yp, color="k", linewidth=1.5, label="y=mx+c")
    if CI_slope:
        plt.plot(
            xpts,
            slope_lo_pts,
            xpts,
            slope_hi_pts,
            linestyle=":",
            color="g",
            linewidth=1.5,
        )
    if CI_region:
        plt.plot(
            xreg,
            y_conf_int_lo,
            linestyle="--",
            color="orange",
            linewidth=1.5,
            label="{}% confidence region".format(str((1 - alpha) * 100)),
        )
        plt.plot(xreg, y_conf_int_hi, linestyle="--", color="orange", linewidth=1.5)
    plt.xlim(xpts)
    plt.title(title + "\n Correlation coefficient: " + corr)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc="best", fontsize=10)


if __name__ == "__main__":
    doctest.testmod()
