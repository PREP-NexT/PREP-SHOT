"""Tests for the long-format ("tidy") CSV input reader added in v1.4.0.

Long-format CSVs follow a single convention: dimension columns first,
value column last. The reader produces a dict whose keys are scalars
(for 1-dim inputs) or tuples (for 2+ dim inputs), so model-side lookups
work the same regardless of whether the file on disk is wide-Excel or
long-CSV.
"""
import logging
import os
import tempfile
import unittest

from prepshot.load_data import read_long_csv, load_excel_data


class TestReadLongCsv(unittest.TestCase):
    """Direct tests of read_long_csv."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dirname = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _write(self, name, contents):
        path = os.path.join(self.dirname, name)
        with open(path, "w") as f:
            f.write(contents)
        return path

    def test_two_dim_tuple_keys(self):
        """A 2-dim CSV produces tuple-keyed entries in the column order."""
        path = self._write("carbon_tax.csv", (
            "zone,year,value\n"
            "BA1,2020,0\n"
            "BA1,2025,5\n"
            "BA2,2030,10\n"
        ))
        result = read_long_csv(path)
        self.assertEqual(result[("BA1", 2020)], 0)
        self.assertEqual(result[("BA1", 2025)], 5)
        self.assertEqual(result[("BA2", 2030)], 10)
        self.assertEqual(len(result), 3)

    def test_three_dim_tuple_keys(self):
        """A 3-dim CSV produces 3-tuple keys."""
        path = self._write("tech_capacity_min.csv", (
            "zone,tech,year,value\n"
            "BA1,Coal,2020,0\n"
            "BA1,Hydro,2025,500\n"
        ))
        result = read_long_csv(path)
        self.assertEqual(result[("BA1", "Coal", 2020)], 0)
        self.assertEqual(result[("BA1", "Hydro", 2025)], 500)

    def test_one_dim_scalar_keys(self):
        """A 1-dim CSV produces scalar (not tuple) keys, matching the
        wide-format reader's behavior for ``first_col_only=True``."""
        path = self._write("discount_factor.csv", (
            "year,value\n"
            "2020,0.07\n"
            "2025,0.07\n"
        ))
        result = read_long_csv(path)
        self.assertEqual(result[2020], 0.07)
        self.assertEqual(result[2025], 0.07)

    def test_dropna_default(self):
        """Rows with NaN are dropped by default."""
        path = self._write("sparse.csv", (
            "zone,year,value\n"
            "BA1,2020,0\n"
            "BA1,2025,\n"
            "BA2,2020,5\n"
        ))
        result = read_long_csv(path)
        self.assertNotIn(("BA1", 2025), result)
        self.assertEqual(result[("BA1", 2020)], 0)
        self.assertEqual(result[("BA2", 2020)], 5)

    def test_rejects_zero_dim_csv(self):
        """A CSV with only a value column (no dim columns) is rejected."""
        path = self._write("bad.csv", "value\n0\n1\n")
        with self.assertRaises(ValueError):
            read_long_csv(path)

    def test_unit_column_filtered(self):
        """A 'unit' annotation column is dropped before keying so it
        does not appear in the output dict's tuple keys."""
        path = self._write("with_unit.csv", (
            "zone,year,unit,value\n"
            "BA1,2020,USD/tonne,3\n"
            "BA2,2025,USD/tonne,5\n"
        ))
        result = read_long_csv(path)
        # Keys are still (zone, year), not (zone, year, unit).
        self.assertEqual(result[("BA1", 2020)], 3)
        self.assertEqual(result[("BA2", 2025)], 5)

    def test_name_and_other_annotation_columns_filtered(self):
        """`name`, `commodity`, columns ending in `_name`, etc., are all
        treated as annotations and filtered out before keying."""
        path = self._write("with_annotations.csv", (
            "station_id,name,zone_name,unit,zone\n"
            "1,Grand Coulee,Singapore,zone_code,BA1\n"
            "2,Chief Joseph,Singapore,zone_code,BA1\n"
        ))
        result = read_long_csv(path)
        # Only `station_id` survives as a dim; `zone` is the value column.
        self.assertEqual(result[1], "BA1")
        self.assertEqual(result[2], "BA1")


class TestLongFormatDispatch(unittest.TestCase):
    """The format dispatch in load_excel_data picks the right reader."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.input_folder = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _write_csv(self, name, contents):
        with open(os.path.join(self.input_folder, name), "w") as f:
            f.write(contents)

    def test_long_format_dispatches_to_csv_reader(self):
        """A params entry with format:long reads from .csv, not .xlsx."""
        self._write_csv("carbon_tax.csv", "zone,year,value\nBA1,2020,3\n")
        params_info = {
            "carbon_tax": {
                "file_name": "carbon_tax",
                "format": "long",
                "drop_na": True,
            }
        }
        data_store = {}
        load_excel_data(self.input_folder, params_info, data_store)
        self.assertEqual(data_store["carbon_tax"][("BA1", 2020)], 3)

    def test_long_format_optional_missing_uses_default(self):
        """A long-format optional input that's missing falls back to default."""
        # No file written; we expect the default to be used.
        params_info = {
            "carbon_tax": {
                "file_name": "carbon_tax",
                "format": "long",
                "drop_na": True,
                "required": False,
                "default": 0,
            }
        }
        data_store = {}
        logging.disable(logging.DEBUG)
        try:
            load_excel_data(self.input_folder, params_info, data_store)
        finally:
            logging.disable(logging.NOTSET)
        # Defaultdict-wrapped scalar default returns 0 for any tuple lookup.
        self.assertEqual(data_store["carbon_tax"][("any", 9999)], 0)


if __name__ == "__main__":
    unittest.main()
