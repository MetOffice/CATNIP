import os
import unittest
import numpy
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

    @unittest.skip("TO DO")
    def test_calculate_dewpoint(self):
        """Test one"""
        pass

    @unittest.skip("TO DO")
    def test_linear_regress(self):
        """Test two"""
        pass

    @unittest.skip("TO DO")
    def test_ci_interval(self):
        """Test three"""
        pass

    @unittest.skip("TO DO")
    def test_regrid_to_target(self):
        """Test four"""
        pass

    @unittest.skip("TO DO")
    def test_set_regridder(self):
        """Test five"""
        pass


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


    @unittest.skip("TO DO")
    def test_regular_point_to_rotated(self):
        """Test seven"""
        pass

    @unittest.skip("TO DO")
    def test_rotated_point_to_regular(self):
        """Test eight"""
        pass

    @unittest.skip("TO DO")
    def test_windspeed(self):
        """Test nine"""
        pass

    @unittest.skip("TO DO")
    def test_wind_direction(self):
        """Test ten"""
        pass


if __name__ == "__main__":
    unittest.main()
