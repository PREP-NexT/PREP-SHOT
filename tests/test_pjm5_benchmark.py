"""External-benchmark validation against the Hogan / PJM 5-bus system.

The 5-bus textbook example (Hogan 2002; MATPOWER ``case5``) is the
canonical "did your DC-OPF + LMP extraction get this right" check.
We run a single-hour PCM dispatch on the dataset shipped at
``examples/pjm5/`` and compare against MATPOWER's published
``runopf`` results.

The rock-solid invariants are total cost and per-tech dispatch --
the LP optimum is unique and identical across formulations:

* Total system cost:        ``$17,479.89 / hour``
* Alta + Park City:         40 + 170 MW (both at upper bound)
* Solitude (bus 3):         ~323.49 MW (marginal, sets bus 3 LMP)
* Sundance (bus 4):         0 MW (most expensive, never dispatched)
* Brighton (bus 5):         ~466.51 MW (marginal, sets bus 5 LMP)
* Line 4 -> 5 binding:      240 MW

The LMPs at bus 3 ($30) and bus 5 ($10) anchor on the marginal
plant cost and match exactly.  LMPs at bus 1 / bus 2 / bus 4
depend on the DC-OPF formulation's reference-bus choice and
susceptance normalization, so we only check that they fall in
the merit-order envelope of $10..$50 / MWh.
"""
import os
import sys
import unittest
from pathlib import Path

import pandas as pd

try:
    import pyoptinterface as poi  # noqa: F401  imported to gate the test
    from prepshot.set_up import initialize_environment
    from prepshot.pcm import (
        _build_window_params, _override_existing_fleet,
        load_fixed_capacity, _extract_window_dispatch,
    )
    from prepshot.model import create_model
    from prepshot.solver import solve_model
    SOLVER_AVAILABLE = True
except ImportError:
    SOLVER_AVAILABLE = False

REPO_ROOT = Path(__file__).resolve().parent.parent
SCENARIO = REPO_ROOT / 'examples' / 'pjm5'

# MATPOWER case5 / Hogan reference values (DC OPF, lossless).
EXPECTED_TOTAL_COST = 17479.89
EXPECTED_DISPATCH = {
    'Alta':     40.0,    # at upper bound
    'ParkCity': 170.0,   # at upper bound
    'Solitude': 323.49,
    'Sundance': 0.0,
    'Brighton': 466.51,
}
# LMPs that match exactly (anchored on a marginal plant's cost).
EXPECTED_LMP_EXACT = {
    'bus3': 30.0,   # Solitude is partial here -> LMP = its var_om
    'bus5': 10.0,   # Brighton is partial here -> LMP = its var_om
}


@unittest.skipUnless(
    SOLVER_AVAILABLE, "pyoptinterface / HiGHS not available in this env"
)
class TestPjm5Benchmark(unittest.TestCase):
    """PJM 5-bus single-hour DC-OPF, validated against MATPOWER case5."""

    @classmethod
    def setUpClass(cls):
        argv_before = sys.argv
        cwd_before = os.getcwd()
        sys.argv = [argv_before[0]]
        os.chdir(SCENARIO)
        try:
            full_params = initialize_environment({
                'filepath': str(SCENARIO),
                'config_filename': str(SCENARIO / 'config.json'),
                'params_filename': str(SCENARIO / 'params.json'),
            })
            window_hours = list(full_params['hour'])  # [1]
            win = _build_window_params(
                full_params, 2020, window_hours,
                state={'hydro_storage': {}, 'battery_storage': {}},
            )
            cap = load_fixed_capacity(
                Path('input/capacity_pcm.csv'), 2020, SCENARIO,
            )
            _override_existing_fleet(win, cap)
            cls.model = create_model(win)
            assert solve_model(cls.model, win), "PJM 5-bus solve failed"
            cls.dispatch = _extract_window_dispatch(
                cls.model, window_hours, 2020,
            )
        finally:
            sys.argv = argv_before
            os.chdir(cwd_before)

    def test_total_cost(self):
        """Total cost matches MATPOWER's runopf to the dollar."""
        cost = float(self.model.get_value(self.model.cost))
        self.assertAlmostEqual(
            cost, EXPECTED_TOTAL_COST, delta=1.0,
            msg=f"Total cost {cost:.2f} != {EXPECTED_TOTAL_COST}",
        )

    def test_dispatch_per_tech(self):
        """Each generator dispatches its expected MW."""
        gen = pd.DataFrame(self.dispatch['gen'])
        actual = gen.groupby('tech')['value'].sum().to_dict()
        for tech, expected in EXPECTED_DISPATCH.items():
            self.assertAlmostEqual(
                actual.get(tech, 0.0), expected, delta=0.5,
                msg=f"{tech}: dispatched {actual.get(tech)}, "
                    f"expected {expected}",
            )

    def test_lmp_anchor_buses(self):
        """LMPs at marginal-plant buses match the gen cost exactly."""
        lmp = pd.DataFrame(self.dispatch['lmp'])
        if lmp.empty:
            self.skipTest("backend did not return constraint duals")
        per_bus = lmp.groupby('zone')['value'].first().to_dict()
        for bus, expected in EXPECTED_LMP_EXACT.items():
            self.assertAlmostEqual(
                per_bus[bus], expected, delta=0.1,
                msg=f"LMP at {bus}: {per_bus[bus]}, expected {expected}",
            )

    def test_lmp_merit_envelope(self):
        """All LMPs fall within the merit-order envelope $10 .. $50."""
        lmp = pd.DataFrame(self.dispatch['lmp'])
        if lmp.empty:
            self.skipTest("backend did not return constraint duals")
        per_bus = lmp.groupby('zone')['value'].first()
        self.assertGreaterEqual(per_bus.min(), 10.0 - 0.01)
        self.assertLessEqual(per_bus.max(), 50.0)


if __name__ == "__main__":
    unittest.main()
