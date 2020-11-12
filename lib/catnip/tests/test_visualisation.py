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

import io
import os
import unittest
import iris
import catnip.config as conf
import imagehash
from PIL import Image
from catnip.visualisation import vector_plot, plot_regress

# import matplotlob after catnip vector plot as that sets the Agg
# backend
import matplotlib.pyplot as plt


#: Default perceptual hash size.
_HASH_SIZE = 16
#: Default maximum perceptual hash hamming distance.
_HAMMING_DISTANCE = 0


def _compare_images(figure, expected_filename):
    """
    Use imagehash to compare images fast and reliably.

    Returns True if they match within tolerance, false
    otherwise
    """
    img_buffer = io.BytesIO()
    figure.savefig(img_buffer, format="png")
    img_buffer.seek(0)
    gen_phash = imagehash.phash(Image.open(img_buffer), hash_size=_HASH_SIZE)
    exp_phash = imagehash.phash(Image.open(expected_filename), hash_size=_HASH_SIZE)
    distance = abs(gen_phash - exp_phash)
    return distance <= _HAMMING_DISTANCE


class TestVisualisation(unittest.TestCase):
    """Unittest class for visualisation module"""

    @classmethod
    def setUpClass(self):
        file1 = os.path.join(conf.DATA_DIR, "rcm_monthly.pp")
        file2 = os.path.join(conf.DATA_DIR, "gcm_monthly.pp")
        self.rcm_monthly_cube = iris.load(file1)
        self.gcm_monthly_cube = iris.load(file2)
        self.gcm_u = self.gcm_monthly_cube.extract_strict("x_wind")
        self.gcm_v = self.gcm_monthly_cube.extract_strict("y_wind")
        self.rcm_u = self.rcm_monthly_cube.extract_strict("x_wind")[0, ...]
        self.rcm_v = self.rcm_monthly_cube.extract_strict("y_wind")[0, ...]

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        # we need to close the figure produced by each test
        plt.close()

    def test_vector_plot_gcm(self):
        """
        Test plotting for GCM data
        """

        expected_png = os.path.join(conf.KGO_DIR, "gcm_ws.png")

        vector_plot(self.gcm_u, self.gcm_v)

        actual_fig = plt.gcf()
        self.assertTrue(_compare_images(actual_fig, expected_png))

    def test_vector_plot_gcm_title(self):
        """
        Test plotting for GCM data with a title
        """

        expected_png = os.path.join(conf.KGO_DIR, "gcm_ws_title.png")

        vector_plot(self.gcm_u, self.gcm_v, title="GCM W/S")

        actual_fig = plt.gcf()
        self.assertTrue(_compare_images(actual_fig, expected_png))

    def test_vector_plot_gcm_subplots(self):
        """
        Test plotting for GCM data with subplots
        """

        expected_png = os.path.join(conf.KGO_DIR, "gcm_ws_121.png")

        vector_plot(self.gcm_u, self.gcm_v, num_plot=121)

        actual_fig = plt.gcf()
        self.assertTrue(_compare_images(actual_fig, expected_png))

    def test_vector_plot_gcm_n10(self):
        """
        Test plotting for GCM data with npoints = 10
        """

        expected_png = os.path.join(conf.KGO_DIR, "gcm_ws_n10.png")

        vector_plot(self.gcm_u, self.gcm_v, npts=10)

        actual_fig = plt.gcf()
        plt.savefig("/scratch/fris/gcm_ws_n10.png")
        self.assertTrue(_compare_images(actual_fig, expected_png))

    def test_vector_rot_error(self):
        """
        Test that passing a global field gives an Exception
        """

        self.assertRaises(Exception, vector_plot, self.gcm_u, self.gcm_v, unrotate=True)

    def test_vector_plot_rcm(self):
        """
        Test plotting for RCM data without unrotation
        """

        expected_png = os.path.join(conf.KGO_DIR, "rcm_ws.png")

        vector_plot(self.rcm_u, self.rcm_v)

        actual_fig = plt.gcf()
        self.assertTrue(_compare_images(actual_fig, expected_png))

    def test_vector_plot_rcm_unrot(self):
        """
        Test plotting for RCM data with unrotation
        """

        expected_png = os.path.join(conf.KGO_DIR, "rcm_ws_unrot.png")

        vector_plot(self.rcm_u, self.rcm_v, unrotate=True)

        actual_fig = plt.gcf()
        self.assertTrue(_compare_images(actual_fig, expected_png))

    # other tests:
    # assert raises value error if pass in GCM cube with unrot
    # also test optional args: npts=30, num_plot=111, title="")
    # need to generate these - use a notebook
    @unittest.skip("TO DO")
    def test_plot_regress(self):
        """Test two"""
        pass


if __name__ == "__main__":
    unittest.main()
