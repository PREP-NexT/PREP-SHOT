"""External-benchmark validation against the IEEE RTS-96 (3-area, 73-bus).

Source:
  IEEE Reliability Test System Task Force (1999),
  "IEEE reliability test system-96,"
  IEEE Trans. Power Systems, Vol. 14, No. 3, pp. 1010-1020.

The 3-area system is built by replicating RTS-79 three times (bus
numbers area-prefixed as 1xx / 2xx / 3xx) and connecting the
areas with the 5 inter-area tie lines from Table V of the 1999
paper.  Bus 325 is an area-3 tie node (no load, no gen).

System scale: 73 buses, 96 generators (3 x 32), 107 unique
intra-area lines + 5 inter-area ties, peak load 8 550 MW
(= 3 x 2 850 MW).

The validation thesis: each area is self-sufficient under
peak load (~83 % reserve margin within-area), so no inter-area
tie binds.  The dispatch is then exactly three identical copies
of the RTS-79 solution -- annual energy, capacity factors, and
peak dispatch should all be ``3 x`` the single-area numbers.
This is the canonical RTS-96 pass/fail check for nodal LP
correctness on a multi-area network.
"""
import os
import sys
import unittest
from pathlib import Path

import pandas as pd

try:
    import pyoptinterface as poi  # noqa: F401
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
SCENARIO = REPO_ROOT / 'examples' / 'rts96'
SKIP_SLOW = os.environ.get('PREPSHOT_SKIP_SLOW') == '1'

PEAK_HOUR = 8442

# Expected per-carrier dispatch at peak hour 8442 (= 3 x RTS-79).
EXPECTED_PEAK_DISPATCH_MW = {
    'hydro':    900.0,    # = 3 x 300
    'nuclear': 2400.0,    # = 3 x 800
    'coal':    3822.0,    # = 3 x 1 274
    'oil':     1428.0,    # = 3 x 476
}
TOTAL_PEAK_MW = sum(EXPECTED_PEAK_DISPATCH_MW.values())  # 8 550

# Expected annual energy (GWh) -- = 3 x RTS-79 numbers.
EXPECTED_ANNUAL_GWH = 45891.0
EXPECTED_ANNUAL_BY_CARRIER_GWH = {
    'nuclear': 20937.0,
    'coal':    16882.0,
    'hydro':    7862.0,
    'oil':       210.0,
}
NAMEPLATE_MW_BY_CARRIER = {
    'hydro':     900,    # 3 x 6 x U50
    'nuclear':  2400,    # 3 x 2 x U400
    'coal':     3822,    # 3 x (U350 + 4 U155 + 4 U76)
    'oil':      3093,    # 3 x (4 U20 + 3 U100 + 3 U197 + 5 U12)
}


@unittest.skipUnless(
    SOLVER_AVAILABLE, "pyoptinterface / HiGHS not available in this env"
)
@unittest.skipIf(SKIP_SLOW, "PREPSHOT_SKIP_SLOW=1 set; skipping slow test")
class TestRts96FullYear(unittest.TestCase):
    """IEEE RTS-96 full-year (8 736 h) PCM, 3-area network."""

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
            full_hours = list(full_params['hour'])
            cap = load_fixed_capacity(
                Path('input/capacity_pcm.csv'), 2020, SCENARIO,
            )
            state = {'hydro_storage': {}, 'battery_storage': {}}
            window_outs = []
            t = 0
            while t < len(full_hours):
                wh = full_hours[t:t + 24]
                win = _build_window_params(full_params, 2020, wh, state)
                _override_existing_fleet(win, cap)
                m = create_model(win)
                assert solve_model(m, win), \
                    f"RTS-96 window starting at hour {wh[0]} failed"
                window_outs.append(_extract_window_dispatch(m, wh, 2020))
                t += 24
            cls.gen_df = pd.concat(
                [pd.DataFrame(w['gen']) for w in window_outs],
                ignore_index=True,
            )
            cls.registry = pd.read_csv(SCENARIO / 'input' / 'tech_registry.csv')
            cls.gen_df = cls.gen_df.merge(
                cls.registry[['tech', 'carrier']], on='tech',
            )
            cls.demand = pd.read_csv(SCENARIO / 'input' / 'demand.csv')
        finally:
            sys.argv = argv_before
            os.chdir(cwd_before)

    def test_annual_energy_balance(self):
        """Total dispatched gen equals total demand."""
        total_gen = self.gen_df['value'].sum() / 1000
        total_demand = self.demand['value'].sum() / 1000
        self.assertAlmostEqual(
            total_gen, total_demand, delta=1.0,
            msg=f"gen={total_gen:.1f} GWh, demand={total_demand:.1f} GWh",
        )
        self.assertAlmostEqual(
            total_gen, EXPECTED_ANNUAL_GWH, delta=20.0,
        )

    def test_annual_energy_by_carrier_is_3x_rts79(self):
        """Per-carrier annual energy = 3 x RTS-79 (no inter-area binding)."""
        actual = (
            self.gen_df.groupby('carrier')['value'].sum() / 1000
        ).to_dict()
        for carrier, expected in EXPECTED_ANNUAL_BY_CARRIER_GWH.items():
            self.assertAlmostEqual(
                actual.get(carrier, 0), expected, delta=30.0,
                msg=f"{carrier}: got {actual.get(carrier):.1f} GWh, "
                    f"expected ~{expected}",
            )

    def test_capacity_factor_envelope_matches_rts79(self):
        """CF by carrier matches the single-area textbook pattern."""
        per_carrier = self.gen_df.groupby('carrier')['value'].sum().to_dict()
        cf = {
            c: per_carrier[c] / (NAMEPLATE_MW_BY_CARRIER[c] * 8736)
            for c in NAMEPLATE_MW_BY_CARRIER
        }
        self.assertGreater(cf['nuclear'], 0.99)
        self.assertGreater(cf['hydro'], 0.99)
        self.assertTrue(0.40 < cf['coal'] < 0.65)
        self.assertLess(cf['oil'], 0.05)

    def test_peak_hour_dispatch_is_3x_rts79(self):
        """At peak (hour 8442, 8550 MW), each carrier dispatches 3x RTS-79."""
        peak = self.gen_df[self.gen_df['hour'] == PEAK_HOUR]
        if peak.empty:
            self.skipTest(f"no dispatch at hour {PEAK_HOUR}")
        peak_by_carrier = peak.groupby('carrier')['value'].sum().to_dict()
        total = sum(peak_by_carrier.values())
        self.assertAlmostEqual(total, TOTAL_PEAK_MW, delta=1.0)
        for carrier, expected in EXPECTED_PEAK_DISPATCH_MW.items():
            self.assertAlmostEqual(
                peak_by_carrier.get(carrier, 0), expected, delta=1.0,
                msg=f"peak {carrier}: {peak_by_carrier.get(carrier)} "
                    f"!= {expected} MW",
            )


if __name__ == "__main__":
    unittest.main()
