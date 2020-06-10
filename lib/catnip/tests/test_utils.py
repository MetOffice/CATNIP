import os
import unittest
import numpy
import iris
from catnip.utils import *
import catnip.config as conf




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

    @unittest.skip("TO DO")
    def test_common_timeperiod(self):
        """Test one"""
        pass

    @unittest.skip("TO DO")
    def test_compare_coords(self):
        """Test two"""
        pass


    @unittest.skip("TO DO")
    def test_compare_cubes(self):
        """Test three"""
        pass


    @unittest.skip("TO DO")
    def test_date_chunks(self):
        """Test four"""
        pass


    @unittest.skip("TO DO")
    def test_get_date_range(self):
        """Test five"""
        pass


    @unittest.skip("TO DO")
    def test_sort_cube(self):
        """Test six"""
        pass

    @unittest.skip("TO DO")
    def test_convert_from_um_stamp(self):
        """Test seven"""
        pass

    @unittest.skip("TO DO")
    def test_convert_to_um_stamp(self):
        """Test eight"""
        pass

    @unittest.skip("TO DO")
    def test_precisYY(self):
        """Test nine"""
        pass

    @unittest.skip("TO DO")
    def test_precisD2(self):
        """Test ten"""
        pass

    @unittest.skip("TO DO")
    def test_um_file_list(self):
        """Test eleven"""
        pass

    @unittest.skip("TO DO")
    def test_umstash_2_pystash(self):
        """Test twelve"""
        pass



if __name__ == "__main__":
    unittest.main()
