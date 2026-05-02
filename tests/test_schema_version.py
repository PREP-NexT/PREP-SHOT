"""Tests for the params.json _schema_version guard added in v1.1.1."""
import unittest

from prepshot.load_data import CURRENT_SCHEMA, check_schema


class TestCheckSchema(unittest.TestCase):
    def test_accepts_current_schema(self):
        """A params.json stamped with the current schema passes silently."""
        check_schema({"_schema_version": CURRENT_SCHEMA, "demand": {}})

    def test_rejects_missing_stamp(self):
        """An unstamped params.json (legacy) is rejected with a hint."""
        with self.assertRaises(RuntimeError) as ctx:
            check_schema({"demand": {}})
        msg = str(ctx.exception)
        self.assertIn("_schema_version", msg)
        self.assertIn("pre-v1.1.0", msg)

    def test_rejects_old_schema(self):
        """A params.json stamped with an older schema is rejected."""
        with self.assertRaises(RuntimeError) as ctx:
            check_schema({"_schema_version": CURRENT_SCHEMA - 1})
        msg = str(ctx.exception)
        self.assertIn(f"_schema_version={CURRENT_SCHEMA - 1}", msg)
        self.assertIn(f"requires _schema_version={CURRENT_SCHEMA}", msg)

    def test_rejects_future_schema(self):
        """A params.json stamped with a newer schema is rejected too."""
        with self.assertRaises(RuntimeError):
            check_schema({"_schema_version": CURRENT_SCHEMA + 1})


if __name__ == "__main__":
    unittest.main()
