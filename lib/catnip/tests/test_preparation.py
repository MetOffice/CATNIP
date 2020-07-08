import os
import unittest
import numpy
import iris
import catnip.config as conf
from catnip.preparation import *

class TestPreparation(unittest.TestCase):
    """Unittest class for preparation module"""

    @classmethod
    def setUpClass(self):
        file1 = os.path.join(conf.DATA_DIR, 'mslp.daily.rcm.viet.nc')
        file2 = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
        file3 = os.path.join(conf.DATA_DIR, 'rcm_mslp_monthly.pp')
        file4 = os.path.join(conf.DATA_DIR, 'gtopo30_025deg.nc')
        self.mslp_daily_cube = iris.load_cube(file1)
        self.rcm_monthly_cube = iris.load(file2)
        self.mslp_monthly_cube = iris.load_cube(file3)
        self.topo_cube = iris.load_cube(file4)


    @classmethod
    def tearDownClass(cls):
        pass


    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_add_aux_unrotated_coords(self):
        """for demo purpose only"""
        cube = self.mslp_daily_cube
        add_aux_unrotated_coords(cube)
        self.assertEqual(cube.shape,(360, 136, 109))

    @unittest.skip("TO DO")
    def test_add_bounds(self):
        """small discription"""
        pass

    @unittest.skip("TO DO")
    def test_add_coord_system(self):
        """testing coordinates"""
        pass

    @unittest.skip("TO DO")
    def test_add_time_coord_cats(self):
        """blah blah"""
        pass

    @unittest.skip("TO DO")
    def test_remove_forecast_coordinates(self):
        """Testing testing"""
        pass

    #@unittest.skip("TO DO")
    def test_rim_remove(self):
        """
        Tests to check that the correct number of coordinate points are removed and that the exceptions for invalid
        input values are caught.
        """

        for rim_width in range(8, 11):

            lat_points = len(self.mslp_monthly_cube.coord('grid_latitude').points)
            lon_points = len(self.mslp_monthly_cube.coord('grid_longitude').points)
            expected_lat_points = lat_points - (2*rim_width)
            expected_lon_points = lon_points - (2*rim_width)

            rrc = rim_remove(self.mslp_monthly_cube, rim_width)
            self.assertEqual(len(rrc.coord('grid_latitude').points), expected_lat_points)
            self.assertEqual(len(rrc.coord('grid_longitude').points), expected_lon_points)

        # check that TypeError exceptions are caught
        with self.assertRaises(TypeError):

            # not a cube instance
            rim_remove(self.rcm_monthly_cube, 8)
            # none integer values
            rim_remove(self.mslp_monthly_cube, 8.2)
            rim_remove(self.mslp_monthly_cube, 'a')

        # check that IndexError exceptions are caught
        with self.assertRaises(IndexError):

            rim_remove(self.mslp_monthly_cube, -5)
            rim_remove(self.mslp_monthly_cube, 400)
            rim_remove(self.mslp_monthly_cube, 0)





if __name__ == "__main__":
    unittest.main()
