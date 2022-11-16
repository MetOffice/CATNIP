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

import os
import unittest
import iris
import catnip.config as conf
import iris.analysis
import iris.exceptions
from catnip.preparation import *
from catnip.preparation import _get_xy_noborder


class TestPreparation(unittest.TestCase):
    """Unittest class for preparation module"""

    @classmethod
    def setUpClass(self):
        file1 = os.path.join(conf.DATA_DIR, "mslp.daily.rcm.viet.nc")
        file2 = os.path.join(conf.DATA_DIR, "rcm_monthly.pp")
        file3 = os.path.join(conf.DATA_DIR, "rcm_mslp_monthly.pp")
        file4 = os.path.join(conf.DATA_DIR, "gtopo30_025deg.nc")
        file5 = os.path.join(conf.DATA_DIR, "gcm_monthly.pp")
        self.mslp_daily_cube = iris.load_cube(file1)
        self.rcm_monthly_cube = iris.load(file2)
        self.mslp_monthly_cube = iris.load_cube(file3)
        self.topo_cube = iris.load_cube(file4)
        self.gcm_cube = iris.load(file5)

        # a cube with no time coordinate
        self.daily_cube_notimedim = self.mslp_daily_cube.copy()
        time_coord = self.daily_cube_notimedim.coord("time")
        self.daily_cube_notimedim.remove_coord(time_coord)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_xy_noborder(self):
        """
        Test basic version of _get_xy_noborder
        """

        indices_expected = (2, 4, 1, 4)

        # set up test data
        d = np.full((5, 5), True)
        # fill some values
        d[3, 2] = False
        d[3, 3,] = False
        d[1, 3] = False

        indices_actual = _get_xy_noborder(d)
        self.assertEqual(indices_expected, indices_actual)

    def test_get_xy_noborder_false(self):
        """
        Test get_xy_noborder when mask all False
        """

        indices_expected = (0, 5, 0, 5)

        # set up test data
        d = np.full((5, 5), False)

        indices_actual = _get_xy_noborder(d)
        self.assertEqual(indices_expected, indices_actual)

    def test_get_xy_noborder_true(self):
        """
        Test _get_xy_noborder when all True - error
        """

        # set up test data
        d = np.full((5, 5), True)

        self.assertRaises(ValueError, _get_xy_noborder, d)

    def test_add_aux_unrotated_coords(self):

        cube = add_aux_unrotated_coords(self.mslp_daily_cube)
        self.assertEqual(cube.shape, (360, 136, 109))

        coords = [coord.name() for coord in cube.coords()]
        self.assertEqual(
            coords, ["time", "grid_latitude", "grid_longitude", "latitude", "longitude"]
        )

        self.assertRaises(TypeError, add_aux_unrotated_coords, self.rcm_monthly_cube)
        self.assertRaises(TypeError, add_aux_unrotated_coords, self.topo_cube)
        # print(self.gcm_cube)

    def test_add_bounds(self):

        latcube = add_bounds(self.mslp_daily_cube, "grid_latitude")
        glat_coord = latcube.coord("grid_latitude")
        self.assertTrue(glat_coord.has_bounds())

        tcube = add_bounds(self.mslp_daily_cube, "time")
        t_coord = tcube.coord("time")
        self.assertTrue(t_coord.has_bounds())

        latloncube = add_bounds(
            self.mslp_daily_cube, ["grid_latitude", "grid_longitude"]
        )
        for coord in ["grid_latitude", "grid_longitude"]:
            latlon_coord = latloncube.coord(coord)
            self.assertTrue(latlon_coord.has_bounds())

        self.assertRaises(AttributeError, add_bounds, self.mslp_daily_cube, "t")
        self.assertRaises(TypeError, add_bounds, self.rcm_monthly_cube, "time")
        self.assertRaises(TypeError, add_bounds, self.mslp_daily_cube, [123, 123])
        self.assertRaises(
            TypeError, add_bounds, self.mslp_daily_cube, ["grid_latitude", 123]
        )

    def test_add_coord_system(self):

        cscube = add_coord_system(self.topo_cube)
        self.assertIsNotNone(cscube.coord("latitude").coord_system)

        cscube = add_coord_system(self.gcm_cube[0])
        self.assertEqual(cscube, self.gcm_cube[0])

        self.assertRaises(TypeError, add_coord_system, self.rcm_monthly_cube)
        self.assertRaises(TypeError, add_coord_system, self.mslp_daily_cube)

    def test_extract_rot_cube(self):
        """
        Test the shape of the extracted cube and min/max
        lat and lon
        """

        # define box to extract
        min_lat = 50
        min_lon = -10
        max_lat = 60
        max_lon = 0

        tcube = self.rcm_monthly_cube.extract_cube("air_temperature")
        extracted_cube = extract_rot_cube(tcube, min_lat, min_lon, max_lat, max_lon)
        self.assertEqual(np.shape(extracted_cube.data), (2, 102, 78))
        self.assertEqual(
            np.max(extracted_cube.coord("latitude").points), 61.365291870327816
        )
        self.assertEqual(
            np.min(extracted_cube.coord("latitude").points), 48.213032844268646
        )
        self.assertEqual(
            np.max(extracted_cube.coord("longitude").points), 3.642576550089792
        )
        self.assertEqual(
            np.min(extracted_cube.coord("longitude").points), -16.29169201066359
        )

    def test_add_time_coord_cats(self):
        cube = self.mslp_daily_cube.copy()
        cube = add_time_coord_cats(cube)
        coord_names = [coord.name() for coord in cube.coords()]
        self.assertIn("day_of_month", coord_names)
        self.assertIn("month_number", coord_names)
        self.assertIn("season_number", coord_names)

        self.assertRaises(
            iris.exceptions.CoordinateNotFoundError,
            add_time_coord_cats,
            self.daily_cube_notimedim,
        )

    def test_remove_forecast_coordinates(self):

        """
        test that the forecast coordinates are removed and the
        exceptions are caught when they don't exist
        """

        cubes = self.rcm_monthly_cube
        self.assertEqual(
            "forecast_period", cubes[0].coord("forecast_period").standard_name
        )
        self.assertEqual(
            "forecast_reference_time",
            cubes[0].coord("forecast_reference_time").standard_name,
        )
        frc = remove_forecast_coordinates(cubes[0])
        self.assertIsInstance(frc, iris.cube.Cube)

        with self.assertRaises(iris.exceptions.CoordinateNotFoundError):
            print(cubes[0].coord("forecast_period").standard_name)
            print(cubes[0].coord("forecast_reference_time").standard_name)

    def test_rim_remove(self):
        """
        Tests to check that the correct number of coordinate points are
        removed and that the exceptions for invalid
        input values are caught.
        """

        for rim_width in range(8, 11):

            lat_points = len(self.mslp_monthly_cube.coord("grid_latitude").points)
            lon_points = len(self.mslp_monthly_cube.coord("grid_longitude").points)
            expected_lat_points = lat_points - (2 * rim_width)
            expected_lon_points = lon_points - (2 * rim_width)

            rrc = rim_remove(self.mslp_monthly_cube, rim_width)
            self.assertEqual(
                len(rrc.coord("grid_latitude").points), expected_lat_points
            )
            self.assertEqual(
                len(rrc.coord("grid_longitude").points), expected_lon_points
            )

        # check that TypeError exceptions are caught
        with self.assertRaises(TypeError):

            # not a cube instance
            rim_remove(self.rcm_monthly_cube, 8)
            # none integer values
            rim_remove(self.mslp_monthly_cube, 8.2)
            rim_remove(self.mslp_monthly_cube, "a")

        # check that IndexError exceptions are caught
        with self.assertRaises(IndexError):

            rim_remove(self.mslp_monthly_cube, -5)
            rim_remove(self.mslp_monthly_cube, 400)
            rim_remove(self.mslp_monthly_cube, 0)


if __name__ == "__main__":
    unittest.main()
