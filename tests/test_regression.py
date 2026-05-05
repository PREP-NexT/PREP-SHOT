"""End-to-end regression test against the canonical ``examples/three_zone/`` dataset.

This test is the safety net that catches accidental changes to model
formulation, input loading, the cost objective, or the hydropower
head-iteration loop. It runs the full ``python run.py`` flow on the
standard ``examples/three_zone/`` dataset and locks in the final-iteration objective
value captured at the v1.1.x baseline.

If a future change perturbs the value beyond the tolerance, that is a
signal to investigate — either the change was intentional (update the
expected value here and note it in Changelog.rst) or it is an
unintended regression.

This test is **slow** (≈100 s on commodity hardware) because it runs
the head-iteration loop at the default config's ``iteration_number``.
Set ``PREPSHOT_SKIP_SLOW=1`` in the environment to skip it.
"""
import os
import sys
import unittest

try:
    import pyoptinterface as poi  # noqa: F401  imported to gate the test
    from prepshot.set_up import initialize_environment
    from prepshot.model import create_model
    from prepshot.solver import solve_model
    SOLVER_AVAILABLE = True
except ImportError:
    SOLVER_AVAILABLE = False


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCENARIO_DIR = os.path.join(REPO_ROOT, 'examples', 'three_zone')
SKIP_SLOW = os.environ.get('PREPSHOT_SKIP_SLOW') == '1'


@unittest.skipUnless(
    SOLVER_AVAILABLE, "pyoptinterface / HiGHS not available in this env"
)
@unittest.skipIf(SKIP_SLOW, "PREPSHOT_SKIP_SLOW=1 set; skipping slow test")
class TestRegressionDefaultInput(unittest.TestCase):
    """Lock in the final objective for the canonical ``examples/three_zone/`` dataset."""

    # Re-baselined at v1.16.0 with the full feature stack:
    # is_reserve=True (multi-product: regulation_up/regulation_down/
    # spinning/non_spinning), is_dc_flow=True, is_uc=True with
    # uc_relaxation="continuous". Drift history kept inline for
    # traceability:
    #   v1.1.1  : 1.8793771299e11  -- transport model, no reserve
    #   v1.12.0 : 1.8878269786e11  -- + reserve up/down (~+0.4 %)
    #   v1.13.0 : 1.8967979487e11  -- + DC flow Kirchhoff (~+0.5 %)
    #   v1.15.0 : 1.9070270274e11  -- + UC overlay (continuous relax)
    #   v1.16.0 : 1.9070043702e11  -- reserve generalized to 4
    #                                 products (regulation_up/_down,
    #                                 spinning, non_spinning); total
    #                                 requirement same as v1.12, just
    #                                 split across products.
    #   v1.17.0 : 1.9009490431e11  -- hydro now eligible for
    #                                 non_spinning (real markets
    #                                 typically allow this since hydro
    #                                 ramps from cold within 10 min).
    #                                 Slight drop because hydro can
    #                                 now serve more reserve products
    #                                 cheaply.
    EXPECTED_OBJECTIVE = 1.9009490431e11
    # 1 % tolerance — head iteration is non-trivial; this absorbs minor
    # numerical differences across HiGHS minor versions and platforms
    # without being so loose it stops catching real regressions.
    REL_TOLERANCE = 1e-2

    def test_default_input_full_solve(self):
        """Run the full python-run.py flow and check the final objective."""
        # initialize_environment uses argparse on sys.argv, so isolate it.
        # solve_model writes output relative to cwd, so cd into the scenario
        # directory for the whole test and restore on exit.
        argv_before = sys.argv
        cwd_before = os.getcwd()
        sys.argv = [argv_before[0]]
        os.chdir(SCENARIO_DIR)
        try:
            parameters = initialize_environment({
                'filepath': SCENARIO_DIR,
                'config_filename': os.path.join(SCENARIO_DIR, 'config.json'),
                'params_filename': os.path.join(SCENARIO_DIR, 'params.json'),
            })

            model = create_model(parameters)
            solved = solve_model(model, parameters)
        finally:
            sys.argv = argv_before
            os.chdir(cwd_before)
        self.assertTrue(solved, "solve_model returned False")

        objective = model.get_value(model.cost)
        rel_error = abs(objective - self.EXPECTED_OBJECTIVE)             \
            / self.EXPECTED_OBJECTIVE
        self.assertLess(
            rel_error, self.REL_TOLERANCE,
            f"objective drifted: got {objective:.6e}, "
            f"expected {self.EXPECTED_OBJECTIVE:.6e}, "
            f"relative error {rel_error:.2e}"
        )


if __name__ == "__main__":
    unittest.main()
