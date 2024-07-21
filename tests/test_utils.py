"""This module contains tests for the utils module.
"""

import unittest

import numpy as np
import pandas as pd

from prepshot.utils import calc_cost_factor
from prepshot.utils import calc_inv_cost_factor
from prepshot.utils import check_positive
from prepshot.utils import interpolate_z_by_q_or_s
from prepshot.utils import cartesian_product

class TestUtils(unittest.TestCase):
    """Tests for the utils module.
    """

    def test_calc_cost_factor(self):
        """Test the prepshot.utils.calc_cost_factor function.
        """
        self.assertAlmostEqual(
            calc_cost_factor(0.05, 2025, 2020, 2030),
            3.561871, places=6
        )
        with self.assertRaises(ValueError):
            calc_cost_factor(0.05, 2025, 2020, 2024)
        with self.assertRaises(ValueError):
            calc_cost_factor(0.05, 2025, 2026, 2025)
        with self.assertRaises(ValueError):
            calc_cost_factor(-0.05, 2025, 2020, 2030)

    def test_calc_inv_cost_factor(self):
        """Test the prepshot.utils.calc_inv_cost_factor function.
        """
        self.assertAlmostEqual(
            calc_inv_cost_factor(20, 0.05, 2025, 0.05, 2020, 2050),
            0.783526, places=6
        )
        self.assertAlmostEqual(
            calc_inv_cost_factor(100, 0.05, 2025, 0.05, 2020, 2050),
            0.567482, places=6
        )

    def test_check_positive(self):
        """Test the prepshot.utils.check_positive function. 
        """
        with self.assertRaises(ValueError):
            check_positive(-0.01)
        with self.assertRaises(ValueError):
            check_positive(0)

    def test_interpolate_z_by_q_or_s(self):
        """Test the prepshot.utils.interpolate_z_by_q_or_s function.
        """
        name = '001'
        qs_val = 100
        qs_arr = [0, 200, 250]
        qs_beyond_val = 400
        qs_beyoud_arr = [-50, 200, 400]
        zq = pd.DataFrame({
            'name' : [name] * 3,
            'Q' : [0, 200, 300],
            'Z' : [0, 100, 200]
        })
        zs = pd.DataFrame({
            'name' : [name] * 3,
            'V' : [0, 200, 300],
            'Z' : [0, 100, 200]
        })
        self.assertAlmostEqual(
            interpolate_z_by_q_or_s(name, qs_val, zq),
            50
        )
        self.assertAlmostEqual(
            interpolate_z_by_q_or_s(name, qs_val, zs),
            50
        )
        np.testing.assert_allclose(
            interpolate_z_by_q_or_s(name, qs_arr, zq),
            np.array([0, 100, 150])
        )
        np.testing.assert_allclose(
            interpolate_z_by_q_or_s(name, qs_arr, zs),
            np.array([0, 100, 150])
        )
        self.assertAlmostEqual(
            interpolate_z_by_q_or_s(name, qs_beyond_val, zq),
            300
        )
        self.assertAlmostEqual(
            interpolate_z_by_q_or_s(name, qs_beyond_val, zs),
            300
        )
        np.testing.assert_allclose(
            interpolate_z_by_q_or_s(name, qs_beyoud_arr, zq),
            np.array([-25, 100, 300])
        )
        np.testing.assert_allclose(
            interpolate_z_by_q_or_s(name, qs_beyoud_arr, zs),
            np.array([-25, 100, 300])
        )
 
    def test_cartestian(self):
        """Test the prepshot.utils.cartestian function.
        """
        self.assertListEqual(
            cartesian_product([1, 2], [3, 4]),
            [(1, 3), (1, 4), (2, 3), (2, 4)]
        )
        self.assertListEqual(
            cartesian_product([1], [3, 4]),
            [(1, 3), (1, 4)]
        )
        self.assertListEqual(
            cartesian_product([1, 2]),
            [(1,), (2,)]
        )

if __name__ == '__main__':
    unittest.main()
