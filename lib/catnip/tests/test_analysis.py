import os
import unittest
import numpy as np
import iris
from catnip.analysis import *
import catnip.config as conf




class TestAnalysis(unittest.TestCase):
    """Unittest class for analysis module"""


    @classmethod
    def setUpClass(self):
        file1 = os.path.join(conf.DATA_DIR, 'FGOALS-g2_ua@925_nov.nc')
        file2 = os.path.join(conf.DATA_DIR, 'gcm_monthly.pp')
        file3 = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
        file4 = os.path.join(conf.DATA_DIR, 'mslp.daily.rcm.viet.nc')
        file5 = os.path.join(conf.DATA_DIR, 'dewpointtest_pt1.pp')
        file6 = os.path.join(conf.DATA_DIR, 'dewpointtest_pt2.pp')

        self.ua_cube = iris.load_cube(file1)

        # load the whole cubelist of gcm_monthly and rcm_monthly, to reduce the lines???
        self.gcm_u_cube = iris.load_cube(file2,'x_wind')
        self.gcm_v_cube = iris.load_cube(file2,'y_wind')
        self.gcm_cfrac_cube = iris.load_cube(file2,'cloud_area_fraction')
        self.gcm_t_cube = iris.load_cube(file2,'air_temperature')
        self.rcm_t_cube = iris.load_cube(file3,'air_temperature')
        self.rcm_u_cube = iris.load_cube(file3,'x_wind')
        self.rcm_v_cube = iris.load_cube(file3,'y_wind')
        self.mslp_daily_cube = iris.load_cube(file4)
        self.t_cube = iris.load_cube(file5,'air_temperature')
        self.q_cube = iris.load_cube(file5,'specific_humidity')
        self.d_cube = iris.load_cube(file5,'dew_point_temperature')
        self.p_cube = iris.load_cube(file6,'surface_air_pressure')

    @classmethod
    def tearDownClass(cls):
        pass


    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_calculate_dewpoint(self):

            td = calculate_dewpoint(self.p_cube, self.q_cube, self.t_cube)
            self.assertEqual(td.units,'K')
            self.assertEqual(td.standard_name,'dew_point_temperature')

            self.assertRaises(TypeError, calculate_dewpoint, self.p_cube, self.q_cube, 't_cube')

            self.t_cube.convert_units('celsius')
            self.assertRaises(ValueError, calculate_dewpoint, self.p_cube, self.q_cube, self.t_cube)



    def test_linear_regress(self):
        x = np.array([2,4,6,8,10,12,14,16,17,18])
        y = np.array([1,2,3,4,5,6,7,8,9,10])

        grad, intcp, xp, yp, sum_res = linear_regress(x, y)
        self.assertEqual(grad,0.5367828229496657)
        self.assertEqual(intcp,-0.2435762055614227)
        self.assertEqual(xp,[2, 18])

        self.assertRaises(ValueError,linear_regress,x, 1)
        y = np.array([2,4,6,8,10,12])
        self.assertRaises(ValueError,linear_regress,x, y)







    def test_ci_interval(self):

        x = np.array([1, 4, 2, 7, 0, 6, 3, 2, 1, 9])
        y = np.array([5, 6, 2, 9, 1, 4, 7, 8, 2, 3])
        slope_conf_int, intcp_conf_int, xpts, slope_lo_pts, slope_hi_pts, \
                xreg, y_conf_int_lo, y_conf_int_hi = ci_interval(x, y)

        self.assertEqual(slope_conf_int,0.7257975101330552)
        self.assertEqual(intcp_conf_int,3.253969685918782)

        y = np.array([5, 6, 2, 9, 1, 4, 7])
        self.assertRaises(ValueError,ci_interval,x, y)



    def test_regrid_to_target(self):

        gcm_cube = self.gcm_t_cube.copy()
        rcm_cube = self.gcm_t_cube.copy()

        # regridding from regular to rotated
        cube_reg = regrid_to_target(gcm_cube, rcm_cube)
        self.assertEqual(cube_reg.shape[-1], rcm_cube.shape[-1])
        self.assertEqual(cube_reg.shape[-2], rcm_cube.shape[-2])

        # regridding from rotated to rotated
        cube_reg = regrid_to_target(rcm_cube, self.mslp_daily_cube)
        self.assertEqual(cube_reg.shape[-1],self.mslp_daily_cube.shape[-1])
        self.assertEqual(cube_reg.shape[-2],self.mslp_daily_cube.shape[-2])

        # regridding from rotated to regular
        cube_reg = regrid_to_target(rcm_cube, gcm_cube)
        self.assertEqual(cube_reg.shape[-1],gcm_cube.shape[-1])
        self.assertEqual(cube_reg.shape[-2],gcm_cube.shape[-2])

        # regridding from regular to regular
        cube_reg = regrid_to_target(gcm_cube,self.gcm_u_cube)
        self.assertEqual(cube_reg.shape[-1],self.gcm_u_cube.shape[-1])
        self.assertEqual(cube_reg.shape[-2],self.gcm_u_cube.shape[-2])

        # regridding from regular to regular using method nearest
        cube_reg = regrid_to_target(gcm_cube, self.gcm_u_cube, 'nearest')
        self.assertEqual(cube_reg.shape[-1],self.gcm_u_cube.shape[-1])
        self.assertEqual(cube_reg.shape[-2],self.gcm_u_cube.shape[-2])

        # regridding from regular to regular using method nearest
        cube_reg = regrid_to_target(gcm_cube, self.gcm_u_cube, 'areaweighted')
        self.assertEqual(cube_reg.shape[-1],self.gcm_u_cube.shape[-1])
        self.assertEqual(cube_reg.shape[-2],self.gcm_u_cube.shape[-2])


        self.assertRaises(TypeError, regrid_to_target, gcm_cube, 'target_cube')
        self.assertRaises(TypeError, regrid_to_target, 'cube', rcm_cube)


    def test_set_regridder(self):

        gcm_cube = self.gcm_t_cube.copy()
        rcm_cube = self.gcm_t_cube.copy()

        regridder = set_regridder(gcm_cube, rcm_cube)
        regridder(self.gcm_cfrac_cube)
        self.assertEqual(self.gcm_cfrac_cube.shape, gcm_cube.shape)

        regridder = set_regridder(gcm_cube, rcm_cube,'nearest')
        regridder(self.gcm_cfrac_cube)
        self.assertEqual(self.gcm_cfrac_cube.shape, gcm_cube.shape)

        self.assertRaises(TypeError, set_regridder, 'gcm_cube', rcm_cube)
        self.assertRaises(TypeError, set_regridder, gcm_cube, 'rcm_cube')


    def test_seas_time_stat(self):

        seas_min_cubelist = seas_time_stat(self.mslp_daily_cube, metric='min', years=[2000,2002])
        self.assertEqual(seas_min_cubelist[0].coord('season').points,['mam'])
        self.assertEqual(seas_min_cubelist[1].coord('season').points,['jja'])
        self.assertEqual(seas_min_cubelist[2].coord('season').points,['son'])
        self.assertEqual(seas_min_cubelist[3].coord('season').points,['djf'])

        seas_min_cubelist = seas_time_stat(self.ua_cube, seas_mons=[[11]], metric='percentile', pc=95, ext_area=[340, 350, 0,10])
        self.assertEqual(seas_min_cubelist[0].coord('season').points,['n'])

        notim_cube = self.mslp_daily_cube.copy()
        time_coord = notim_cube.coord('time')
        notim_cube.remove_coord(time_coord)

        nolat_cube = self.mslp_daily_cube.copy()
        lat_coord = notim_cube.coord('grid_latitude')
        nolat_cube.remove_coord(lat_coord)


        self.assertRaises(iris.exceptions.CoordinateNotFoundError, seas_time_stat,notim_cube)
        self.assertRaises(TypeError, seas_time_stat, self.ua_cube, seas_mons=[[11]], metric='percentile', pc=95.5)
        self.assertRaises(ValueError, seas_time_stat, self.ua_cube, seas_mons=[[11]], metric='percentile')
        self.assertRaises(TypeError, seas_time_stat, 'self.ua_cube')
        self.assertRaises(IndexError, seas_time_stat, self.ua_cube, ext_area=[350, 0,10])
        self.assertRaises(IndexError, seas_time_stat, nolat_cube, ext_area=[340, 350, 0,10])



    def test_regular_point_to_rotated(self):

        reg_lon = 289
        reg_lat = 6.5
        rot_lon, rot_lat = regular_point_to_rotated(self.rcm_t_cube, reg_lon, reg_lat)
        self.assertEqual(float("%.3f" % rot_lon),-84.330)
        self.assertEqual(float("%.3f" % rot_lat),3.336)

        reg_lon = 3
        reg_lat = -60
        rot_lon, rot_lat = regular_point_to_rotated(self.rcm_t_cube, reg_lon, reg_lat)
        self.assertEqual(float("%.3f" % rot_lon),-160.482)
        self.assertEqual(float("%.3f" % rot_lat),-67.212)

        self.assertRaises(TypeError, regular_point_to_rotated, 'cube', reg_lon, reg_lat)




    def test_rotated_point_to_regular(self):

        rot_lat = 3.34
        rot_lon = -84.33
        reg_lon, reg_lat = rotated_point_to_regular(self.rcm_t_cube, rot_lon, rot_lat)
        self.assertEqual(float("%.3f" % reg_lon),-71.003)
        self.assertEqual(float("%.3f" % reg_lat),6.502)

        rot_lat = self.rcm_t_cube.coord('grid_latitude').points.max()
        rot_lon = self.rcm_t_cube.coord('grid_longitude').points.max()
        reg_lon, reg_lat = rotated_point_to_regular(self.rcm_t_cube, rot_lon, rot_lat)
        self.assertEqual(float("%.3f" % reg_lon), 68.722)
        self.assertEqual(float("%.3f" % reg_lat), 66.977)

        rot_lat = self.rcm_t_cube.coord('grid_latitude').points.min()
        rot_lon = self.rcm_t_cube.coord('grid_longitude').points.min()
        reg_lon, reg_lat = rotated_point_to_regular(self.rcm_t_cube, rot_lon, rot_lat)
        self.assertEqual(float("%.3f" % reg_lon), -10.602)
        self.assertEqual(float("%.3f" % reg_lat), 20.506)

        rot_lat = -6
        rot_lon = 10
        reg_lon, reg_lat = rotated_point_to_regular(self.rcm_t_cube, rot_lon, rot_lat)
        self.assertEqual(float("%.3f" % reg_lon), 31.847)
        self.assertEqual(float("%.3f" % reg_lat), 43.814)

        self.assertRaises(TypeError, 'cube', rot_lon, rot_lat)


    def test_windspeed(self):

        ws = windspeed(self.gcm_u_cube, self.gcm_v_cube)
        self.assertEqual(ws.standard_name,'wind_speed')
        self.assertEqual(ws.units,'m s-1')

        self.assertRaises(TypeError, windspeed,'self.gcm_u_cube', self.gcm_v_cube)
        self.assertRaises(TypeError, windspeed,self.gcm_u_cube, 'self.gcm_v_cube')

        self.assertRaises(ValueError, windspeed,self.gcm_t_cube, self.gcm_v_cube)
        self.assertRaises(ValueError, windspeed,self.gcm_u_cube, self.gcm_t_cube)




    def test_wind_direction(self):

        """Unit test for wind_direction() function"""

        wd = wind_direction(self.rcm_u_cube, self.rcm_v_cube)

        self.assertEqual(wd.standard_name, 'wind_to_direction')
        self.assertEqual(wd.long_name, 'wind vector direction')
        self.assertEqual(wd.var_name, 'angle')
        self.assertEqual(wd.units, 'degree')

        self.assertEqual(float("%.3f" % np.min(wd.data)), 0.018)
        self.assertEqual(float("%.3f" % np.max(wd.data)), 359.990)

        self.rcm_u_cube.units = 'degree'

        with self.assertRaises(ValueError):
            wind_direction(self.rcm_u_cube, self.rcm_v_cube)


if __name__ == "__main__":
    unittest.main()
