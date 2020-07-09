import os
import unittest
import numpy
import iris
import catnip.config as conf
from catnip.preparation import *
import iris.analysis
import iris.exceptions


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


    def test_remove_forecast_coordinates(self):
        """
        test that the forecast coordinates are removed and the
        exceptions are caught when they don't exist
        """

        cubes = self.rcm_monthly_cube
        self.assertEqual('forecast_period', cubes[0].coord('forecast_period').standard_name)
        self.assertEqual('forecast_reference_time', cubes[0].coord('forecast_reference_time').standard_name)
        frc = remove_forecast_coordinates(cubes[0])
        self.assertIsInstance(frc, iris.cube.Cube)

        with self.assertRaises(iris.exceptions.CoordinateNotFoundError):
            print(cubes[0].coord('forecast_period').standard_name)
            print(cubes[0].coord('forecast_reference_time').standard_name)



        #remove_forecast_coordinates(fcr_cube)


    #@unittest.skip("TO DO")
    def test_rim_remove(self):
        """testing rim remove"""
        pass


if __name__ == "__main__":
    unittest.main()
