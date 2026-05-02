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
        """A params.json stamped with an older schema is rejected.

        For the specific schema-1 -> schema-2+ jump we expect a tailored
        migration hint that points at tools/migrate_to_long.py; for any
        other mismatch a generic message suffices.
        """
        with self.assertRaises(RuntimeError) as ctx:
            check_schema({"_schema_version": 1})
        msg = str(ctx.exception)
        if CURRENT_SCHEMA >= 2:
            # Tailored schema-1 -> schema-2+ migration hint.
            self.assertIn("migrate_to_long", msg)
            self.assertIn("long-format CSV", msg)
        else:
            # Generic mismatch message (in case CURRENT_SCHEMA is rolled back).
            self.assertIn("_schema_version=1", msg)

    def test_rejects_future_schema(self):
        """A params.json stamped with a newer schema is rejected too."""
        with self.assertRaises(RuntimeError):
            check_schema({"_schema_version": CURRENT_SCHEMA + 1})


if __name__ == "__main__":
    unittest.main()
