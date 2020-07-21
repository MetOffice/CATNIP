import os
import unittest
import numpy
import iris
import catnip.config as conf
import iris.analysis
import iris.exceptions
from catnip.preparation import *


class TestPreparation(unittest.TestCase):
    """Unittest class for preparation module"""

    @classmethod
    def setUpClass(self):
        file1 = os.path.join(conf.DATA_DIR, 'mslp.daily.rcm.viet.nc')
        file2 = os.path.join(conf.DATA_DIR, 'rcm_monthly.pp')
        file3 = os.path.join(conf.DATA_DIR, 'rcm_mslp_monthly.pp')
        file4 = os.path.join(conf.DATA_DIR, 'gtopo30_025deg.nc')
        file5 = os.path.join(conf.DATA_DIR, 'gcm_monthly.pp')
        self.mslp_daily_cube = iris.load_cube(file1)
        self.rcm_monthly_cube = iris.load(file2)
        self.mslp_monthly_cube = iris.load_cube(file3)
        self.topo_cube = iris.load_cube(file4)
        self.gcm_cube = iris.load(file5)


    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_aux_unrotated_coords(self):

        add_aux_unrotated_coords(self.mslp_daily_cube)
        self.assertEqual(self.mslp_daily_cube.shape,(360, 136, 109))

        coords = [coord.name() for coord in self.mslp_daily_cube.coords()]
        self.assertEqual(coords,['time', 'grid_latitude', 'grid_longitude', 'latitude', 'longitude'])

        self.assertRaises(TypeError, add_aux_unrotated_coords, self.rcm_monthly_cube)
        self.assertRaises(TypeError, add_aux_unrotated_coords, self.topo_cube)
        #print(self.gcm_cube)

    def test_add_bounds(self):

        self.assertIsNone(add_bounds(self.mslp_daily_cube, 'grid_latitude'))
        self.assertIsNone(add_bounds(self.mslp_daily_cube, 'grid_latitude'))
        self.assertIsNone(add_bounds(self.mslp_daily_cube, 'time'))
        self.assertIsNone(add_bounds(self.mslp_daily_cube, ['grid_latitude','grid_longitude']))

        self.assertRaises(AttributeError, add_bounds, self.mslp_daily_cube, 't')
        self.assertRaises(TypeError, add_bounds, self.rcm_monthly_cube, 'time')
        self.assertRaises(TypeError, add_bounds, self.mslp_daily_cube, [123,123])
        self.assertRaises(TypeError, add_bounds, self.mslp_daily_cube, ['grid_latitude', 123])


    def test_add_coord_system(self):

        cscube = add_coord_system(self.topo_cube)
        self.assertIsNotNone(cscube.coord('latitude').coord_system)

        cscube = add_coord_system(self.gcm_cube[0])
        self.assertEqual(cscube,self.gcm_cube[0])

        self.assertRaises(TypeError, add_coord_system, self.rcm_monthly_cube)
        self.assertRaises(TypeError, add_coord_system, self.mslp_daily_cube)



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
