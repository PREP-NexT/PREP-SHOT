"""Tests for the check on existing transmission lines.

Each line has one entry for each direction, and the cost rules charge
half of the line cost on each entry. The two entries must thus have
the same capacity.
"""
import unittest

try:
    from prepshot.model import check_line_symmetry
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False


@unittest.skipUnless(MODEL_AVAILABLE, "pyoptinterface not available")
class TestCheckLineSymmetry(unittest.TestCase):
    """Behavior of check_line_symmetry."""

    def test_symmetric_lines_pass(self):
        """Equal capacity in both directions is accepted."""
        check_line_symmetry({})
        check_line_symmetry({
            ('A', 'B', 2020): 100.0, ('B', 'A', 2020): 100.0,
            ('A', 'A', 2020): 0.0,
        })
        # Legacy 2-tuple keys.
        check_line_symmetry({('A', 'B'): 50.0, ('B', 'A'): 50.0})

    def test_missing_direction_fails(self):
        """A line with only one direction is rejected."""
        with self.assertRaises(ValueError):
            check_line_symmetry({('A', 'B', 2020): 100.0})

    def test_different_capacity_fails(self):
        """Different capacities in the two directions are rejected."""
        with self.assertRaises(ValueError):
            check_line_symmetry({
                ('A', 'B', 2020): 100.0, ('B', 'A', 2020): 80.0,
            })


if __name__ == "__main__":
    unittest.main()
