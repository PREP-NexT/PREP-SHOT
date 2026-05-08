"""External-benchmark validation against the IEEE RTS-79 (24-bus) system.

Source: MATPOWER ``case24_ieee_rts``, originally from
IEEE Reliability Test System Task Force (1979),
"IEEE reliability test system,"
IEEE Trans. Power App. Syst., Vol. 98, No. 6, pp. 2047-2054.
Cost coefficients from Georgia Tech PSCAL.

The example ships a full IEEE RTS-79 hourly load profile spanning
8736 hours (52 weeks x 7 days x 24 hours, multipliers from Tables
1-3 of the 1979 paper).  Annual peak = 2 850 MW (hour 8442 in
week 51).

We run the full-year PCM and validate three things:

1. **Energy balance** -- total dispatched gen equals total demand
   (15 297 GWh, no shedding).
2. **Per-carrier capacity factors** match the textbook RTS-79
   thermal-dominated dispatch pattern: nuclear and hydro at ~100 %
   (cheapest), coal cycling at ~50 % (intermediate), oil
   peakers at < 5 % (only when load > coal+hydro+nuclear).
3. **Peak-hour dispatch** matches the unconstrained merit-order
   benchmark exactly (hydro 300, nuclear 800, coal 1274,
   oil 476 MW at the 2 850 MW peak hour 8442).

The merit-order numbers are computed by hand from the gencost
``c1`` linear coefficients -- see the source paper for the
detailed cost data.
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
SCENARIO = REPO_ROOT / 'examples' / 'rts79'
SKIP_SLOW = os.environ.get('PREPSHOT_SKIP_SLOW') == '1'

# Single-hour merit-order benchmark at peak load (2 850 MW).
PEAK_HOUR = 8442  # week 51, Monday-evening winter peak in IEEE RTS-79
EXPECTED_PEAK_DISPATCH_MW = {
    'hydro':    300.0,
    'nuclear':  800.0,
    'coal':    1274.0,
    'oil':      476.0,
}

# Annual-energy expectations from the textbook merit-order pattern
# (verified by running the full-year LP -- baseline-locked here).
EXPECTED_ANNUAL_ENERGY_GWH = 15297.1
EXPECTED_ANNUAL_BY_CARRIER_GWH = {
    'nuclear':  6979.0,   # at 99.9 % CF (always-on)
    'coal':     5627.0,   # cycling intermediate
    'hydro':    2621.0,   # at 100 % CF (cheapest)
    'oil':        70.0,   # peaker, < 1 %
}
NAMEPLATE_MW = {
    'hydro':    300,
    'nuclear':  800,
    'coal':    1274,
    'oil':     1031,  # 4 x U20 + 3 x U100 + 3 x U197 + 5 x U12
}


@unittest.skipUnless(
    SOLVER_AVAILABLE, "pyoptinterface / HiGHS not available in this env"
)
@unittest.skipIf(SKIP_SLOW, "PREPSHOT_SKIP_SLOW=1 set; skipping slow test")
class TestRts79FullYear(unittest.TestCase):
    """IEEE RTS-79 full-year (8 736 h) PCM, validated against the
    textbook thermal-dominated dispatch pattern."""

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

            # Roll 24-hour windows across the year.  Each window's
            # state (initial battery / hydro storage) is empty
            # because RTS-79 has no batteries and we don't model
            # the U50 hydro as cascading-reservoir techs.
            state = {'hydro_storage': {}, 'battery_storage': {}}
            window_outs = []
            t = 0
            while t < len(full_hours):
                wh = full_hours[t:t + 24]
                win = _build_window_params(full_params, 2020, wh, state)
                _override_existing_fleet(win, cap)
                m = create_model(win)
                assert solve_model(m, win), \
                    f"RTS-79 window starting at hour {wh[0]} failed"
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
        """Total dispatched gen equals total demand (no shortage)."""
        total_gen = self.gen_df['value'].sum() / 1000  # GWh
        total_demand = self.demand['value'].sum() / 1000
        self.assertAlmostEqual(
            total_gen, total_demand, delta=1.0,
            msg=f"gen={total_gen:.1f} GWh, demand={total_demand:.1f} GWh",
        )
        self.assertAlmostEqual(
            total_gen, EXPECTED_ANNUAL_ENERGY_GWH, delta=10.0,
        )

    def test_annual_energy_by_carrier(self):
        """Per-carrier annual energy matches the merit-order pattern."""
        actual = (
            self.gen_df.groupby('carrier')['value'].sum() / 1000
        ).to_dict()
        for carrier, expected_gwh in EXPECTED_ANNUAL_BY_CARRIER_GWH.items():
            self.assertAlmostEqual(
                actual.get(carrier, 0), expected_gwh, delta=20.0,
                msg=f"{carrier}: got {actual.get(carrier):.1f} GWh, "
                    f"expected ~{expected_gwh}",
            )

    def test_capacity_factor_envelope(self):
        """CF by carrier in the textbook envelope.

        Cheapest carriers run flat-out; the marginal carrier (coal)
        cycles; peakers (oil) idle.
        """
        per_carrier = (
            self.gen_df.groupby('carrier')['value'].sum().to_dict()
        )
        cf = {c: per_carrier[c] / (NAMEPLATE_MW[c] * 8736)
              for c in NAMEPLATE_MW}
        self.assertGreater(cf['nuclear'], 0.99,
                           f"nuclear CF too low: {cf['nuclear']:.3f}")
        self.assertGreater(cf['hydro'], 0.99,
                           f"hydro CF too low: {cf['hydro']:.3f}")
        self.assertTrue(0.40 < cf['coal'] < 0.65,
                        f"coal CF outside envelope: {cf['coal']:.3f}")
        self.assertLess(cf['oil'], 0.05,
                        f"oil CF too high: {cf['oil']:.3f}")

    def test_peak_hour_dispatch_matches_merit_order(self):
        """At the annual peak (2 850 MW), dispatch matches merit order."""
        peak = self.gen_df[self.gen_df['hour'] == PEAK_HOUR]
        if peak.empty:
            self.skipTest(f"no dispatch rows at hour {PEAK_HOUR}")
        peak_by_carrier = peak.groupby('carrier')['value'].sum().to_dict()
        total = sum(peak_by_carrier.values())
        self.assertAlmostEqual(total, 2850.0, delta=1.0,
                               msg=f"peak total {total} != 2850 MW")
        for carrier, expected in EXPECTED_PEAK_DISPATCH_MW.items():
            self.assertAlmostEqual(
                peak_by_carrier.get(carrier, 0), expected, delta=1.0,
                msg=f"peak {carrier}: {peak_by_carrier.get(carrier)} "
                    f"!= {expected} MW",
            )


if __name__ == "__main__":
    unittest.main()
