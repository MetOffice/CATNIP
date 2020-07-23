import os
import unittest
import numpy
import iris
from catnip.analysis import *
import catnip.config as conf




class TestPreparation(unittest.TestCase):
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


    @unittest.skip("TO DO")
    def test_regrid_to_target(self):
        """Test four"""
        pass

    @unittest.skip("TO DO")
    def test_set_regridder(self):
        """Test five"""
        pass

    @unittest.skip("TO DO")
    def test_seas_time_stat(self):
        """Test six"""
        pass

    @unittest.skip("TO DO")
    def test_regular_point_to_rotated(self):
        """Test seven"""
        pass

    @unittest.skip("TO DO")
    def test_rotated_point_to_regular(self):
        """Test eight"""
        pass


    def test_windspeed(self):

        ws = windspeed(self.gcm_u_cube, self.gcm_v_cube)
        self.assertEqual(ws.standard_name,'wind_speed')
        self.assertEqual(ws.units,'m s-1')

        self.assertRaises(TypeError, windspeed,'self.gcm_u_cube', self.gcm_v_cube)
        self.assertRaises(TypeError, windspeed,self.gcm_u_cube, 'self.gcm_v_cube')

        self.assertRaises(ValueError, windspeed,self.gcm_t_cube, self.gcm_v_cube)
        self.assertRaises(ValueError, windspeed,self.gcm_u_cube, self.gcm_t_cube)



    @unittest.skip("TO DO")
    def test_wind_direction(self):
        """Test ten"""
        pass


if __name__ == "__main__":
    unittest.main()
