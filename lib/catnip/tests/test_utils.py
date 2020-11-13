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
import sys
from io import StringIO
import unittest
import numpy
import iris
from catnip.utils import *
import catnip.config as conf
import datetime as dt


class TestUtils(unittest.TestCase):
    """Unittest class for utils module"""

    @classmethod
    def setUpClass(self):
        file1 = os.path.join(conf.DATA_DIR, "FGOALS-g2_ua@925_nov.nc")
        file2 = os.path.join(conf.DATA_DIR, "gcm_monthly.pp")
        file3 = os.path.join(conf.DATA_DIR, "daily.19990801_19990823.pp")
        file4 = os.path.join(conf.DATA_DIR, "daily.19990808_19990830.pp")

        self.ua_cube = iris.load_cube(file1)
        self.gcm_t_cube = iris.load_cube(file2, "air_temperature")
        self.gcm_u_cube = iris.load_cube(file2, "x_wind")
        self.daily_01_08_cube = iris.load_cube(file3)
        self.daily_08_30_cube = iris.load_cube(file4)

        # a cube with no time coordinate
        self.daily_01_08_cube_notimedim = self.daily_01_08_cube.copy()
        time_coord = self.daily_01_08_cube_notimedim.coord("time")
        self.daily_01_08_cube_notimedim.remove_coord(time_coord)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_common_timeperiod(self):

        st, et, c1, c2 = common_timeperiod(self.daily_01_08_cube, self.daily_08_30_cube)
        self.assertEqual(c1.coord("time")[0], c2.coord("time")[0])
        self.assertEqual(c1.coord("time")[-1], c2.coord("time")[-1])
        self.assertEqual(c1.shape, c2.shape)

        # passing a cube with no time coordinate
        self.assertRaises(
            KeyError,
            common_timeperiod,
            self.daily_01_08_cube_notimedim,
            self.daily_08_30_cube,
        )
        self.assertRaises(
            KeyError,
            common_timeperiod,
            self.daily_08_30_cube,
            self.daily_01_08_cube_notimedim,
        )

        # passing a cube with no time bound
        daily_01_08_cube_nobound = self.daily_01_08_cube.copy()
        daily_01_08_cube_nobound.coord("time").bounds = None

        self.assertRaises(
            TypeError,
            common_timeperiod,
            daily_01_08_cube_nobound,
            self.daily_08_30_cube,
        )
        self.assertRaises(
            TypeError,
            common_timeperiod,
            self.daily_08_30_cube,
            daily_01_08_cube_nobound,
        )

    def test_compare_coords(self):
        # object to store console output
        capturedOutput = StringIO()
        # redirect print statements
        sys.stdout = capturedOutput
        compare_coords(
            self.gcm_t_cube.coord("latitude"), self.ua_cube.coord("latitude")
        )
        # reset the redirect
        sys.stdout = sys.__stdout__
        # get the output as a list
        out_str = str(capturedOutput.getvalue()).splitlines()

        # check the coords are captured correctly by the function
        func_cube1_long_name = out_str[0].split()[3]
        cube1_long_name = str(self.gcm_t_cube.coord("latitude").long_name)
        self.assertEqual(func_cube1_long_name, cube1_long_name)
        func_cube2_long_name = out_str[0].split()[5]
        cube2_long_name = str(self.ua_cube.coord("latitude").long_name)
        self.assertEqual(func_cube2_long_name, cube2_long_name)

        func_cube1_points_dtype = out_str[2].split()[3]
        cube1_points_dtype = str(self.gcm_t_cube.coord("latitude").points.dtype)
        self.assertEqual(func_cube1_points_dtype, cube1_points_dtype)
        func_cube2_points_dtype = out_str[2].split()[5]
        cube2_points_dtype = str(self.ua_cube.coord("latitude").points.dtype)
        self.assertEqual(func_cube2_points_dtype, cube2_points_dtype)

    def test_compare_cubes(self):
        # first test for failure when one of the inputs is not a cube
        with self.assertRaises(TypeError):
            compare_cubes(self.gcm_u_cube, "foo")

        # object to store console output
        capturedOutput = StringIO()
        # redirect print statements
        sys.stdout = capturedOutput
        compare_cubes(self.gcm_u_cube, self.ua_cube)
        # reset the redirect
        sys.stdout = sys.__stdout__
        # get the output as a list
        out_str = str(capturedOutput.getvalue()).splitlines()

        # check the cube meta data are captured correctly by the function
        func_cube1_standard_name = out_str[2].split()[3]
        cube1_standard_name = str(self.gcm_u_cube.standard_name)
        self.assertEqual(func_cube1_standard_name, cube1_standard_name)
        func_cube2_standard_name = out_str[2].split()[5]
        cube2_standard_name = str(self.ua_cube.standard_name)
        self.assertEqual(func_cube2_standard_name, cube2_standard_name)

        func_cube1_ndim = out_str[4].split()[3]
        cube1_ndim = str(self.gcm_u_cube.ndim)
        self.assertEqual(func_cube1_ndim, cube1_ndim)
        func_cube2_ndim = out_str[4].split()[5]
        cube2_ndim = str(self.ua_cube.ndim)
        self.assertEqual(func_cube2_ndim, cube2_ndim)

        # check coord data captured correctly by the function
        func_cube1_lat_shape = out_str[13].split()[4]
        cube1_lat_shape = str(self.gcm_u_cube.coord("latitude").shape)
        self.assertEqual(func_cube1_lat_shape, cube1_lat_shape)
        func_cube2_lat_shape = out_str[13].split()[6]
        cube2_lat_shape = str(self.ua_cube.coord("latitude").shape)
        self.assertEqual(func_cube2_lat_shape, cube2_lat_shape)

    def test_date_chunks(self):
        """
        Generate a series of random numbers to cover the number of years between the start and end date
        and pass it as a parameter to the data_chunks() function and assert the results

        """

        start_date = "2000/01/01"
        int_start_year = int(start_date.split("/")[0])
        end_date = "2020/12/31"
        int_end_year = int(end_date.split("/")[0])
        expected_year_span = int_end_year - int_start_year

        for i in range(2, expected_year_span):  # divmod(expected_year_span, 2)[0] + 1):

            year_chunk = i  # random.randint(2, divmod(expected_year_span, 2)[0])
            expected_result = date_chunks(start_date, end_date, year_chunk)

            # check the whole of output string
            self.assertEqual(expected_result, expected_result)

            # check that the first and last element of date list match the input
            self.assertEqual(start_date, expected_result[0][0])
            self.assertEqual(end_date, expected_result[-1][-1])

            # check that the year span is as expected as set by start/end dates
            output_year_span = int(expected_result[-1][-1].split("/")[0]) - int(
                expected_result[0][0].split("/")[0]
            )
            self.assertEqual(expected_year_span, output_year_span)

            # check that the year difference between the chunked years is <= year_chunk value
            for years_pair in expected_result:
                start_year = int(years_pair[0].split("/")[0])
                end_year = int(years_pair[1].split("/")[0])
                year_diff = end_year - start_year
                self.assertLessEqual(year_diff, year_chunk)

        # Negative tests

        # check for wrong date format
        with self.assertRaises(ValueError):
            bad_date_format = "01/01/2005"
            date_chunks(bad_date_format, end_date, 3)
        # check for exception using zero chunk year value
        with self.assertRaises(ValueError):
            date_chunks(start_date, end_date, 0)

        # check for exception using negative chunk year value
        with self.assertRaises(ValueError):
            date_chunks(start_date, end_date, -5)

    def test_get_date_range(self):
        """Tests for get_date_range function"""

        # First file - ua
        start_str, end_str, dr_constraint = get_date_range(self.ua_cube)
        self.assertEqual(start_str, "1/11/490")
        self.assertEqual(end_str, "1/12/747")
        self.assertIsInstance(dr_constraint, iris.Constraint)

        # File 2 x_wind from GCM
        start_str, end_str, dr_constraint = get_date_range(self.gcm_u_cube)
        self.assertEqual(start_str, "1/9/1960")
        self.assertEqual(end_str, "1/10/1960")
        self.assertIsInstance(dr_constraint, iris.Constraint)

        # File 3
        start_str, end_str, dr_constraint = get_date_range(self.daily_01_08_cube)
        self.assertEqual(start_str, "1/8/1999")
        self.assertEqual(end_str, "23/8/1999")
        self.assertIsInstance(dr_constraint, iris.Constraint)

        # File 4
        start_str, end_str, dr_constraint = get_date_range(self.daily_08_30_cube)
        self.assertEqual(start_str, "8/8/1999")
        self.assertEqual(end_str, "30/8/1999")
        self.assertIsInstance(dr_constraint, iris.Constraint)

        # pass a cube with no time dimension
        self.assertRaises(
            AttributeError, get_date_range, self.daily_01_08_cube_notimedim
        )

        # Pass an integer
        self.assertRaises(TypeError, get_date_range, 1)

    def test_sort_cube(self):
        """
        add and sort integer and char values to an iris cube coordinate and assert the results
        """
        # test for some integer values
        int_values = [-1, 2, 3, 0, 4, 5, 6, 50, -5]
        expected_results = [-5, -1, 0, 2, 3, 4, 5, 6, 50]

        cube = iris.cube.Cube(int_values)
        cube.add_aux_coord(iris.coords.AuxCoord(int_values, long_name="test_ints"), 0)
        cube = sort_cube(cube, "test_ints")

        self.assertListEqual(cube.coord("test_ints").points.tolist(), expected_results)

        # test for char values
        char_values = ["a", "z", "b", "e"]
        expected_results = ["a", "b", "e", "z"]

        cube = iris.cube.Cube(char_values)
        cube.add_aux_coord(iris.coords.AuxCoord(char_values, long_name="test_chars"), 0)
        cube = sort_cube(cube, "test_chars")

        self.assertListEqual(cube.coord("test_chars").points.tolist(), expected_results)

    def test_convert_from_um_stamp(self):

        fmt = ["YYMMM", "YYMDH"]
        umdate = ["k5bu0", "i1feb", "i1nov"]

        self.assertEqual(
            convert_from_um_stamp(umdate[0], fmt[1]), dt.datetime(2005, 11, 30, 0, 0)
        )
        self.assertEqual(
            convert_from_um_stamp(umdate[1], fmt[0]), dt.datetime(1981, 2, 1, 0, 0)
        )
        self.assertEqual(
            convert_from_um_stamp(umdate[2], fmt[0]), dt.datetime(1981, 11, 1, 0, 0)
        )

        self.assertRaises(ValueError, convert_from_um_stamp, "k5bu00", fmt[1])
        self.assertRaises(ValueError, convert_from_um_stamp, umdate[1], fmt[1])

    def test_convert_to_um_stamp(self):

        fmt = ["YYMMM", "YYMDH"]
        dt = datetime(1990, 5, 2)

        self.assertEqual(convert_to_um_stamp(dt, fmt[0]), "j0may")
        self.assertEqual(convert_to_um_stamp(dt, fmt[1]), "j0520")

        dt = cdatetime(1995, 2, 30)

        self.assertEqual(convert_to_um_stamp(dt, fmt[0]), "j5feb")
        self.assertEqual(convert_to_um_stamp(dt, fmt[1]), "j52u0")

        self.assertRaises(ValueError, convert_to_um_stamp, "19960101", fmt[1])
        self.assertRaises(ValueError, convert_to_um_stamp, dt, "YMDH")

    def test_um_file_list(self):

        """
        UMFileList() function currently only supports:
        pa: Timeseries of daily data spanning 1 month (beginning 0z on the 1st day)
        pj: Timeseries of hourly data spanning 1 day (0z - 24z)
        pm: Monthly average data for 1 month
        """

        runid = "akwss"
        startd = datetime(1980, 12, 29)
        endd = datetime(1981, 1, 1)
        freq1 = "pj"
        freq2 = "pa"
        freq3 = "pm"
        expected_result_1 = [
            "akwssa.pji0ct0.pp",
            "akwssa.pji0cu0.pp",
            "akwssa.pji0cv0.pp",
            "akwssa.pji1110.pp",
        ]
        expected_result_2 = [
            "akwssa.pai0ct0.pp",
            "akwssa.pai0cu0.pp",
            "akwssa.pai0cv0.pp",
            "akwssa.pai1110.pp",
        ]
        expected_result_3 = ["akwssa.pmi0dec.pp"]

        self.assertListEqual(
            um_file_list(runid, startd, endd, freq1), expected_result_1
        )
        self.assertListEqual(
            um_file_list(runid, startd, endd, freq2), expected_result_2
        )
        self.assertListEqual(
            um_file_list(runid, startd, endd, freq3), expected_result_3
        )

        # check for ValueError exception using start year > end year value
        with self.assertRaises(ValueError):
            um_file_list(runid, datetime(1990, 12, 29), datetime(1981, 1, 1), freq1)

    def test_umstash_2_pystash(self):

        umstash = ["24", "16222", "3236", "15201"]

        self.assertEqual(umstash_2_pystash(umstash[0]), ["m01s00i024"])
        self.assertEqual(
            umstash_2_pystash(umstash),
            ["m01s00i024", "m01s16i222", "m01s03i236", "m01s15i201"],
        )

        errstash = ["-16222", "123456", "xyz", "123xyz", 15201]

        self.assertRaises(IndexError, umstash_2_pystash, errstash[0])
        self.assertRaises(IndexError, umstash_2_pystash, errstash[1])
        self.assertRaises(AttributeError, umstash_2_pystash, errstash[2])
        self.assertRaises(IndexError, umstash_2_pystash, errstash[3])
        self.assertRaises(TypeError, umstash_2_pystash, errstash[4])


if __name__ == "__main__":
    unittest.main()
