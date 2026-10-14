"""Constraints must follow the sparse ``(zone, tech)`` set.

Since the v1.20 sparsity refactor ``model.storage`` / ``model.gen`` /
``model.charge`` / ``model.cap_existing`` only exist for ``(zone, tech)``
pairs that have existing capacity or a candidate row. Constraints built
over the dense ``zone x tech`` product raised ``KeyError`` at model-build
time for a storage tech missing in some zone, and for any sparse tech set
once reserves were switched on.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest

try:
    import pyoptinterface as poi  # noqa: F401  imported to gate the test
    from prepshot.set_up import initialize_environment
    from prepshot.model import create_model
    SOLVER_AVAILABLE = True
except ImportError:
    SOLVER_AVAILABLE = False


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCENARIO_DIR = os.path.join(REPO_ROOT, 'examples', 'three_zone')
ZONE_WITHOUT_STORAGE = 'BA3'


def _build(scenario):
    """Build the model for ``scenario`` with argv / cwd isolated."""
    argv_before = sys.argv
    cwd_before = os.getcwd()
    sys.argv = [argv_before[0]]
    os.chdir(scenario)
    try:
        parameters = initialize_environment({
            'filepath': scenario,
            'config_filename': os.path.join(scenario, 'config.json'),
            'params_filename': os.path.join(scenario, 'params.json'),
        })
        return create_model(parameters)
    finally:
        sys.argv = argv_before
        os.chdir(cwd_before)


@unittest.skipUnless(
    SOLVER_AVAILABLE, "pyoptinterface / HiGHS not available in this env"
)
class TestSparseStorage(unittest.TestCase):
    """Build ``three_zone`` with Storage removed from one zone."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scenario = os.path.join(self._tmp.name, 'three_zone')
        shutil.copytree(
            SCENARIO_DIR, self.scenario,
            ignore=shutil.ignore_patterns('output', 'log')
        )
        # Drop every Storage candidate row of one zone, so that
        # (BA3, Storage) is no longer an active (zone, tech) pair.
        candidates = os.path.join(
            self.scenario, 'input', 'tech_candidates.csv'
        )
        with open(candidates, encoding='utf-8') as f:
            lines = f.readlines()
        prefix = f'{ZONE_WITHOUT_STORAGE},Storage,'
        with open(candidates, 'w', encoding='utf-8') as f:
            f.writelines(l for l in lines if not l.startswith(prefix))

    def tearDown(self):
        self._tmp.cleanup()

    def test_model_builds_when_storage_missing_in_a_zone(self):
        """create_model succeeds and storage constraints stay sparse."""
        model = _build(self.scenario)

        storage_zones = {z for (z, _te) in model.active_zt_storage}
        self.assertNotIn(ZONE_WITHOUT_STORAGE, storage_zones)
        self.assertTrue(storage_zones)
        for cons in (
            model.energy_storage_balance_cons,
            model.init_energy_storage_cons,
            model.end_energy_storage_cons,
            model.energy_storage_up_bound_cons,
            model.energy_storage_gen_cons,
            model.charge_up_bound_cons,
        ):
            self.assertEqual({key[-2] for key in cons}, storage_zones)



@unittest.skipUnless(
    SOLVER_AVAILABLE, "pyoptinterface / HiGHS not available in this env"
)
class TestSparseReserve(unittest.TestCase):
    """Build ``three_zone`` (hydro plants live in one zone each) with
    reserves switched on."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.scenario = os.path.join(self._tmp.name, 'three_zone')
        shutil.copytree(
            SCENARIO_DIR, self.scenario,
            ignore=shutil.ignore_patterns('output', 'log')
        )
        config = os.path.join(self.scenario, 'config.json')
        with open(config, encoding='utf-8') as f:
            cfg = json.load(f)
        cfg['reserve_parameters']['is_reserve'] = True
        with open(config, 'w', encoding='utf-8') as f:
            json.dump(cfg, f)

    def tearDown(self):
        self._tmp.cleanup()

    def test_model_builds_and_inactive_pairs_hold_no_reserve(self):
        """Headroom is built per active pair; reserve elsewhere is 0."""
        model = _build(self.scenario)

        active = set(model.active_zt)
        for cons in (
            model.reserve_headroom_up_cons,
            model.reserve_headroom_down_cons,
        ):
            self.assertTrue(cons)
            self.assertLessEqual({key[-2:] for key in cons}, active)
        # Every reserve variable on an inactive (zone, tech) pair is
        # pinned to zero, so it cannot serve the requirement for free.
        h, m, y = model.hour[0], model.month[0], model.year[0]
        for z in model.zone:
            for te in model.tech:
                if (z, te) in active:
                    continue
                for p in model.reserve_products:
                    self.assertIn(
                        (h, m, y, z, te, p), model.reserve_non_eligible_cons
                    )


if __name__ == "__main__":
    unittest.main()
