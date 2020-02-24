"""
Authors:Dave Rowell, Grace Redmond
"""

import numpy as np
from scipy.stats.distributions import t
import matplotlib.pyplot as plt


def linear_regress(xi, yi):
    """
    Solves y = mx + c by returning the
    least squares solution to a linear matrix
    equation. Expects two numpy arrays of dimension 1.
    TODO: use sklearn to perform regression

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

    A simple example:
    >>> x = np.array([1, 4, 2, 7, 0, 6, 3, 3, 1, 9])
    >>> y = np.array([5, 6, 2, 9, 1, 4, 7, 8, 2, 6])
    >>> grad, intcp, xp, yp, sum_res = linear_regress(x, y)
    >>> print('gradient', "{:.2f}".format(grad))
    gradient 0.54
    >>> print('intercept', "{:.2f}".format(intcp))
    intercept 3.07
    """

    if np.ndim(xi) != 1 or np.ndim(yi) != 1:
        raise ValueError('xi and yi must have dinemsion 1, not xi \
            {} and yi {}'.format(str(np.ndim(xi)), str(np.ndim(yi))))
    else:
        # Return the least-squares solution to a linear matrix equation
        regression = np.linalg.lstsq(np.vstack([xi, np.ones(len(xi))]).T, yi,rcond=None)

        # Get the slope and the intercept
        grad, intcp = regression[0]

        # sum of residuals: squared Euclidean 2-norm for each column in yi - xi*x
        sum_res = regression[1]

        xmin, xmax = np.min(xi), np.max(xi)
        xpts = [xmin, xmax]
        ypts = grad*np.array(xpts)+intcp

        return grad, intcp, xpts, ypts, sum_res


def ci_interval(xi, yi, alpha=0.05):

    """
    Calculates  Confidence interval (default 95%) parameters for two
    numpy arrays of dimension 1. Returns include the gradient
    and intercept of the confidence interval.

    It also returns vectors for confidence interval plotting:
    -  the high/low confidence interval of the slope
    -  the high low curves of confidence interval of yi.

    Parameters have been calculated using von Storch &
    Zwiers Statisical Analysis in Climate Research
    Sect.8.3.7 and 8.3.10

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
    xreg: x values spanning xmin to xmax linearly spaced, for plotting against  yi CI curve.
    y_conf_int_lo: for plotting, lower bound of CI region for yi
    y_conf_int_hi: for plotting, upper bound of CI region for yi

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
        raise ValueError('The input fields do not have the same shape, \
            {} and {}'.format(str(xi.shape), str(yi.shape)))

    print(('Calculating the {}% confidence interval'.format(str((1-alpha)*100))))
    # number of points
    n = len(xi)
    # degrees of freedom
    dof = n - 2 # assuming 2 parameters
    # student-t value for the dof and confidence level
    # Note, ppf - Percent point function (inverse of cdf - percentiles).
    t_val = t.ppf(1.0-alpha/2., dof)


    # Return the least-squares solution to a linear matrix equation
    slope, intcp, xp, yp, sum_res = linear_regress(xi, yi)

    # If yi is 1-dimensional, sum_res is a (1,) shape array.
    # Use this to calculate confidence intervals for plotting.
    if sum_res.shape == (1,):
        # standard error
        sd_err = np.sqrt(sum_res/(dof))[0]
        # calculate the sum of the squares of the difference
        # between each x and the mean x value
        sxx = np.sum((xi-np.mean(xi))**2)
        if sxx == 0.0:
            raise ValueError('Sum of squares of difference is 0')

        # CI of slope: Formulated from vonStorch & Zwiers Sect.8.3.7
        slope_conf_int = (t_val * sd_err) / np.sqrt(sxx)
        # lower bound of slope using CI interval
        slope_lo = slope - slope_conf_int
        # upper bound of slope using CI interval
        slope_hi = slope + slope_conf_int
        xmin, xmax = np.min(xi), np.max(xi)
        # for plotting CI slope you want
        xpts = xmin, xmax
        slope_lo_pts = np.mean(yi) + slope_lo*([xmin, xmax] - np.mean(xi))
        slope_hi_pts = np.mean(yi) + slope_hi*([xmin, xmax] - np.mean(xi))

        # get regularly spaced np array of x points
        xreg = np.linspace(xmin, xmax, 101)
        # Population yi CI: Formulated from vonStorch & Zwiers Sect.8.3.10
        # CI for the mean of the response variable
        yfact = np.sqrt((1.0/n) + (((xreg-np.mean(xi))**2)/sxx))
        # 95% CI
        ymean_conf_int = (t_val * sd_err) * yfact
        # get the lines for plotting ymean CI
        y_conf_int_hi = (slope*xreg)+intcp+ymean_conf_int
        y_conf_int_lo = (slope*xreg)+intcp-ymean_conf_int

        # Intercept CI, using population y CI at x=0
        # Note, this isn't meaningful if x=0 is not physically meaningful
        yfact0 = np.sqrt((1.0/n) + ((np.mean(xi)**2)/sxx))
        intcp_conf_int = (t_val * sd_err) * yfact0
        intcp_lo = intcp - intcp_conf_int
        intcp_hi = intcp + intcp_conf_int

        return slope_conf_int, intcp_conf_int, xpts, slope_lo_pts, \
                    slope_hi_pts, xreg, y_conf_int_lo, y_conf_int_hi


def plot_regress(x, y, best_fit=True, CI_region=True, CI_slope=False, alpha=0.05, num_plot=111, title='', xlabel='', ylabel=''):

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
    slope_conf_int, intcp_conf_int, xpts, slope_lo_pts, slope_hi_pts, \
        xreg, y_conf_int_lo, y_conf_int_hi = ci_interval(x, y, alpha)

    # calculate the correlation coefficient for x and y
    corr = "{:.3f}".format(np.corrcoef(x, y)[0][1])
    print(('Correlation coefficent for x and y: ' + corr))

    print(('Plotting . . . ' + title))
    plt.subplot(num_plot)
    plt.scatter(x, y)
    if best_fit:
        plt.plot(xp, yp, color='k', linewidth=1.5, label='y=mx+c')
    if CI_slope:
        plt.plot(xpts, slope_lo_pts, xpts, slope_hi_pts, linestyle=':', color='g', linewidth=1.5)
    if CI_region:
        plt.plot(xreg, y_conf_int_lo, linestyle='--', color='orange', linewidth=1.5,
                 label='{}% confidence region'.format(str((1-alpha)*100)))
        plt.plot(xreg, y_conf_int_hi, linestyle='--', color='orange', linewidth=1.5)
    plt.xlim(xpts)
    plt.title(title + '\n Correlation coefficient: ' + corr)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(loc='best', fontsize=10)

if __name__ == "__main__":

    import doctest
    doctest.testmod()
