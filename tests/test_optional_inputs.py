"""Tests for the optional-input mechanism added in v1.3.0.

A params.json entry may declare ``"required": false`` and a ``"default"``
value. When the corresponding Excel file is missing on disk, the loader
substitutes the default rather than terminating the process.
"""
import logging
import os
import tempfile
import unittest

from prepshot.load_data import load_excel_data


class TestLoadExcelDataOptional(unittest.TestCase):
    """Behavior of load_excel_data with required vs optional entries."""

    def setUp(self):
        # All test inputs reference files that do not exist on disk; we
        # control file existence by writing fixtures to a temp directory.
        self._tmp = tempfile.TemporaryDirectory()
        self.input_folder = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def test_missing_required_terminates(self):
        """Missing file for a required parameter calls sys.exit(1)."""
        params_info = {
            "demand": {
                "file_name": "demand",  # not on disk
                "index_cols": [0],
                "header_rows": [0],
                "unstack_levels": None,
                "first_col_only": True,
                "drop_na": True,
                # No "required" key -> defaults to True.
            }
        }
        data_store = {}
        with self.assertRaises(SystemExit) as ctx:
            load_excel_data(self.input_folder, params_info, data_store)
        self.assertEqual(ctx.exception.code, 1)

    def test_missing_optional_uses_scalar_default(self):
        """Missing file for an optional parameter substitutes a default
        wrapped in a defaultdict so tuple-key lookups still work."""
        params_info = {
            "carbon_tax": {
                "file_name": "carbon_tax",  # not on disk
                "index_cols": [0],
                "header_rows": [0],
                "unstack_levels": [0],
                "first_col_only": False,
                "drop_na": True,
                "required": False,
                "default": 0,
            }
        }
        data_store = {}
        # Suppress the debug log during the test for clean output.
        logging.disable(logging.DEBUG)
        try:
            load_excel_data(self.input_folder, params_info, data_store)
        finally:
            logging.disable(logging.NOTSET)

        self.assertIn("carbon_tax", data_store)
        # The wrapper behaves like a dict for any tuple-key lookup.
        loaded = data_store["carbon_tax"]
        self.assertEqual(loaded[("BA1", 2025)], 0)
        self.assertEqual(loaded[("Singapore", 2050)], 0)

    def test_missing_optional_no_default_is_empty_dict(self):
        """An optional entry without an explicit default uses an empty dict."""
        params_info = {
            "foo": {
                "file_name": "foo",  # not on disk
                "index_cols": [0],
                "header_rows": [0],
                "unstack_levels": [0],
                "first_col_only": False,
                "drop_na": True,
                "required": False,
                # no "default"
            }
        }
        data_store = {}
        logging.disable(logging.DEBUG)
        try:
            load_excel_data(self.input_folder, params_info, data_store)
        finally:
            logging.disable(logging.NOTSET)
        self.assertEqual(data_store["foo"], {})


if __name__ == "__main__":
    unittest.main()
