import os
import unittest

from prepshot.load_data import load_data
from prepshot.utils import (read_break_point, read_four_dims,
                            read_hydro_static, read_lag_time, read_one_dims,
                            read_three_dims, read_two_dims,
                            read_four_dims_three_index_one_col)
import sys


class TestPrepshot(unittest.TestCase):

    def test_read_four_dims(self):
        # Obtain the absolute path of the test input file
        test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        test_input_file = os.path.join(test_data_dir, 'four.xlsx')

        # Prepare test data
        data = {
            ('Solar', 'Guangxi', 1, 1): 0.064,
            ('Solar', 'Guangxi', 10, 2): 0.126,
            ('Wind', 'Guangxi', 1, 1): 0.064,
            ('Wind', 'Guangxi', 10, 2): 0.126
        }

        # Call the read_four_dims function with the sample excel file
        result = read_four_dims(test_input_file)

        # Validate the output structure and values
        self.assertEqual(result, data)

    def test_read_three_dims(self):
        # Obtain the absolute path of the test input file
        test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        test_input_file = os.path.join(test_data_dir, 'three.xlsx')

        # Prepare test data
        data = {
            ('Guangxi', 1, 1): 0.064,
            ('Guangxi', 10, 2): 0.126,
            ('Guangdong', 1, 1): 0.064,
            ('Guangdong', 10, 2): 0.126
        }

        # Call the read_three_dims function with the sample excel file
        result = read_three_dims(test_input_file)

        # Validate the output structure and values
        self.assertEqual(result, data)

    def test_read_two_dims(self):
        # Obtain the absolute path of the test input file
        test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        test_input_file = os.path.join(test_data_dir, 'two.xlsx')

        # Prepare test data
        data = {
            ('Guangxi', 1): 0.064,
            ('Guangxi', 2): 0.126,
            ('Guangdong', 1): 0.064,
            ('Guangdong', 2): 0.126
        }

        # Call the read_two_dims function with the sample excel file
        result = read_two_dims(test_input_file)

        # Validate the output structure and values
        self.assertEqual(result, data)

    def test_read_one_dims(self):
        # Obtain the absolute path of the test input file
        test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        test_input_file = os.path.join(test_data_dir, 'one.xlsx')

        # Prepare test data
        data = {1: 0.064, 2: 0.126}

        # Call the read_one_dims function with the sample excel file
        result = read_one_dims(test_input_file)

        # Validate the output structure and values
        self.assertEqual(result, data)


if __name__ == '__main__':
    # Redirect standard output to a file and print the data
    unittest.main()
