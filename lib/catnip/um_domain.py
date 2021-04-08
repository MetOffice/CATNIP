'''
Plot the LAM domains
Variable resolution not supported. Old dynamics
is supported.
'''
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import iris
import matplotlib.pyplot as plt
import numpy as np
import os

class UmDomain:
    '''
    A class to hold the information needed
    to define a model domain in the MetUM
    '''

    def __init__(self, delta_lat, delta_lon,
                 frstlata, frstlona,
                 polelata, polelona,
                 global_row_length, global_rows,
                 old_dynam=False):

        'Initialise the class holding a rotated pole domain'
        self.delta_lat = delta_lat  # lattitude grid spacing
        self.delta_lon = delta_lon  # longitude grid spacing
        self.frstlata = frstlata    # first latitude
        self.frstlona = frstlona    # first lon
        self.polelata = polelata    # latidude of rotated pole
        self.polelona = polelona    # longitude of rotated pole
        self.global_row_length = global_row_length # no of columns
        self.global_rows = global_rows             # no of rows
        self.old_dynam = old_dynam  # is this an old dynamics grid?

        self.theta_cube_2d = None
        self.theta_cube_3d = None

    def last_lon_lat(self):
        'get the last lat and lon in the grid'
        # NB is the right for old dynamics? Only matters
        # if going to use it to make old dynamics cubes

        lastlona = (self.frstlona +
                    (self.global_row_length - 1) * self.delta_lon)
        lastlata = (self.frstlata +
                    (self.global_rows - 1) * self.delta_lat)

        return lastlona, lastlata

    def make_2d_theta_cube(self):
        '''
        using the information on the grid, make a 2D cube
        of theta
        '''

        # calculate the lat and lon arrays
        lastlona, lastlata = self.last_lon_lat()
        theta_lon = np.linspace(self.frstlona, lastlona,
                                     num=self.global_row_length)
        theta_lat = np.linspace(self.frstlata, lastlata,
                                     num=self.global_rows)

        # create a 2D numpy ndarray
        theta_data = np.zeros((len(theta_lon), len(theta_lat)))

        lon_coord = iris.coords.DimCoord(theta_lon,
            standard_name='grid_longitude',
            units='degrees',
            coord_system=
                iris.coord_systems.RotatedGeogCS(self.polelata, self.polelona))
        lat_coord = iris.coords.DimCoord(theta_lat,
            standard_name='grid_latitude',
            units='degrees',
            coord_system=
                iris.coord_systems.RotatedGeogCS(self.polelata, self.polelona)
            )

        self.theta_cube_2d = iris.cube.Cube(theta_data, long_name = 'air_potential_temperature',
                                    units = 'K',
                                    dim_coords_and_dims=[
                                        (lon_coord, 0),
                                        (lat_coord, 1)])

        return self.theta_cube_2d

    def get_corners(self):
        '''
        Find the lat/lon of the extreme corners of the
        domain.
        Note that for old dynamics first lat and lon
        are the grid box centres whereas for ND/EG
        they are the grid box corners
        '''

        # Old dynamics
        if self.old_dynam:

            # add code here
            # longitude - as this refers to centres,
            # we have to subtract half a grid box
            self.minlon = self.frstlona - self.delta_lon/2.
            # latitude - not that frstlona is
            # the maximum latitude
            self.minlat = (self.frstlata
                           - self.delta_lon * (self.global_rows - 0.5))

            # max lon/lat
            self.maxlon = (self.frstlona
                           + (self.global_row_length -0.5) * self.delta_lon)
            self.maxlat = self.frstlata + self.delta_lat/2.


        # New dynamics/ENDGAME
        else:

            # min lon and min lat are same as firstlona etc
            self.minlon = self.frstlona
            self.minlat = self.frstlata

            # as this refers to grid box corners not
            # centres we multiply by N not by N-1
            self.maxlat = (self.frstlata
                           + self.global_rows * self.delta_lat)

            self.maxlon = (self.frstlona
                           + self.global_row_length * self.delta_lon)


        return self.minlat, self.minlon, self.maxlat, self.maxlon

def domain_plotter(title, mapextent, domains, background=None, resolution='1.0',
                   central_longitude=0.,plot_origin=True):
    '''
    Take the standard information used to describe
    domains for the UM and plot them as a boxes on a map

    Could add default extent as whole globe?

    extent - left, right, bottom, top in plate carree coordinates
    '''

    # create axes, with lower threshold for interpolation
    # so that the lines are smoothly curving
    pc = ccrs.PlateCarree(central_longitude=central_longitude)
    pc._threshold /= 10

    ax = plt.axes(projection=pc)
    ax.set_extent(mapextent)
    if background is None:
        ax.stock_img()
    else:
        # tell cartopy where to find backgrounds
        os.environ["CARTOPY_USER_BACKGROUNDS"] = '/data/users/fris/nasa_bg'
        ax.background_img(name=background, resolution=resolution)
    ax.coastlines(color='gray')
    # Create a feature for States/Admin 1 regions at 1:50m from Natural Earth
    states_provinces = cfeature.NaturalEarthFeature(
        category='cultural',
        name='admin_1_states_provinces_lines',
        scale='10m',
        facecolor='none')

    ax.add_feature(states_provinces, edgecolor='gray')
    ax.add_feature(cartopy.feature.RIVERS)
    ax.add_feature(cartopy.feature.BORDERS)
    ax.add_feature(cartopy.feature.LAKES)
    ax.add_feature(cartopy.feature.COASTLINE)
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = False


    plt.title(title)

    for domain in domains:
        rotated_pole = ccrs.RotatedPole(pole_latitude=domain.polelata,
                                        pole_longitude=domain.polelona)

        # specify x and y of corners in rotated pole co-ordinates,
        # returning to start to make a closed curve

        # Replace this with a call to domain.get_corners()
        # and then
        # x = domain.minlon, domain.minlon, domain.maxlon,
        # domain.maxlon, domain.minlon]

        domain.get_corners()

        x = [domain.minlon, domain.minlon, domain.maxlon,
             domain.maxlon, domain.minlon]
        y = [domain.minlat, domain.maxlat, domain.maxlat,
             domain.minlat, domain.minlat]


        p = ax.plot(x, y, marker='o', transform=rotated_pole)
        color = p[0].get_color()
        if plot_origin:
            # Add a marker for the origin of the domain
            ax.plot(0.0, 0.0, marker='o', color=color, markersize=5,
                     alpha=0.7, transform=rotated_pole)

    return plt.gcf()

def plot_cities(site_list):
    '''
    Given a list of names of cities, plot them on the current axes
    Must be included in the Natural Earth populated places 
    '''

    # load populated places data from natural Earth
    shpfilename = shpreader.natural_earth(resolution='10m', category='cultural',
        name='populated_places')
    reader = shpreader.Reader(shpfilename)
    places = reader.records()

    # filter only sites in the list above
    sites_shapes = [place for place in places if place.attributes['NAME'] in site_list ]

    ax = plt.gca()

    ax.scatter([point.attributes['LONGITUDE'] for point in sites_shapes],
               [point.attributes['LATITUDE'] for point in sites_shapes],
               c='red',
               transform=ccrs.Geodetic())
