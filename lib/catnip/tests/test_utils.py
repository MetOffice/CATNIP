import os
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
        file1 = os.path.join(conf.DATA_DIR, 'FGOALS-g2_ua@925_nov.nc')
        file2 = os.path.join(conf.DATA_DIR, 'gcm_monthly.pp')
        file3 = os.path.join(conf.DATA_DIR, 'daily.19990801_19990823.pp')
        file4 = os.path.join(conf.DATA_DIR, 'daily.19990808_19990830.pp')

        self.ua_cube = iris.load_cube(file1)
        self.gcm_t_cube = iris.load(file2,'air_temperature')
        self.gcm_u_cube = iris.load(file2,'x_wind')
        self.daily_01_08_cube = iris.load_cube(file3)
        self.daily_08_30_cube = iris.load_cube(file4)

    @classmethod
    def tearDownClass(cls):
        pass


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_common_timeperiod(self):

        st, et, c1, c2 = common_timeperiod(self.daily_01_08_cube, self.daily_08_30_cube)
        self.assertEqual(c1.coord('time')[0],c2.coord('time')[0])
        self.assertEqual(c1.coord('time')[-1],c2.coord('time')[-1])
        self.assertEqual(c1.shape,c2.shape)

        # passing a cube with no time coordinate
        daily_01_08_cube_notimedim = self.daily_01_08_cube.copy()
        time_coord = daily_01_08_cube_notimedim.coord('time')
        daily_01_08_cube_notimedim.remove_coord(time_coord)

        self.assertRaises(KeyError, common_timeperiod, daily_01_08_cube_notimedim, self.daily_08_30_cube)
        self.assertRaises(KeyError, common_timeperiod, self.daily_08_30_cube, daily_01_08_cube_notimedim)

        # passing a cube with no time bound
        daily_01_08_cube_nobound = self.daily_01_08_cube.copy()
        daily_01_08_cube_nobound.coord('time').bounds = None

        self.assertRaises(TypeError, common_timeperiod, daily_01_08_cube_nobound, self.daily_08_30_cube)
        self.assertRaises(TypeError, common_timeperiod, self.daily_08_30_cube, daily_01_08_cube_nobound)

    @unittest.skip("TO DO")
    def test_compare_coords(self):
        """Test two"""
        pass


    @unittest.skip("TO DO")
    def test_compare_cubes(self):
        """Test three"""
        pass

    def test_date_chunks(self):
        """
        Generate a series of random numbers to cover the number of years between the start and end date
        and pass it as a parameter to the data_chunks() function and assert the results

        """

        start_date = '2000/01/01'
        int_start_year = int(start_date.split("/")[0])
        end_date = '2020/12/31'
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
            output_year_span = int(expected_result[-1][-1].split("/")[0]) - int(expected_result[0][0].split("/")[0])
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


    @unittest.skip("TO DO")
    def test_get_date_range(self):
        """Test five"""
        pass


    def test_sort_cube(self):
        """
        add and sort integer and char values to an iris cube coordinate and assert the results
        """
       # test for some integer values
        int_values = [-1, 2, 3, 0, 4, 5, 6, 50, -5]
        expected_results = [-5, -1, 0, 2, 3, 4, 5, 6, 50]

        cube = iris.cube.Cube(int_values)
        cube.add_aux_coord(iris.coords.AuxCoord(int_values, long_name='test_ints'), 0)
        cube = sort_cube(cube, 'test_ints')

        self.assertListEqual(cube.coord('test_ints').points.tolist(), expected_results)

        # test for char values
        char_values = ['a', 'z', 'b', 'e']
        expected_results = ['a', 'b', 'e', 'z']

        cube = iris.cube.Cube(char_values)
        cube.add_aux_coord(iris.coords.AuxCoord(char_values, long_name='test_chars'), 0)
        cube = sort_cube(cube, 'test_chars')

        self.assertListEqual(cube.coord('test_chars').points.tolist(), expected_results)



    def test_convert_from_um_stamp(self):

        fmt = ['YYMMM','YYMDH']
        umdate = ['k5bu0','i1feb','i1nov']

        self.assertEqual(convert_from_um_stamp(umdate[0], fmt[1]),dt.datetime(2005, 11, 30, 0, 0))
        self.assertEqual(convert_from_um_stamp(umdate[1], fmt[0]),dt.datetime(1981, 2, 1, 0, 0))
        self.assertEqual(convert_from_um_stamp(umdate[2], fmt[0]),dt.datetime(1981, 11, 1, 0, 0))

        self.assertRaises(ValueError, convert_from_um_stamp,'k5bu00',fmt[1])
        self.assertRaises(ValueError, convert_from_um_stamp,umdate[1],fmt[1])


    def test_convert_to_um_stamp(self):

        fmt = ['YYMMM','YYMDH']
        dt = datetime(1990, 5, 2)

        self.assertEqual(convert_to_um_stamp(dt, fmt[0]),'j0may')
        self.assertEqual(convert_to_um_stamp(dt, fmt[1]),'j0520')

        dt = cdatetime(1995, 2, 30)

        self.assertEqual(convert_to_um_stamp(dt, fmt[0]),'j5feb')
        self.assertEqual(convert_to_um_stamp(dt, fmt[1]),'j52u0')

        self.assertRaises(ValueError, convert_to_um_stamp,'19960101',fmt[1])
        self.assertRaises(ValueError, convert_to_um_stamp,dt,'YMDH')



    def test_precisYY(self):

        self.assertEqual(precis_yy(2001),'k1')
        self.assertEqual(precis_yy(1995),'j5')

        self.assertRaises(TypeError, precis_yy,'1995')
        self.assertRaises(ValueError, precis_yy,12345)


    def test_precisD2(self):

        self.assertEqual(precis_d2('s'),28)
        self.assertEqual(precis_d2('x'),33)
        self.assertEqual(precis_d2(28),'s')
        self.assertEqual(precis_d2(33),'x')

        self.assertRaises(ValueError, precis_d2,50)
        self.assertRaises(ValueError, precis_d2,'%')

    def test_um_file_list(self):

        """
        UMFileList() function currently only supports:
        pa: Timeseries of daily data spanning 1 month (beginning 0z on the 1st day)
        pj: Timeseries of hourly data spanning 1 day (0z - 24z)
        pm: Monthly average data for 1 month
        """

        runid = 'akwss'
        startd = datetime(1980, 12, 29)
        endd = datetime(1981, 1, 1)
        freq1 = 'pj'
        freq2 = 'pa'
        freq3 = 'pm'
        expected_result_1 = ['akwssa.pji0ct0.pp', 'akwssa.pji0cu0.pp', 'akwssa.pji0cv0.pp', 'akwssa.pji1110.pp']
        expected_result_2 = ['akwssa.pai0ct0.pp', 'akwssa.pai0cu0.pp', 'akwssa.pai0cv0.pp', 'akwssa.pai1110.pp']
        expected_result_3 = ['akwssa.pmi0dec.pp']

        self.assertListEqual(um_file_list(runid, startd, endd, freq1), expected_result_1)
        self.assertListEqual(um_file_list(runid, startd, endd, freq2), expected_result_2)
        self.assertListEqual(um_file_list(runid, startd, endd, freq3), expected_result_3)

        # check for ValueError exception using start year > end year value
        with self.assertRaises(ValueError):
            um_file_list(runid, datetime(1990, 12, 29), datetime(1981, 1, 1), freq1)

    @unittest.skip("TO DO")
    def test_umstash_2_pystash(self):
        """Test twelve"""
        pass



if __name__ == "__main__":
    unittest.main()
