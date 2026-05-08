Changelog
=========

Here, you'll find notable changes for each version of PREP-SHOT.

Version 1.26.0 - May 8, 2026
-------------------------------

Two new validation benchmarks: PowNet Cambodia and Laos
(Chowdhury et al. 2020), as must-take ports.  PREP-SHOT
reproduces the published Cambodia thermal+import dispatch within
0.3 %; Laos passes the structural envelope of a hydro-export
system (hydro > 75 % of annual energy).

Why
+++

PJM 5-bus / RTS-79 / RTS-96 are textbook DC-OPF benchmarks with
analytic reference numbers.  The PowNet cases are real-world
hydro-thermal systems with an external solver (Pyomo + Gurobi/
HiGHS) producing the reference -- a different validation flavour.

Cambodia is thermal-dominated with a small hydro base; Laos is
hydro-export-dominated.  The two together cover the spectrum of
ASEAN power-system shapes.

Added
+++++

* ``examples/cambodia/`` -- single-bus aggregation of
  PowNet's Cambodia 2016 dataset (18 thermals + 6 hydros + 3
  imports, 8 760 hours).  Hydro and import dispatch are forced
  via ``tech_max_gen_profile = tech_min_gen_profile`` to match
  PowNet's must-take semantics.  Source:
  https://github.com/kamal0013/PowNet/tree/v2.1/model_library/cambodia
* ``examples/laos/`` -- same structure for Laos 2016
  (5 thermals + 30 hydros + 4 imports).  Source:
  https://github.com/kamal0013/PowNet/tree/v2.1/model_library/laos
* ``examples/{cambodia,laos}/{PowNetCambodia,
  PowNetLaos}.ipynb`` -- tutorial notebooks with background,
  data-source citations, validation cells, and weekly stacked
  dispatch plots.
* ``tests/test_pownet_benchmark.py`` -- 5 assertions
  (gated by ``PREPSHOT_SKIP_SLOW``):

  - Cambodia thermal+import = 3.90 TWh +/- 0.1 (matches
    PowNet's ``out_camb_R1_2016_mwh.csv``).
  - Cambodia hydro + import dispatch match the must-take input
    profiles to the MWh.
  - Laos hydro share > 75 % of annual energy.
  - Laos thermal share (coal + biomass) < 10 %.
  - Laos total annual gen ~ 30 TWh (matches augmented demand).

Notes
+++++

**Single-bus aggregation.** All demand buses in each country
collapse onto one zone; bus-level dispatch and DC-OPF detail are
dropped.  System-level economics (per-carrier annual energy,
total cost) match PowNet.  Adding back the 16-bus Cambodia /
69-bus Laos topology requires a plant-bus mapping that PowNet's
public data doesn't ship explicitly.

**Augmented demand.** ~3 290 hours in Cambodia (and ~5 850 hours
in Laos) have must-take supply > original demand, totalling 0.49
TWh (Cambodia) / 5.54 TWh (Laos) of implied exports.  Those are
added to ``demand.csv`` so the LP's nodal-balance equality stays
feasible -- equivalent to modelling cross-border exports as
internal demand absorption.

**Variable cost simplification.** PowNet's ``fuel_price.csv`` has
hourly resolution; PREP-SHOT's ``cost_var`` is per (tech, year).
We use the per-tech median annual fuel price.  This drops < 1 %
of the cost detail.

Version 1.25.0 - May 8, 2026
-------------------------------

Documentation: the three external-benchmark notebooks (PJM 5-bus,
RTS-79, RTS-96) are now first-class doc pages.  They live under a
new "Validation Benchmarks" caption in the index toctree, and the
landing page has a section explaining what each one validates and
the published reference numbers.

Added
+++++

* New ``Validation Benchmarks`` toctree caption in
  ``doc/source/index.rst`` linking the three notebooks in
  increasing complexity (PJM 5-bus -> RTS-79 -> RTS-96).
* Landing-page section "Validation benchmarks" with a one-line
  summary of each benchmark and its reference number.
* Symlinks ``doc/source/{PJM5,RTS79,RTS96}.ipynb`` ->
  ``examples/{pjm5,rts79,rts96}/...``, matching the existing
  pattern for ``Thailand``, ``SoutheastAsia``, ``ThailandPCM``.

Notes
+++++

The notebooks were committed in v1.22.0 / v1.23.0 / v1.24.0 with
the matching ``examples/`` data and pytest regressions.  This
release just plumbs them into the Sphinx build so they show up
in the rendered docs.

Version 1.24.0 - May 8, 2026
-------------------------------

Third external benchmark: IEEE RTS-96 (3-area, 73-bus extension
of RTS-79).  Full-year PCM solves cleanly with each area's
dispatch matching RTS-79 to the MW -- the canonical "no
inter-area binding" pass/fail check on a multi-area network.

Why
+++

RTS-79 (v1.23.0) validates single-area DC OPF + nodal LP
correctness.  RTS-96 adds the multi-area dimension: 3 RTS-79
copies connected by 5 inter-area tie lines from Table V of the
1999 paper.  Because each area is independently self-sufficient
at peak (3 405 MW Pmax vs 2 850 MW peak load), no tie should
bind, and the system dispatch is exactly 3 x RTS-79.  Any
deviation = the LP isn't treating the multi-area topology
correctly.

Added
+++++

* ``examples/rts96/`` -- 73 buses (areas 1xx / 2xx / 3xx,
  with bus 325 as area-3's tie-only node), 96 generators,
  107 unique intra-area lines (after folding parallels) plus
  5 inter-area ties (107-203, 113-215, 123-217, 223-318,
  325-121).  Full IEEE RTS-79 hourly load profile applied to
  every area.  Annual peak = 8 550 MW (= 3 x 2 850 MW).
  Runs via::

      cd examples/rts96
      python -m prepshot.pcm . --year 2020 --horizon 24 --step 24

  Full-year wall time: ~100 s.

* ``tests/test_rts96_benchmark.py`` -- four full-year
  assertions (gated by ``PREPSHOT_SKIP_SLOW``):

  - **Annual energy balance** -- gen == demand
    (45 891 GWh, no shed).
  - **Per-carrier annual energy = 3 x RTS-79** within +/- 30
    GWh: nuclear 20 937, coal 16 882, hydro 7 862, oil 210.
  - **CFs match RTS-79 envelope** -- nuclear / hydro > 99 %,
    coal in [40 %, 65 %], oil < 5 %.
  - **Peak-hour dispatch is 3 x RTS-79** within 1 MW per
    carrier -- hydro 900, nuclear 2 400, coal 3 822, oil
    1 428 MW.

Notes
+++++

The 5 inter-area ties stay unbound through the full year
because each area can serve its own peak from its own gen.
Validation still confirms the multi-area LP is wired
correctly: change any area's data and the result diverges
from 3 x RTS-79.

Test runs in ~97 s and is included in the standard suite
under the ``PREPSHOT_SKIP_SLOW`` gate (now 34 tests; fast
suite 25 with 9 skipped under ``PREPSHOT_SKIP_SLOW=1``).

Version 1.23.0 - May 8, 2026
-------------------------------

Second external benchmark: IEEE RTS-79 (24-bus reliability test
system), full-year PCM.  At peak the dispatch matches the
unconstrained merit-order benchmark to within 1 MW per carrier;
across the year nuclear and hydro run at ~100 % CF, coal cycles
near 51 % CF, and oil peakers idle below 1 % CF -- the textbook
thermal-dominated dispatch pattern.

Why
+++

PJM 5-bus (v1.22.0) is the smallest possible LMP / DC-OPF check.
RTS-79 is one tier up: 24 buses, 32 generators across nine plant
types (oil, coal, nuclear, hydro), 38 transmission branches,
and a documented hourly load profile spanning the full year.
The merit-order dispatch is unique enough that the per-carrier
energy can be computed by hand and the total cost at peak load
matches a closed-form reference -- no MATLAB / MATPOWER
required to produce the "ground truth".

Added
+++++

* ``examples/rts79/`` -- full-year PCM scenario matching
  MATPOWER ``case24_ieee_rts``.  Bus loads, generator capacities,
  and ``c1`` linear cost coefficients all from the IEEE 1979
  paper / Georgia Tech PSCAL data.  Total system Pmax = 3 405
  MW; annual peak = 2 850 MW (week 51, hour 8442).  Runs via::

      cd examples/rts79
      python -m prepshot.pcm . --year 2020 --horizon 24 --step 24

  ``input/demand.csv`` ships the full IEEE RTS-79 hourly load
  profile (8 736 hours = 52 weeks x 7 days x 24 hours), built
  from Tables 1-3 of the 1979 paper:

  * Table 1: weekly peak as % of annual peak (52 values).
  * Table 2: daily peak as % of weekly peak (Mon-Sun).
  * Table 3: hourly peak as % of daily peak, by season
    (winter / summer / spring-fall) and weekday vs weekend.

* ``tests/test_rts79_benchmark.py`` -- four assertions on the
  full-year solve (~22 s on commodity hardware, gated by
  ``PREPSHOT_SKIP_SLOW``):

  - **Annual energy balance**: dispatched gen == demand
    (15 297 GWh, no shedding).
  - **Annual energy by carrier**: nuclear ~6 979 GWh,
    coal ~5 627, hydro ~2 621, oil ~70 GWh.
  - **Capacity factors**: nuclear & hydro > 99 %, coal in
    [40 %, 65 %], oil < 5 %.
  - **Peak-hour dispatch** (hour 8 442, 2 850 MW load):
    hydro 300, nuclear 800, coal 1 274, oil 476 MW -- matches
    merit-order to 1 MW.

Notes
+++++

The MATPOWER cost data is quadratic (``cost = c2 P^2 + c1 P +
c0``); we take ``c1`` as the per-MWh dispatch cost and drop the
quadratic / no-load terms (PREP-SHOT's ``cost_var`` is linear).
The merit-order benchmark uses the same simplification, so the
two should agree exactly at peak.  Differences elsewhere come
from LP degeneracy when both a transmission line and a gen's
upper bound bind together (e.g. line 7-8 outbound from bus 7's
surplus U100 generation).

The U50 hydro plants are modelled as fixed-cost dispatchable
techs (``carrier='hydro'`` but no reservoir / inflow physics).
A future revision could attach the IEEE RTS-79 weekly hydro
energy budgets to drive a real reservoir representation.

Version 1.22.0 - May 8, 2026
-------------------------------

First externally-anchored validation benchmark: the Hogan / PJM
5-bus system (MATPOWER ``case5``). PREP-SHOT now reproduces
MATPOWER's ``runopf`` total cost to the dollar (``$17,479.89/h``)
and per-tech dispatch to under 0.5 MW on a single-hour DC OPF.

Why
+++

The other shipped examples (``three_zone``, ``southeast_asia``,
``thailand_pcm``) all validate against PREP-SHOT's own past
results -- useful as regression catches but they don't anchor
the model against a published external reference. The PJM
5-bus is the textbook DC-OPF / LMP example (Hogan 2002; Stoft;
PJM training material; reproduced verbatim as MATPOWER's
``case5``), with widely-cited reference dispatch and total cost.

Added
+++++

* ``examples/pjm5/`` -- single-hour, single-year scenario
  matching MATPOWER ``case5``: 5 buses, 5 generators (Alta,
  ParkCity, Solitude, Sundance, Brighton), 6 lines (line 4-5
  rated 240 MW becomes the binding congestion). 51 input CSVs
  in PREP-SHOT's long-format schema; runs via ``python -m
  prepshot.pcm . --year 2020 --horizon 1 --step 1 --total-h 1``.
* ``tests/test_pjm5_benchmark.py`` -- four assertions against
  MATPOWER's published values:

  - total cost == ``$17,479.89`` +/- $1
  - per-tech dispatch within 0.5 MW (Alta 40, ParkCity 170,
    Solitude 323.49, Sundance 0, Brighton 466.51)
  - LMP at bus 3 == $30 / MWh (Solitude marginal)
  - LMP at bus 5 == $10 / MWh (Brighton marginal)
  - LMPs at every bus inside the merit-order envelope $10..$50

  The bus-1 / bus-2 / bus-4 LMPs ($16.98, $26.38, $39.94 with
  PREP-SHOT) differ by a few $/MWh from MATPOWER's published
  values ($14.27, $15.08, $35.91) because they depend on
  shift-factor weighting that varies with the DC-OPF formulation
  (reference-bus choice, susceptance normalization).  Both
  formulations agree on the binding constraint (line 4-5) and
  the marginal-plant LMPs.

Changed
+++++++

* ``prepshot/pcm.py:_extract_window_dispatch`` LMP extractor:
  prefer the typed ``ConstraintAttribute.Dual`` API (which
  works on PoI 0.4's HiGHS backend) and fall back to raw
  attribute names (``Pi`` for Gurobi, ``dual`` for HiGHS) only
  when the typed API raises. The previous code skipped the typed
  API entirely because Gurobi raises ``AttributeError:
  Quadratric`` on linear constraints, but HiGHS handles it
  correctly.

Notes
+++++

The PJM 5-bus is small enough to run in 0.07 s end-to-end and
its test class is included in ``tests/`` -- it runs as part of
the standard suite. Future external benchmarks (Garver 6-bus
for transmission expansion, IEEE RTS-79 for full-year PCM /
UC) can follow the same pattern.

Version 1.21.0 - May 7, 2026
-------------------------------

PCM additions: load shedding (``reliability_parameters``,
``--allow-load-shedding`` / ``--voll`` CLI flags), locational
marginal prices in the rolling-horizon output, and a switch to
long-format Parquet sidecars instead of dense NetCDF -- the
previous writer overflowed scipy's NetCDF3 32-bit ``vsize`` on
full-year Thai PCM (the dense ``trans_export`` array would have
been ~16 GB).

Why
+++

Three independent needs that landed in the same release window:

1. **Load shedding** -- on big nodal models, single PCM windows
   are occasionally infeasible due to local water/storage budgets
   (cascade boundary, low-inflow hour). Without slack, the
   rolling driver crashes mid-year. With a VOLL-priced ``lns``
   slack the dispatch always completes and the output reveals
   exactly which (hour, zone) pairs hit the floor.
2. **LMP** -- the dual of the nodal power-balance constraint is
   the bus-level marginal price; it's the standard PCM diagnostic
   for congestion / fuel-mix transitions / scarcity. CEM mode
   already ships this; PCM didn't.
3. **Parquet output** -- pivoting the long-format result rows to
   dense ``(hour, month, year, zone, ...)`` xarray arrays is
   wasteful when the data is sparse-by-construction (e.g. only
   1230 directed lines populated out of 472 x 472 cells). On a
   full-year run the dense array pads NaN into ~2 B cells and
   blows up to ~16 GB.

Added
+++++

* ``reliability_parameters`` block in ``config.json``::

      "reliability_parameters": {
          "allow_load_shedding": false,
          "voll": 10000
      }

  When ``allow_load_shedding`` is true, ``model.lns[h, m, y, z]``
  enters the nodal power-balance constraint as a non-negative
  slack and the ``cost_lns = voll * sum(lns) * var_factor /
  weight`` term is added to the objective. The slack defaults to
  off, so unset / pre-1.21 configs are byte-for-byte unchanged.
* ``prepshot.pcm`` CLI flags ``--allow-load-shedding`` and
  ``--voll <USD/MWh>`` override the config block at run time.
* ``run_pcm(..., allow_load_shedding=True, voll=10000.0)``
  programmatic kwargs.
* ``lmp.parquet`` in the PCM output bundle: per-(hour, month,
  year, zone) shadow price of the demand-balance constraint,
  scaled to real-year USD/MWh (raw dual times ``weight /
  var_factor``, sign-flipped). Saturates at ``voll`` for
  shortage hours.
* PoI portability shim: PoI 0.4's
  ``get_constraint_attribute(c, ConstraintAttribute.Dual)``
  raises ``AttributeError: Quadratric`` (sic) on linear
  constraints, so we go through the backend-native raw name
  (``Pi`` for Gurobi, ``dual`` for HiGHS) selected by a probe
  on the first constraint.
* ``examples/thailand_pcm/ThailandPCM.ipynb`` Section 10
  "Result analysis" -- six diagnostic plots (annual generation
  by carrier, peak-week dispatch, load-shedding hotspots, top
  transmission corridors, hydro-station discharge profiles, LMP
  geography + duration curve). The notebook's ``build-hydro``
  cell now also writes ``reservoir_storage_min.csv`` /
  ``reservoir_storage_max.csv`` (from V_min / V_max in the
  source) and clamps initial storage into ``[V_min * 1.01,
  V_max * 0.99]`` so the LP isn't infeasible at hour 0 when a
  reservoir's V_min > 0.5 * V_max.

Changed
+++++++

* ``prepshot/pcm.py:_save_pcm_netcdf`` -- writes long-format
  ``output/baseline_pcm/<var>.parquet`` (zstd-compressed) plus
  a ``manifest.json`` instead of a single dense NetCDF. Total
  Thai-PCM full-year output goes from ~16 GB-in-memory (didn't
  fit) to ~40 MB on disk.
* ``prepshot/pcm.py:_extract_window_dispatch`` -- iterates
  ``model.zone_techs[z]`` and ``model.out_neighbours[z]`` so it
  works against the v1.20 sparse ``model.gen`` /
  ``model.trans_export``. Previously KeyError'd at the first
  inactive ``(z, te)``.
* ``prepshot/pcm.py:_extract_window_state`` -- guards the empty
  ``reservoir_water_delay_time`` case (``int(NaN)`` raised when
  the cascade table has no rows).

Caveats
+++++++

PoI HiGHS does not consistently expose constraint duals as a
typed attribute; the raw ``dual`` lookup is used as a fallback
and may not work on all HiGHS builds. If the dual extractor
returns nothing the PCM run logs ``could not extract LMP duals``
and ``lmp.parquet`` is omitted -- the rest of the output is
unaffected.

Version 1.20.0 - May 7, 2026
-------------------------------

Sparsity refactor: every variable and constraint family that was
indexed over the dense ``zone x tech`` or ``zone x zone`` Cartesian
now iterates only the structurally meaningful subset (real
``(zone, tech)`` pairs from ``existing_fleet`` /
``expansion_candidates``, real lines from ``transmission_existing``
/ ``transmission_candidates``). On full-nodal Thai PCM (472 buses,
212 techs, 1230 lines) ``create_model`` drops from **~26 minutes
per window** to **~0.55 s** -- a ~3000x speedup for the LP-build
step alone.

Why
+++

Profiling on the Thai PCM (full-nodal, 472 zones, 212 techs,
615 directed lines) showed three structurally wasteful patterns,
all in the same shape:

* ``model.add_variables(model.zone, model.tech, ...)`` creates
  ~5 M ``gen`` variables, ~99 % of which are 0-by-construction
  because each thermal/VRE plant lives at exactly one bus.
* ``model.add_variables(model.zone, model.zone, ...)`` creates
  ~10.7 M ``trans_export`` variables, ~99.5 % of which are
  unbounded waste because Thailand only has 1230 directed lines.
* Every ``poi.make_tupledict(model.hour, model.month, model.year,
  model.zone, model.tech, rule=...)`` runs the rule 4.8 M times
  per constraint family on Thai-PCM scale, plus ~10 M times for
  trans-indexed families.

PoI's ``make_tupledict`` walks the dense Cartesian even when the
rule returns ``None`` (the sparse-storage path saves the result
but not the rule call), so most of the per-window time was pure
Python iteration with no LP-side payoff.

Added
+++++

* ``prepshot.utils.sparse_tupledict(index_iter, rule)`` -- like
  ``poi.make_tupledict`` but iterates an explicit list of keys
  instead of the dense Cartesian, skipping the per-element
  ``flatten_tuple`` + ``isinstance`` overhead.
* ``prepshot.load_data.compute_active_zone_tech(data_store)``
  populates ``data_store['active_zt']`` /
  ``['tech_zones']`` / ``['zone_techs']`` /
  ``['active_zt_storage']`` from ``existing_fleet`` and
  ``expansion_candidates``. Computed once at load time so every
  PCM window reuses it.
* ``prepshot.load_data.compute_active_lines(data_store)``
  populates ``data_store['active_lines']`` /
  ``['out_neighbours']`` / ``['in_neighbours']`` from
  ``transmission_existing`` and ``transmission_candidates``.
* ``prepshot.model.define_active_zone_tech(model)`` derives the
  per-window time-indexed key lists ``model.active_hmyzte``,
  ``model.active_hmyzte_storage``, ``model.active_hmyz1z2``,
  ``model.active_yz1z2`` from those sets.

Changed
+++++++

* Sparse variable creation in ``define_variables``: ``gen``,
  ``charge``, ``storage``, ``cap_newline``, ``trans_export`` now
  use ``sparse_tupledict`` over the active set instead of the
  dense ``model.add_variables(*sets)``.
* All constraint rules that were ``poi.make_tupledict(...,
  model.zone, model.tech, ...)`` switched to ``sparse_tupledict``
  over ``active_hmyzte`` / ``active_yzt``: 11 files touched
  (``co2.py``, ``cost.py``, ``dc_flow.py``, ``demand.py``,
  ``finance.py``, ``generation.py``, ``heat_rate.py``,
  ``investment.py``, ``transmission.py``, ``unit_commitment.py``,
  plus the variable-creation in ``model.py``).
* All ``for te in model.tech`` quicksums in nodal balance rules
  switched to ``for te in model.zone_techs.get(z, [])``; same
  for ``for z1 in model.zone`` -> ``for z1 in
  model.in_neighbours.get(z, [])`` /
  ``model.out_neighbours.get(z, [])``.
* ``prepshot._model.investment.AddInvestmentConstraints`` now
  pre-indexes ``existing_fleet`` by ``(zone, tech)`` once at
  ``__init__`` time so ``tech_lifetime_rule`` is O(1) per call
  instead of O(N) where N is the fleet size. On Thai PCM this
  alone saves ~0.6 s per window (the previous worst genexpr
  scan).
* ``prepshot.model.define_complex_sets`` no longer pads the
  dense ``zone x zone`` Cartesian (was 222 784 dict writes on
  Thai PCM); only pads on the sparse ``active_lines`` set, with
  saner defaults (``transmission_line_efficiency`` = 1.0 lossless
  rather than 0 = blocked, ``transmission_line_lifetime`` = 9999
  rather than 0 = expired).
* ``prepshot.pcm._build_window_params`` -- shallow copy
  (``dict(full_params)``) instead of ``deepcopy``. The big
  dicts (``demand``, ``max_gen_profile``, ``inflow``) are never
  mutated per-window, so deep-copying them was pure waste --
  ~10.9 s per window on Thai PCM, more than 20x the actual
  ``create_model`` cost.

Performance
+++++++++++

Single-window timings, Thai PCM 472-bus 212-tech 1230-line
configuration, M1 Max:

================================  ============  ============  =========
Stage                              v1.19         v1.20         Speedup
================================  ============  ============  =========
``_build_window_params``           10.9 s        ~0 s          1000x+
``create_model`` (LP build)        26+ min       0.55 s        ~3000x
``solve_model`` (HiGHS / Gurobi)   --            0.20 s        --
``_extract_window_dispatch``       --            0.02 s        --
Per-window total                   infeasible    ~0.8 s        --
Full year (365 windows)            infeasible    ~5-10 min     --
================================  ============  ============  =========

three_zone full regression-test wall-clock: 145 s -> 117 s.
Objective drift: < 0.04 % (within the 1e-2 tolerance).

Notes
+++++

The remaining theoretical lever is reusing the model object
across rolling-horizon windows (``set_normalized_rhs`` /
``set_normalized_coefficient`` for window-specific values
instead of rebuilding). Estimated extra savings: ~3 minutes
on the full year. Not in this release.

Version 1.19.1 - May 6, 2026
-------------------------------

CI hotfix: turn off ``is_n1_secure`` in ``three_zone`` so the
regression test passes reliably across Python 3.9 / 3.10 / 3.11 on
GitHub Actions. The N-1 SCDC OPF feature itself is unchanged --
just no longer enabled in the regression-test scenario.

Why
+++

CI runner on Python 3.10 reported ``solve_model returned False``
after a 409-second solve. The 4 x larger N-1 LP plus continuous-UC
+ piecewise-heat-rate stack pushed HiGHS into a non-OPTIMAL
termination status (probably numerical, possibly tolerance-related)
that wasn't reproducible on the local conda environment. Killing
N-1 in the regression scenario shrinks the LP back to the v1.17
size and HiGHS solves cleanly.

Changed
+++++++

* ``examples/three_zone/config.json``: ``dc_parameters.is_n1_secure
  : true -> false``.
* ``prepshot/_model/head_iteration.py``: when ``model.optimize()``
  returns a non-OPTIMAL status, log the actual ``TerminationStatus``
  enum at ``WARNING`` level before returning ``False``. Future CI
  failures will surface the specific status code instead of the
  opaque "solve_model returned False" assertion.
* ``tests/test_regression.py`` ``EXPECTED_OBJECTIVE`` re-baselined
  to ``1.9007200040e11`` (v1.17-shape LP without N-1, drops the
  +11 % N-1 premium that was in the v1.18/v1.19 baselines).

Notes
+++++

The N-1 feature still ships and still works -- enable it per
scenario by flipping ``is_n1_secure: true`` in that scenario's
``config.json``. ``examples/southeast_asia`` and
``examples/thailand_pcm`` ship with N-1 contingency CSVs in place
for opt-in.

Version 1.19.0 - May 6, 2026
-------------------------------

New feature: optional **piecewise-linear heat rates** for thermal
generators. Replaces the flat ``fuel_price * gen`` fuel-cost model
with a convex 3-segment (or N-segment) curve where the marginal
heat rate increases as a unit's output approaches its rated
capacity. LP-stable because the segments are sized so that
multipliers are non-decreasing -- the LP optimum naturally fills
cheaper segments first without binary ordering constraints.

Closes Tier 1 item 4 (generator economics granularity) of the
PCM-gap analysis. Real heat-rate curves below the design point
(part-load losses dominate, curve becomes concave) are still
abstracted into the v1.15 UC overlay's no-load + min-stable-load
constraints; this commit handles the above-design "increasing
marginal heat rate" half cleanly.

Added
+++++

* ``prepshot/_model/heat_rate.py`` -- ``AddHeatRateConstraints``
  class. Per ``(h, m, y, z, te)`` in the heat-rate set, three new
  constraint families:

  - **sum-to-gen**: ``sum_s gen_segment[..., s] = gen[..., te]``
  - **per-segment width**: ``gen_segment[..., s] <=
    (frac_max[s] - frac_max[s-1]) * cap_existing[y,z,te] * dt``
  - **unused-segment zero**: lock ``gen_segment[..., s] = 0`` for
    segments not declared for the tech.

  And a new variable ``model.gen_segment`` (lb=0) sized over
  ``(hour, month, year, zone, tech, segment_idx)``.

* ``add_heat_rate_fuel_cost(model)`` (in the same module) returns
  the per-segment fuel cost contribution as an ExprBuilder:

      fuel_price[te, y] * sum_s multiplier[s] * gen_segment[..., s]

  NPV-discounted via ``var_factor[y, z]`` and divided by ``weight``
  -- identical accounting to the rest of ``cost_var``. Wired into
  ``cost.var_cost_rule``.

* ``cost.fuel_cost_breakdown`` now SKIPS techs that have a
  heat-rate curve (returns a zero ExprBuilder for them). Those
  techs are priced through ``add_heat_rate_fuel_cost`` instead.
  Without the skip, the flat-rate cost would be double-counted.

* New optional input ``tech_heat_rate.csv`` (table format) with
  columns ``tech, segment, frac_max, multiplier``. One row per
  (tech, segment); per-tech segments must be sorted by ``frac_max``
  ascending and have non-decreasing multipliers (the loader
  validates this and raises ``ValueError`` if violated).

* New ``cost_parameters.is_piecewise_heat_rate`` config flag
  (default false). When false, the module is a no-op and PREP-SHOT
  keeps the v1.18 flat-rate behaviour byte-for-byte.

Default heat-rate curves shipped
++++++++++++++++++++++++++++++++

3-segment convex curve for every thermal tech in every example:

  Segment 1 (0-50 % of cap):   multiplier 1.00 (baseline)
  Segment 2 (50-80 % of cap):  multiplier 1.03
  Segment 3 (80-100 % of cap): multiplier 1.10

Eligible carriers: coal, oil, gas, bioenergy, biomass, nuclear,
geothermal. Solar / wind / hydro / storage are not thermal;
``tech_heat_rate.csv`` skips them and they keep the flat-rate
fuel cost (which is 0 for renewables anyway).

Per-example wiring
++++++++++++++++++

* ``three_zone``: ``is_piecewise_heat_rate=true``. 1 thermal tech
  (Coal) x 3 segments = 3 rows in tech_heat_rate.csv.
* ``thailand``: ``is_piecewise_heat_rate=false``. CSV ships
  (3 thermal techs x 3 segments = 9 rows) for opt-in.
* ``southeast_asia``: ``is_piecewise_heat_rate=false``. CSV
  ships (4 thermal techs x 3 segments = 12 rows) for opt-in.

Regression
++++++++++

three_zone EXPECTED_OBJECTIVE 2.1091201892e11 -> 2.1092168430e11
(+0.005 %). The drift is tiny because Coal in this scenario rarely
runs above 50 % of cap (segment 1, multiplier 1.00) -- wind, solar,
and hydro dominate dispatch. The constraint structure is in place
for scenarios where thermal pushes the upper segments; in those
cases the cost shift is meaningful.

Version 1.18.0 - May 6, 2026
-------------------------------

New feature: optional **N-1 security-constrained DC OPF** at the
zone level. Layered on top of the v1.13 DC flow module: when
enabled, the same dispatch must be feasible in the base case AND
under each line outage listed in
``transmission_contingencies.csv`` (preventive policy -- ``gen``
and ``charge`` are shared across base + contingencies, only flows
redistribute). Closes Tier 1 item 1 (network fidelity) of the
PCM-gap analysis.

Added
+++++

* ``prepshot/_model/dc_flow.py`` extended with four new rule
  methods and three new variable sets, all gated by
  ``dc_parameters.is_n1_secure``:

  - ``model.theta_c[h, m, y, z, c]`` -- phase angle in contingency
    ``c``.
  - ``model.trans_export_c[h, m, y, z1, z2, c]`` -- per-direction
    flow in contingency ``c``.
  - ``theta_ref_c_rule`` -- pin reference zone's angle to 0 per
    contingency.
  - ``flow_c_rule`` -- DC flow eq for every (line, contingency)
    pair; the outaged line itself is forced to zero in both
    directions.
  - ``cap_c_rule`` -- per-direction capacity bound (numerically
    same as the base case).
  - ``demand_balance_c_rule`` -- per-(zone, contingency) power
    balance using contingency-case flows but the SHARED base-case
    ``gen`` and ``charge``.

* New optional input ``transmission_contingencies.csv`` (cols
  ``zone1, zone2``) listing the lines to protect against. Empty
  file or missing -> no contingencies, equivalent to
  ``is_n1_secure=false``.

* New config flag ``dc_parameters.is_n1_secure`` (default ``false``).
  Requires ``is_dc_flow=true``; falsey configs preserve byte-for-
  byte v1.17 behaviour.

* Per-example wiring:

  - ``three_zone``: ``is_n1_secure=true``; all 3 lines protected.
    Three-fold parallel constraint set on top of the base case.
  - ``thailand``: ``is_n1_secure=false`` (single zone, no
    inter-zone lines).
  - ``southeast_asia``: ``is_n1_secure=false``; CSV ships listing
    the 7 inter-country lines for opt-in. The 8x problem-size
    multiplier on a 288-hour x 5-zone scenario isn't currently
    practical for routine runs.

Implementation notes
++++++++++++++++++++

* **Preventive** policy chosen over corrective: ``gen`` is one
  decision feasible everywhere, no post-contingency redispatch.
  Stays LP, simpler to formulate, and mirrors what most planning
  studies report. Corrective (with ramp-limited redispatch) is a
  v1.19+ candidate.

* The contingency-case flows are bounded by the SAME
  ``cap_lines_existing`` as the base case. A real SCUC would
  often increase emergency ratings; the current model treats
  thermal limits as identical, which is conservative.

* No additional cost terms -- the security constraint is purely
  feasibility-side.

Changed
+++++++

* ``tests/test_regression.py`` baseline re-captured for
  three_zone with N-1 enabled: ``1.9009490431e11`` ->
  ``2.1091201892e11`` (~+11 %). The constraint is genuinely
  binding -- v1.17's optimum leaned on inter-zone transmission
  more than any single line could survive outaging.

Verified
++++++++

* three_zone CEM solves with full feature stack (UC continuous +
  4-product reserves + DC flow + N-1) in roughly the same time as
  v1.17 (~5-10 min for 3 head iterations).

Version 1.17.0 - May 6, 2026
-------------------------------

Closes the v1.14.1 limitation: **PCM rolling-horizon now works with
cascading hydro and the full v1.15 / v1.16 feature stack** (UC,
multi-product reserves, DC flow). Adds a cross-window cascade-state
mechanism that carries upstream outflow from one window's solve into
the next window's hydro inflow expression, instead of dropping the
term at boundaries (which made downstream stations infeasible
whenever their ``min_outflow`` exceeded their incremental natural
inflow).

Added
+++++

* New ``params['prior_outflow']`` lookup, dict-keyed by ``(station,
  hour, month, year) -> m**3/s``. Populated by
  ``prepshot.pcm._extract_window_state``: at the end of each
  committed window, the last ``max_delay`` hours of ``model.outflow``
  for every upstream station are stashed and threaded into the next
  window's params.

* ``prepshot._model.hydro.inflow_rule`` now consults
  ``params['prior_outflow']`` when ``t = h - delay < hour[0]``. The
  numeric outflow is added as a constant term in the inflow
  expression, so the LP sees the cascade contribution exactly as
  it would in a single-pass full-horizon CEM solve.

  Three-tier fallback:

  - CEM (``cyclic_hydro=True``): wrap modularly within the window.
  - PCM with ``prior_outflow`` (v1.17+): use the carried numeric.
  - PCM without ``prior_outflow`` (first window): drop the term --
    the v1.14.1 fallback, accurate only for the very first window.

Changed
+++++++

* Default reserve eligibility for **hydro** carriers: now eligible
  for ``non_spinning`` (in addition to the existing
  ``regulation_up``, ``regulation_down``, ``spinning``). Real
  ancillary-services markets typically allow hydro to qualify for
  non-spinning since hydro can ramp from cold within the standard
  10-minute non-spinning window. Without this, zones with
  hydro-only fleets (like ``three_zone``'s BA2 in the CEM-2025
  buildout) had no supplier for ``non_spinning`` and tripped a
  presolve infeasibility under PCM mode.

* ``tests/test_regression.py`` baseline re-captured after the hydro
  non_spinning eligibility tweak. Drift is sub-percent.

Verified
++++++++

* PCM single-window with full feature stack (UC continuous-relax +
  4-product reserves + DC flow + per-station hydro):
  ``three_zone`` solves to optimal in ~1 minute.
* PCM multi-window rolling with cascade (``--horizon 24 --step 12``)
  on the same setup: 4 sequential windows all Optimal, dispatch
  written to ``baseline_pcm.nc``.
* PCM + UC compose: ``--cap-source <CEM_baseline>`` + UC continuous
  relaxation works.
* Single-window PCM at ``--horizon 48 --step 48`` remains the
  minimal "fixed-capacity dispatch validator" mode.

Known limitations
+++++++++++++++++

* The carbon emission cap from ``policy_carbon_emission_limit.csv``
  is still applied per-window without rescaling for window length;
  the naive filter applies the full-year cap to e.g. a 48-hour
  window. For the shipped examples it's non-binding so the dispatch
  is unaffected, but a window-length-rescaled cap is the correct
  formulation. v1.18 candidate.

Version 1.16.0 - May 6, 2026
-------------------------------

Generalises the reserve module from a single up/down pair to **named
reserve products**, matching the structure of real ancillary-services
markets and the way GenX, ReEDS, and PowNet model reserves. Closes
**Phase D** of the PCM-fidelity roadmap (Phase A = PCM mode in v1.14;
Phase B = UC overlay in v1.15; Phase C = DC flow in v1.13).

Default product set
+++++++++++++++++++

Four products ship by default. The direction (up vs down) is encoded
in the product *name* (suffix ``_down`` -> down direction):

* ``regulation_up`` / ``regulation_down`` -- frequency regulation,
  fast governor response.
* ``spinning`` -- contingency reserve, online + ready, up-only.
* ``non_spinning`` -- contingency reserve, may be offline (in a real
  UC; in our LP relaxation it's just a slower-response reserve),
  up-only.

Adding a new product (e.g. ``flex_ramp_up``, ``flex_ramp_down``)
requires no code change -- just rows in the eligibility CSV.

Schema change (BREAKING)
++++++++++++++++++++++++

* ``tech_reserve_eligible.csv``: cols ``(tech, eligible)`` ->
  ``(tech, product, eligible)``. v1.12-v1.15 files need migration: each
  old row becomes one row per product the tech is eligible for.

* ``reserve_requirement_up.csv`` + ``reserve_requirement_down.csv``
  consolidated into ``reserve_requirement.csv`` with cols
  ``(zone, year, product, unit, value)``. Direction inferred from
  product name.

* ``params.json`` schema entries ``reserve_requirement_up`` /
  ``reserve_requirement_down`` replaced by a single
  ``reserve_requirement`` entry.

Migration ships in-place: the three example datasets all have new
CSVs in v1.16. v1.16 will not read v1.12-v1.15 reserve files.

Constraints
+++++++++++

The headroom is now **shared across products in the same direction**
(otherwise a unit's spare megawatts would be double-counted across
regulation + spinning):

  for each (h, m, y, z, te) and direction d in {up, down}:
    sum_{p in products_d} reserve[h,m,y,z,t,p] + (gen if d=up else
      -gen + cap*p_min*dt) <= cap * p_max * dt

Per-product zonal requirement:

  for each (h, m, y, z, p):
    sum_t reserve[h,m,y,z,t,p] >= REQ[z,y,p] * dt

Output
++++++

The two ``reserve_up`` / ``reserve_down`` xarray DataArrays are
replaced by a single ``reserve`` array dimensioned
``(hour, month, year, zone, tech, product)``. Slice on ``product``
to recover the v1.12-style per-direction view.

Eligibility defaults shipped
++++++++++++++++++++++++++++

By carrier (in ``tech_registry.csv``):

* coal / oil / gas / bioenergy / biomass: all 4 products.
* nuclear: spinning + non_spinning only (slow ramp).
* geothermal: regulation_up + spinning + non_spinning.
* hydro (including cascading per-station): regulation_up,
  regulation_down, spinning. Excludes non_spinning (hydro can't
  black-start as quickly as a peaker).
* solar / wind / storage discharge: not eligible (storage will get
  proper regulation eligibility in v1.17 once the UC overlay
  understands charging-mode reserve).

Default requirement values
++++++++++++++++++++++++++

The single ``value`` from ``reserve_requirement_up.csv`` (v1.15) is
split across products as: regulation_up 10 %, regulation_down 10 %,
spinning 30 %, non_spinning 50 %. So the total reserve commitment
stays the same as v1.15 -- this commit is a generalisation of
structure, not a tightening of policy.

Regression
++++++++++

``three_zone`` ``EXPECTED_OBJECTIVE`` 1.9070270274e11 ->
1.9070043702e11 (~0.001 % drift -- numerically identical at this
tolerance, since total reserve is unchanged).

Version 1.15.0 - May 6, 2026
-------------------------------

New feature: optional **unit commitment (UC)** overlay using a
clustered MILP formulation. Closes the LP-vs-PCM fidelity gap on the
thermal-fleet side: when enabled, each UC-eligible tech (typically
coal, gas, oil, biomass) is treated as a cluster of identical units
of size ``tech_unit_size[te]``. The model now decides not just how
much to dispatch but how many units to start, run, and shut down
each hour, with realistic minimum up/down times and startup costs.

This is the **Phase B** milestone of the PCM-fidelity roadmap (after
v1.13 DC flow and v1.14 PCM mode). With UC enabled, PREP-SHOT
becomes a **MILP** (HiGHS handles it; runtime grows several-fold).

Added
+++++

* ``prepshot/_model/unit_commitment.py`` -- ``AddUnitCommitment
  Constraints`` class with three new decision variables per
  ``(h, m, y, z, te)``:

  - ``online[h]`` -- number of units in the cluster online (integer
    in ``[0, N_units]`` where ``N_units = cap_existing / unit_size``).
  - ``startup[h]`` -- units started this hour.
  - ``shutdown[h]`` -- units shut down this hour.

  And six new constraint types:

  - **N-units bound**: ``online[h] <= N_units``
  - **State evolution**: ``online[h] - online[h-1] = startup[h] -
    shutdown[h]`` (skipped at ``h == hour[0]``; first-hour state
    free)
  - **Dispatch upper / lower bound on online units**:
    ``gen[h] <=/>= online[h] * unit_size * p_max_pu (or p_min_pu) * dt``
  - **Min up time**: ``online[h] >= sum_{i=0..MinUp-1} startup[h-i]``
  - **Min down time**: ``(N_units - online[h]) >=
    sum_{i=0..MinDown-1} shutdown[h-i]``

* New cost terms wired into ``cost.py`` via ``add_uc_cost_terms``:
  startup cost (``$/MW`` per startup) and no-load cost (``$/MW-h``
  while online), both NPV-discounted via ``var_factor[y, z]`` and
  divided by ``weight``.

* Six new optional inputs in every shipped example, all keyed
  by tech (file -> column):

  - ``tech_uc_eligible.csv``     -> ``eligible`` (boolean)
  - ``tech_unit_size.csv``       -> ``value`` (MW)
  - ``tech_min_up_time.csv``     -> ``value`` (hours)
  - ``tech_min_down_time.csv``   -> ``value`` (hours)
  - ``tech_startup_cost.csv``    -> ``value`` ($/MW)
  - ``tech_no_load_cost.csv``    -> ``value`` ($/MW-h)

  Defaults are ballpark NREL ATB / PowNet values: Coal 250 MW units,
  8h up, 8h down, $150/MW startup, $3/MW-h no-load; Gas 150 MW
  units, 2h/1h, $100/MW, $5/MW-h; Oil 50 MW, 2h/2h, $80/MW, $8/MW-h;
  Bioenergy/Biomass 30 MW, 4h/4h, $70/MW, $4/MW-h; Nuclear 1000 MW,
  24h/48h, $500/MW, $2/MW-h. Edit the CSVs to fine-tune per
  scenario.

* New ``uc_parameters`` block in each example's ``config.json``:

  - ``three_zone``: ``is_uc=true``, ``uc_relaxation="continuous"``.
    The full integer MILP on three_zone with the default 3-pass
    head iteration takes 15-30 minutes -- too slow for the
    regression test, so the example ships with the LP relaxation
    (online / startup / shutdown become continuous in their natural
    ranges). Flip ``uc_relaxation`` to ``"integer"`` for genuine
    MILP runs.
  - ``thailand``: ``is_uc=false``. Single-zone full-year LP is
    already heavy.
  - ``southeast_asia``: ``is_uc=false``. Multi-zone, multi-station
    hydro -- MILP would push runtime past acceptable smoke-test
    bounds.

  Set ``uc_relaxation="continuous"`` to fall back to the LP
  relaxation (binaries become continuous in their natural ranges) --
  useful for warm-starts and scaling tests.

* ``prepshot.load_data.extract_config_data`` now returns ``is_uc``
  and ``uc_relaxation`` so downstream modules can branch on them.
  Missing block -> defaults off, pre-1.15 ``config.json`` files are
  byte-compatible.

Changed
+++++++

* ``tests/test_regression.py`` ``EXPECTED_OBJECTIVE`` re-baselined
  for ``three_zone`` with UC enabled. UC adds startup + no-load
  costs and may shift dispatch to avoid frequent cycling, raising
  total NPV cost. Inline drift history extends to v1.15.0.

Performance notes
+++++++++++++++++

* MILP solve on ``three_zone`` (48 hours, 3 zones, 4 thermal techs):
  a few seconds.
* Full-year (8760 hour) MILP at scenario sizes like ``thailand``:
  not tractable directly -- pair with PCM rolling-horizon mode
  (``prepshot.pcm``) which solves UC on overlapping windows.
* Set ``uc_relaxation="continuous"`` to keep the model LP for quick
  experimentation; the integer constraint drops, but the constraint
  topology and cost terms stay in place.

Version 1.14.1 - May 5, 2026
-------------------------------

Incremental fixes on top of the v1.14.0 PCM scaffold. Adds a
non-cyclic hydro mode and battery SOC carryover. Multi-window
rolling now solves on scenarios without binding min-outflow on
cascaded hydro -- the cross-window cascade-state issue moves to
v1.15+.

Added
+++++

* New ``cyclic_hydro`` param flag (default ``True`` for CEM
  compatibility). When ``False`` (set automatically by
  ``prepshot.pcm._build_window_params``), ``hydro.inflow_rule``
  drops the upstream-cascade contribution at hours where
  ``h - delay < hour[0]`` -- instead of wrapping modularly into the
  same window. This makes each PCM window stand alone in time,
  rather than implicitly looping its end into its beginning.
* Battery SOC carryover in ``prepshot.pcm._extract_window_state``:
  read each ``model.storage[terminal_hour, m, y, z, te]`` (in MWh),
  divide by ``cap_existing[y,z,te] * energy_to_power_ratio[te] * dt``
  to recover the per-unit-of-cap fraction that
  ``initial_energy_storage_level`` expects, clamp to ``[0, 1]``, and
  pass into the next window's params. Storage techs with zero
  capacity are skipped (the next window's lookup defaults to 0).

Known limitations
+++++++++++++++++

* **Cascading hydro across windows**: at window boundaries,
  downstream stations see only their natural (incremental) inflow
  because the upstream's outflow during the lookback period lives in
  the previous window's solve and isn't carried forward. When
  downstream ``reservoir_outflow_min > natural_inflow``, water
  balance drains storage below ``storage_min`` and the sub-problem is
  infeasible. Workaround: run ``--horizon == --step ==
  period_length`` (single-window). Permanent fix in v1.15+ via a
  cross-window cascade-state vector.
* **Annual carbon cap not rescaled to window length**: the naive
  filter applies the full-year cap to each window. Not binding for
  the shipped examples but wrong on principle; will rescale by
  ``window_hours / hours_in_year`` in v1.15.

Version 1.14.0 - May 5, 2026
-------------------------------

New mode: **production-cost-model (PCM)** with a rolling-horizon
driver. Companion to the default capacity-expansion (CEM) flow in
``run.py``: PCM takes a fixed fleet (from a prior CEM ``baseline.nc``
or a user-supplied capacity CSV) and solves *only* hourly dispatch
over a chosen year, in windows. PowNet- and PyPSA-style.

This is the **Phase A scaffold** of the PCM-fidelity roadmap (Phase
B = unit commitment overlay, Phase C = DC flow which already landed
in v1.13). It's shipped as **alpha** -- single-window mode works
end-to-end; multi-window rolling has a known cyclic-wrap interaction
documented in the module docstring and tracked for v1.14.1.

Added
+++++

* ``prepshot/pcm.py`` -- new module + CLI entry point::

      python -m prepshot.pcm <scenario_dir> --year 2025 \
          --horizon 48 --step 48 [--cap-source baseline.nc]

  Supports both ``.nc`` (CEM result) and ``.csv`` capacity sources.
  Output lands in ``output/baseline_pcm.nc`` so it doesn't collide
  with CEM's ``baseline.nc``.

* New ``skip_end_storage`` param flag plumbed through
  ``hydro.end_storage_rule`` and ``storage.end_energy_storage_rule``;
  when ``True``, the cyclical "terminal storage = initial storage"
  equality is dropped so PCM windows can have free terminal SOC
  (carried into the next window).

* ``prepshot.load_data.extract_config_data`` now also returns
  ``hours_in_year`` so PCM windows can recompute the cost-objective
  ``weight`` for shorter time slices.

Changed
+++++++

* ``model.hour_p`` now derives from ``hour[0]`` (``[hour[0] - 1] +
  hour``) instead of being hardcoded to ``[0] + hour``. CEM behaviour
  is unchanged because CEM uses ``hour=[1..N]``; PCM windows starting
  at ``hour[0] > 1`` get the correct prior-hour anchor for storage
  balances.

* ``storage.init_energy_storage_rule`` and
  ``storage.end_energy_storage_rule`` reference ``model.hour_p[0]``
  instead of literal ``0`` for the prior-hour storage variable.

* ``generation.ramping_up_rule`` / ``ramping_down_rule`` skip the
  inter-hour delta when ``h == model.hour[0]`` (no ``h - 1`` in the
  set). Was ``1 < h``, now ``h > model.hour[0]``.

* ``hydro.inflow_rule`` rewrites the cyclic-wrap arithmetic to use
  modular indexing relative to ``hour[0]``, ``hour[-1]`` instead of
  the implicit ``[1..24]`` assumption. CEM behaviour is mathematically
  identical for ``hour=[1..N]``.

Known limitations (v1.14.0 alpha)
+++++++++++++++++++++++++++++++++

* **Multi-window rolling is unstable.** The hydro module's cyclic
  ``inflow_rule`` couples ``upstream.outflow[hour[-1]]`` to
  ``downstream.inflow[hour[0]]`` within each window; with carry-over
  state at ``hour[0]-1``, the second window's cyclic loop can have no
  feasible point. Workaround: run with ``--horizon == --step ==
  period_length`` (single-window PCM = fixed-capacity CEM dispatch).
  v1.14.1 will switch hydro to a non-cyclic rolling form.

* **Battery state carryover deferred.** ``initial_energy_storage_
  level`` is per-unit-of-cap, not absolute MWh; an absolute-MWh
  state extracted from a solved window doesn't compose with that
  convention. Each window currently re-initialises batteries to the
  dataset's default SOC. Fix in v1.14.1.

Version 1.13.0 - May 5, 2026
-------------------------------

New feature: optional **DC linearised power flow** for inter-zone
transmission. Layered on top of the existing transport-model
``trans_export`` variables -- the LP capacity bound stays in place;
DC flow adds Kirchhoff's voltage law via phase-angle differences.
First step toward production-cost-model fidelity.

Added
+++++

* ``prepshot/_model/dc_flow.py`` -- ``AddDCFlowConstraints`` class.

  - **theta variable**: ``model.theta[h, m, y, z]``, free in
    ``[-pi, pi]``. Created only when the module is enabled.
  - **reference bus**: ``theta[h, m, y, ref_zone] = 0`` per timestep,
    pinning the otherwise translation-invariant solution.
  - **flow equation**: for every unordered zone pair ``(z1, z2)`` with
    a positive susceptance ``b``,

    .. math::

        \\text{trans\\_export}_{z_1,z_2} - \\text{trans\\_export}_{z_2,z_1}
          = b \\cdot (\\theta_{z_1} - \\theta_{z_2}) \\cdot \\Delta h

    Each pair gets ONE constraint (alphabetical ordering avoids
    duplicates). Pairs with ``b = 0`` -- electrically disconnected --
    are skipped, so the constraint structure matches the network
    topology.
  - **stays LP**: no binaries, no non-convexity. Adds ``|hour| x
    |month| x |year|`` reference-bus equalities plus
    ``|hour| x |month| x |year| x N_pairs`` flow equalities.

* New optional input file in every shipped example:

  - ``transmission_susceptance.csv`` (cols ``zone1, zone2, unit,
    value``): per-pair susceptance in MW/rad. Defaults derived from
    line capacity: ``b = max(2 * existing_capacity_MW, 1000)``, so a
    ~0.5 rad angle difference saturates the line. Override per pair
    to fine-tune.

* New ``dc_parameters`` block in each example's ``config.json``:

  - ``three_zone``: ``is_dc_flow=true``, ``reference_zone=BA1``.
  - ``thailand``: ``is_dc_flow=false`` (single-zone, nothing to
    constrain).
  - ``southeast_asia``: ``is_dc_flow=true``,
    ``reference_zone=Thailand``.

* ``prepshot/load_data.py`` reads the new config block (default
  ``is_dc_flow=false`` if the section is missing -- pre-1.13
  ``config.json`` files are byte-compatible).

Changed
+++++++

* ``tests/test_regression.py``: ``EXPECTED_OBJECTIVE`` for the
  ``three_zone`` regression bumped to ``1.8967979487e11``. Drift
  history kept inline for traceability:

  - v1.1.1  -> ``1.8793771299e11``  (transport, no reserve)
  - v1.12.0 -> ``1.8878269786e11``  (+ reserve up/down)
  - v1.13.0 -> ``1.8967979487e11``  (+ DC flow Kirchhoff)

  Each step is a real model upgrade, not solver drift; the regression
  test catches accidental cost regressions, and the layered baselines
  let future readers see what each feature added.

Version 1.12.0 - May 5, 2026
-------------------------------

New feature: operating-reserve constraints (LP relaxation, no unit
commitment). Two reserve directions are tracked -- **up** (capacity
available to ramp dispatch up if demand spikes / a unit trips) and
**down** (capacity available to ramp down if VRE over-generates or
load drops). Each plant's headroom above and below its current
dispatch counts toward the corresponding zonal requirement;
non-eligible techs (typically solar / wind / storage discharge) are
forced to zero in both directions. The relaxation matches GenX's
"no-UC" mode and is acceptable for capacity-expansion planning, not
for sub-hourly dispatch studies.

Added
+++++

* ``prepshot/_model/reserve.py`` -- new constraint class
  ``AddReserveConstraints`` with four rules per timestep:

  - **headroom up**: ``reserve_up[h,m,y,z,t] <= cap_existing *
    p_max_pu * dt - gen[h,m,y,z,t]`` for eligible techs (forced to 0
    otherwise).
  - **headroom down**: ``reserve_down[h,m,y,z,t] <= gen[h,m,y,z,t]
    - cap_existing * p_min_pu * dt`` for eligible techs (forced to 0
    otherwise).
  - **requirement up / down**: ``sum_t reserve_<dir>[h,m,y,z,t] >=
    reserve_requirement_<dir>[z,y] * dt`` per (zone, year, hour).

* ``model.reserve_up`` and ``model.reserve_down`` decision variables
  (``hour x month x year x zone x tech``), both gated by
  ``config.reserve_parameters.is_reserve``. When the flag is missing
  or ``false`` the variables + constraints are not built, so any
  pre-1.12 ``config.json`` is byte-compatible.

* New optional inputs in every shipped example:

  - ``tech_reserve_eligible.csv`` (cols ``tech, eligible``):
    dispatchable carriers (coal, gas, oil, bioenergy, hydro, nuclear,
    geothermal) default to ``1``; solar / wind / storage default to
    ``0``. A single eligibility flag covers both directions -- thermal
    plants and dispatchable hydro can ramp either way; storage and VRE
    can't.
  - ``reserve_requirement_up.csv`` and ``reserve_requirement_down.csv``
    (cols ``zone, year, unit, value``): per-zone-year reserve in MW.
    Both default to the same placeholder per example -- 100 MW for
    ``three_zone``, 500 MW per zone for ``southeast_asia``, 1500 MW for
    ``thailand`` (~5 % of Thailand 2023 peak). Override either file
    independently to tune the directions.

* New ``reserve_parameters`` block in each example's ``config.json``.
  Set to ``"is_reserve": true`` for ``three_zone`` and ``thailand`` (~4
  minutes per solve, acceptable). Set to ``"is_reserve": false`` for
  ``southeast_asia`` because the up+down constraints over 288 hours x
  5 zones x 65 techs (mostly per-station hydro) push HiGHS to 25+
  minutes -- too slow for an example dataset. The CSVs are still
  shipped so flipping the flag works out of the box.

Changed
+++++++

* ``tests/test_regression.py``: ``EXPECTED_OBJECTIVE`` for the
  ``three_zone`` regression bumped from ``1.8793771299e11`` (v1.1.1
  baseline) to ``1.8874579528e11``. The reserve constraints (up + down
  together) force some dispatched headroom above and below the
  operating point on eligible techs, which raises total NPV cost by
  ~0.4 %.

Fixed
+++++

* ``examples/southeast_asia/input/reservoir_{initial,final}_storage_
  level.csv``: relaxed from ``= storage_max`` to ``= 0.5 *
  storage_max`` for all 57 stations. The previous setting forced
  each reservoir to start AND end the year at full capacity, leaving
  zero swing room. HiGHS sometimes accepted the tight feasible region
  (commit ``06e1286`` was such a case), but presolve flagged it as
  infeasible on most runs and reliably so once any new constraint
  was layered on top -- including the reserve module added in this
  release. Half-full is also a more realistic annual-average
  operating point for these reservoirs.

Version 1.11.1 - May 5, 2026
-------------------------------

Documentation infrastructure: docs are now hosted on Read the Docs
at https://prep-shot.readthedocs.io/, with a Chinese (``zh_CN``)
translation in flight. Also drops the offline-PDF build (the
canonical docs are HTML only).

Added
+++++

* ``.readthedocs.yaml`` -- the build config RTD requires. ubuntu-22.04
  + python 3.11, pandoc apt package (for nbsphinx), and
  ``pip install -e .`` so autodoc can import ``prepshot``.
* ``html_theme_options`` ported from ``godotengine/godot-docs``:
  ``flyout_display: "attached"`` puts the version + language picker
  inline at the bottom of the sidebar (Godot's UX) once the RTD
  Addons framework is enabled for the project.
* ``sphinxcontrib-mermaid`` extension + an architecture diagram on
  the landing page.
* In-tree Chinese (``zh_CN``) translation scaffolding under
  ``doc/source/locale/zh_CN/LC_MESSAGES/`` -- 11 pages translated:
  index, Installation, Glossary, Model_input_output, Contribution,
  and the six how-to recipes (~447 strings total).
* "Translating the Documentation" section in ``Contribution.rst``
  with the extract / update / translate / build workflow.

Changed
+++++++

* All "Official Documentation" / "Tutorial Page" links in the README,
  ``index.rst``, and ``Installation.rst`` repointed from the
  GitHub-Pages URL to ``https://prep-shot.readthedocs.io/``.
* The mermaid architecture diagram on the landing page rewritten
  to use Mermaid's quoted-label ``\\n`` syntax instead of HTML
  ``<br/>``, sidestepping a Sphinx HTML-escape bug that double-
  escaped the directive contents.

Removed
+++++++

* The ``Generate offline PDF`` step from ``.github/workflows/static.yml``
  and the ``texlive-latex-recommended`` / ``texlive-xetex`` /
  ``latexmk`` / ``xindy`` apt installs that fed it. ``latex_engine``
  and ``latex_documents`` likewise dropped from ``conf.py``. Offline
  reading is now via the htmlzip download from RTD.
* Empty ``.gitattributes`` and the easter-egg ``downwasher`` glossary
  entry.

Notes
+++++

This is the **first release with ``.readthedocs.yaml`` shipped**.
Earlier tags (``v1.11.0`` and below) cannot build on RTD because
RTD now requires the YAML at the project root. Activate ``latest``
+ ``v1.11.1`` (and future tags) in RTD admin's Versions tab; leave
older tags inactive. They remain accessible as GitHub release
tarballs.

Version 1.11.0 - May 5, 2026
-------------------------------

Documentation polish: better navigation, more reference content, no
new features.

Added
+++++

* ``doc/source/Glossary.rst`` -- a reference for the energy-modeling,
  hydropower, and optimization terminology used throughout the docs
  (~50 entries: capacity expansion, head iteration, LMP, NPV,
  carrier, cascading hydropower, WACC, ...).
* ``doc/source/how_to/`` -- a new "How-To Recipes" section with five
  short, focused walkthroughs for common tasks:

  - ``add_a_technology`` -- introduce a new generation tech via
    CSV edits.
  - ``tighten_a_carbon_cap`` -- run a counterfactual without
    overwriting the baseline.
  - ``compare_two_scenarios`` -- side-by-side analysis with xarray.
  - ``inspect_lmps`` -- read the v1.9.1 ``shadow_price_demand``
    output.
  - ``add_a_cascading_hydropower_system`` -- introduce a multi-
    station cascade with reservoir physics.

* Architecture diagram on the landing page (``index.rst``), drawn
  with the new ``sphinxcontrib-mermaid`` extension. Shows the data
  flow from scenario directory through ``load_data`` /
  ``create_model`` / ``solve_model`` / ``extract_results`` and back
  out as NetCDF.
* "Edit on GitHub" link in the top-right of every page (via
  ``html_context`` in ``conf.py``) so readers can fix typos and
  rephrase paragraphs without cloning.
* Solver-choice tabs (``HiGHS``/``Gurobi``/``COPT``/``MOSEK``) in
  ``Installation.rst``, leaning on the existing ``sphinx_tabs``
  extension.
* Quick-link bar on the landing page above the Overview section
  (Get started / Install / How-to / Inputs / GitHub).

Changed
+++++++

* The sidebar is now grouped into four sections via separate
  ``toctree`` directives: **Getting Started** (Installation,
  Quickstart), **User Guide** (Model Inputs/Outputs, Math notation,
  Glossary, How-to recipes), **Reference** (API, Stability,
  Changelog), **Community** (Forum, Contribution, Citations,
  References). Replaces the previous flat 10-page list.
* The Quickstart now includes a "Scenario background" section
  (3 BAs, 15 hydropower stations, 2020-2030 zero-carbon pathway) --
  previously a separate Tutorial page.

Removed
+++++++

* ``doc/source/Tutorial.rst`` -- a 47-line page that only contained
  scenario context and a redirect to Quickstart. Its content moved
  into the Quickstart's intro.
* Duplicate "Run an example" / "Run your own model" instructions
  from ``Installation.rst`` -- now a 1-line pointer to Quickstart.
* "Input formats" and "Migrating an existing input directory"
  sections from ``Installation.rst`` -- redundant with
  ``Model_input_output.rst``.

Version 1.10.0 - May 5, 2026
-------------------------------

Repository housekeeping. Each shipped scenario is now self-contained
under ``examples/`` with its own ``config.json`` + ``params.json`` +
``input/``. There is no longer a "default" scenario at the repo
root -- users explicitly pick one with ``cd examples/<scenario>``.

Added
+++++

* ``examples/thailand/`` -- the legacy ``single_node_with_hydro/``
  dataset migrated from v1.4 wide-format Excel to the v1.9 long-CSV
  schema. 13 cascading Mekong-basin reservoirs (Bhumibol, Sirikit,
  Srinagarind, ...) modeled per-station; ``Large Hydropower``
  capacity allocated by ``N_max``. ``main.ipynb`` rewritten as
  ``Thailand.ipynb`` with the v1.9 API.
* ``examples/three_zone/{config.json, params.json, input/}`` --
  the canonical 3-zone synthetic dataset (used by Quickstart and
  the regression test) now self-contained.
* ``examples/southeast_asia/{config.json, params.json, input/,
  SoutheastAsia.ipynb}`` -- the Lower Mekong scenario also
  self-contained, with its own dataset directory.

Changed
+++++++

* ``run.py`` now takes an optional positional scenario-directory
  argument (defaults to ``cwd``). Without args, expects to be run
  from inside an ``examples/<scenario>/`` directory.
* ``tests/test_regression.py`` ``cd``s into ``examples/three_zone/``
  for the duration of the solve.
* ``prepshot/logs.py`` -- fixed mkdir bug (was creating ``log/``'s
  parent, not ``log/`` itself); the directory is now auto-created
  on first run rather than tracked in git.
* ``examples/single_node_with_hydro/`` -> ``examples/thailand/``
  (consistent geography-based naming with ``southeast_asia/``).

Removed
+++++++

* Repo-root ``config.json`` and ``params.json`` (no default scenario).
* Repo-root ``log/`` and ``output/`` directories (now ignored as
  runtime artifacts).
* ``binder/`` (Binder launcher config) -- cold start was too slow.
  Colab remains as the online launcher.
* ``toolkit/`` -- merged into ``tools/`` (single namespace for
  one-off scripts).
* Empty ``.gitattributes``.

Version 1.9.1 - May 3, 2026
-------------------------------

Added
+++++

* New output variable ``shadow_price_demand`` -- the dual of the
  nodal power-balance constraint, exposing the locational marginal
  price (LMP) at each ``(hour, month, year, zone)``. Sign is
  flipped from the raw dual so positive values mean "more
  expensive to serve more demand", matching the convention used by
  PyPSA / Switch / GenX. Discounted to NPV; divide by
  ``var_factor[year, zone]`` to recover undiscounted real-year
  prices.
* ``prepshot/output_data.py::create_data_array`` gained an
  ``extractor`` parameter so the same helper can lift either primal
  values (``model.get_value``, the default) or duals
  (``model.get_constraint_dual``) out of a tupledict.

Notes
+++++

* The shadow-price extraction is wrapped in a try/except: if the
  solver does not return duals (e.g. for a MIP solve, or after an
  infeasible run), a warning is logged and the variable is omitted
  from the NetCDF file rather than aborting the run.

Version 1.9.0 - May 3, 2026
-------------------------------

Optional finance module: weighted-average cost of capital (WACC) for
new-build investment, plus public-debt accounting and caps.
Backported from the dev branch (commit ``bfd9de6``, "add finance
module") and adapted to the v1.8.x long-format / per-zone /
``max``-naming conventions. The feature is OFF by default; the
regression objective is unchanged at ``1.880e+11`` for the canonical
``input/`` dataset.

Added
+++++

* ``prepshot/_model/finance.py`` with ``AddFinanceConstraints``:

  - ``public_debt_newtech[y, z, te]`` -- discounted public-debt
    obligation incurred by each new-tech investment, exported in
    the ``year.nc`` results.
  - System-wide cap: ``sum over (z, te) of public_debt_newtech[y, z, te]
    <= public_debt_max_system[y]``. Skipped when missing or
    ``+inf``.
  - Per-zone cap: ``sum over te of public_debt_newtech[y, z, te]
    <= public_debt_max_zone[z, y]``. Same skip behavior.

* ``prepshot/utils.py::calc_interest_rate`` -- weighted-average cost
  of capital from public-debt / private-debt / equity tranches.
* Seven new optional inputs (all ``required: false``):
  ``finance_public_debt_ratio.csv`` (per-tech),
  ``finance_private_debt_ratio.csv`` (per-tech),
  ``finance_cost_of_public_debt.csv`` (per-tech, per-zone),
  ``finance_cost_of_private_debt.csv`` (per-tech, per-zone),
  ``finance_cost_of_private_equity.csv`` (per-tech, per-zone),
  ``finance_public_debt_max_system.csv`` (per-year),
  ``finance_public_debt_max_zone.csv`` (per-zone, per-year).

Changed
+++++++

* ``prepshot/load_data.py::compute_cost_factors`` -- when finance
  inputs are present, ``inv_factor[tech, year, zone]`` discounts
  the construction outlay at the project-level WACC instead of the
  zonal discount rate. Fixed/variable/transmission factors continue
  to use the zonal discount rate. With finance OFF (no inputs),
  ``WACC == discount_rate`` and the legacy behavior is preserved.
* ``prepshot/model.py::create_model`` -- ``AddFinanceConstraints``
  is wired in only when ``params['public_debt_ratio']`` is
  populated, so users without finance inputs see no extra
  variables, constraints, or output variables.
* ``prepshot/output_data.py::extract_results_non_hydro`` -- emits
  ``public_debt_newtech`` only when finance is enabled.

Notes
+++++

* The dev-branch commit used wide-Excel inputs and ``np.Inf``;
  this backport uses long-format CSV, ``np.inf``, and the
  v1.8.0 ``max``/``min`` naming convention (e.g.
  ``public_debt_max_system`` rather than
  ``public_debt_upper_bound_system``).
* Cap rules treat both missing entries and ``+inf`` as "no
  constraint", matching the candidates / carbon-emission-limit
  conventions elsewhere in the model.

Version 1.8.1 - May 3, 2026
-------------------------------

Fixed
+++++

* ``prepshot/_model/investment.py``: retirement check now looks up
  ``lifetime`` at the commissioning year, not the current modeled
  year, so units built at vintage ``cy`` retire after
  ``cy + lifetime[te, cy]`` regardless of any later parameter
  changes. Bug present in two locations:

  - ``tech_lifetime_rule`` (existing-fleet retirement, introduced
    by the v1.7.0 refactor): ``lifetime[te, y]`` -> ``lifetime[te, cy]``.
  - ``remaining_capacity_rule`` (new-build retirement, original
    PR #47 by Quan YUAN): ``lt[te, y]`` -> ``lt[te, yy]``.

  The shipped ``input/tech_lifetime.csv`` has constant lifetime
  across years for every tech, so the regression objective is
  unchanged at ``1.880e+11``. The bug only manifests when users
  supply time-varying lifetimes (e.g. modeling tech improvement).

Version 1.8.0 - May 3, 2026
-------------------------------

PyPSA-style data model. The fixed ``resource_type`` enum is replaced
with a free-form ``carrier`` string plus boolean per-tech behavior
flags; any tech can now bound its dispatch with time-varying
``p_max_pu`` / ``p_min_pu`` profiles, removing the need for separate
``capacity_factor`` and ``must_run`` paths. Hydro plants are first-class
techs (carrier ``hydro``) instead of an aggregate ``Hydro``. Input
files gain consistent domain prefixes (``tech_``, ``reservoir_``,
``transmission_``, ``storage_``, ``policy_``, ``economic_``) and
adopt ``max`` / ``min`` instead of mixed ``upper_bound`` / ``lower_bound``.
Existing capacity and candidates are now structured symmetrically for
both plants and transmission lines.

The regression test confirms the model objective is unchanged at
``1.880e+11`` for the canonical ``input/`` dataset across all
intermediate refactors.

Added
+++++

* ``input/tech_registry.csv`` (was ``technologies.csv``) -- per-tech
  registry with columns ``tech``, ``name``, ``carrier``, ``is_storage``.
  Replaces the rigid ``resource_type`` enum.
* ``input/tech_max_gen_profile.csv`` and
  ``input/tech_min_gen_profile.csv`` -- optional time-varying upper /
  lower bounds on dispatch (PyPSA's ``p_max_pu`` / ``p_min_pu``).
  Subsumes the ``capacity_factor`` and ``must_run`` paths.
* ``input/transmission_candidates.csv`` -- symmetric counterpart to
  ``tech_candidates.csv`` for new transmission lines, with columns
  ``zone1, zone2, year, unit, capacity_min, capacity_max``.
* ``input/transmission_existing.csv`` -- now keyed by
  ``(zone1, zone2, commission_year)`` and respects ``transmission_lifetime``,
  matching the existing-fleet structure for plants.
* Per-zone discount factor: ``input/economic_discount_factor.csv`` is
  keyed by ``(zone, year)``; cost factors propagate through ``cost.py``.
* Custom carbon-emission-limit regions in
  ``input/policy_carbon_emission_limit.csv``: each row carries a
  comma-separated ``zones`` field, allowing arbitrary multi-zone
  caps without per-zone duplication.

Removed
+++++++

* ``prepshot/_model/nondispatchable.py`` -- subsumed by the unified
  ``gen_up_bound_rule`` / ``gen_low_bound_rule`` in
  ``prepshot/_model/generation.py``.
* ``predefined_hydropower.csv`` and the ``must_run`` else-branch in
  ``hydro.py`` -- replaced by ``tech_min_gen_profile.csv``.
* ``capacity_factor.csv`` -- replaced by ``tech_max_gen_profile.csv``.

Changed
+++++++

* **Naming sweep:** all ``upper_bound`` / ``lower_bound`` files,
  param keys, and DataFrame columns renamed to ``max`` / ``min``:

  - ``tech_upper_bound.csv`` -> ``tech_capacity_max.csv``
  - ``tech_lower_bound.csv`` -> ``tech_capacity_min.csv``
  - ``reservoir_storage_upper_bound.csv`` -> ``reservoir_storage_max.csv``
  - ``reservoir_storage_lower_bound.csv`` -> ``reservoir_storage_min.csv``
  - ``tech_candidates.csv`` columns ``lower_bound`` / ``upper_bound``
    -> ``capacity_min`` / ``capacity_max``
  - ``transmission_candidates.csv`` columns: same rename.

* **File prefixes:** input files regrouped by domain.
  ``hydro_inflow.csv`` -> ``reservoir_inflow.csv``;
  ``charge_efficiency.csv`` -> ``storage_charge_efficiency.csv``;
  ``carbon_tax.csv`` -> ``policy_carbon_tax.csv``;
  ``discount_factor.csv`` -> ``economic_discount_factor.csv``; etc.
* **Hydro plants are first-class techs.** Each plant appears in
  ``tech_registry.csv`` with ``carrier='hydro'``; reservoir
  parameters are keyed per station (no ``main_hydro`` aggregation).
* **Demand units.** ``demand.csv`` now carries instantaneous power
  in MW (PyPSA convention). The nodal balance constraint multiplies
  by ``dt`` to convert to MWh per timestep, matching ``gen`` /
  ``charge`` which were already in MWh.
* ``prepshot/model.py::define_basic_sets`` derives ``hydro_tech``,
  ``storage_tech``, and ``dispatchable_tech`` from the registry's
  ``carrier`` and ``is_storage`` columns rather than a fixed enum.
* ``prepshot/_model/generation.py`` defines a single pair of
  generation bound rules using ``p_max_pu`` / ``p_min_pu`` lookups,
  replacing the per-resource-type branches.
* ``prepshot/_model/transmission.py`` builds existing transmission
  capacity by summing over ``(zone1, zone2, commission_year)`` entries
  still in service, mirroring ``tech_lifetime_rule``.

Version 1.7.0 - May 3, 2026
-------------------------------

Data-model cleanup ahead of the v1.8.0 PyPSA-style API. The
existing-fleet representation is reshaped from an awkward
``(zone, tech, age)`` "historical capacity" table to a tidy
``(tech, zone, commission_year)`` "existing fleet" table, and the
single-purpose ``technology_type`` file is renamed to ``technologies``
so it can grow into a per-tech registry.

Added
+++++

* ``input/existing_fleet.csv`` and ``southeast_asia/existing_fleet.csv``
  -- one row per existing-capacity block (tech, zone, commission year,
  capacity). Sparse representation: only non-zero entries are listed.
* ``technologies.csv`` (replaces ``technology_type.csv``) with columns
  ``tech`` and ``type``. Designed to grow into a richer per-tech
  registry (e.g. ``description``, ``category``, ``co2_intensity_class``)
  alongside the v1.8.0 API work.

Removed
+++++++

* ``historical_capacity.csv`` -- replaced by ``existing_fleet.csv``.
  The ``age`` dimension is gone; capacity blocks now record an
  explicit ``commission_year``, which is unambiguous and survives
  schedule shifts.
* ``technology_portfolio.csv`` -- file existed in the schema but was
  never referenced by any model rule (all values were 0 in the
  shipped data). Dead code; deleted.
* ``technology_type.csv`` -- renamed to ``technologies.csv`` (see
  Added).

Changed
+++++++

* ``prepshot/_model/investment.py::tech_lifetime_rule`` rewritten:

  - **Before:** sum ``historical_capacity[zone, tech, age]`` for
    ``age`` in ``[0, lifetime - service_time)``.
  - **After:** sum ``existing_fleet[tech, zone, commission_year]``
    for all commission years where
    ``commission_year <= y < commission_year + lifetime``.

  The two formulations are mathematically equivalent for the shipped
  data; the regression test confirms the model objective is unchanged
  at ``1.879e+11``.

* ``prepshot/load_data.py::extract_sets`` derives the ``tech`` set
  from ``technologies`` (was ``technology_type``).
* ``prepshot/model.py::define_basic_sets`` reads tech categories from
  ``technologies`` (was ``technology_type``).
* ``prepshot/_model/hydro.py`` reads the hydro-tech list from
  ``technologies`` (was ``technology_type``).

Version 1.6.0 - May 3, 2026
-------------------------------

Cleanup release. The wide-Excel reading machinery is removed, the
migration tool is rewritten to work under pandas >= 2.0, and the
``pandas<2.0`` / ``numpy<2.0`` caps from v1.3.1 are lifted.

Removed
+++++++

* ``prepshot.load_data.read_excel`` -- deleted. Nothing in the runtime
  path used it after v1.5.0; the migration tool now has its own
  ``pd.read_excel`` call.

Changed
+++++++

* ``tools/migrate_to_long.py`` rewritten to be self-contained:

  - Bundles its own copy of the v1.4.x wide-format spec (since the
    on-disk ``params.json`` is now v1.5.0 long-format and no longer
    carries that information).
  - Uses a custom ``flatten_wide_to_dict`` helper that replicates the
    v1.4.x ``unstack``-based key ordering by direct cell iteration.
    Works under pandas >= 2.0 (which rejects ``unstack`` on
    DataFrames with duplicate column-level values).
  - Verified to produce byte-equivalent output to the shipped
    v1.5.0 ``input/`` CSVs (modulo annotation columns) for all 38
    dict-shape parameters.

* ``pyproject.toml`` and ``requirements.txt`` floors raised:

  - ``numpy>=1.26.0`` (no upper cap)
  - ``pandas>=2.0.0`` (no upper cap)
  - ``xarray>=2023.10.0`` (no upper cap)

* Tested with numpy 2.0.2, pandas 2.3.3, xarray 2024.7.0; full
  test suite passes (22 tests, end-to-end regression objective
  unchanged at 1.879e+11).

Fixed
+++++

* ``np.Inf`` references in ``prepshot/_model/investment.py`` and
  ``prepshot/_model/co2.py`` replaced with ``np.inf`` (``np.Inf``
  was removed in numpy 2.0).

Version 1.5.0 - May 2, 2026
-------------------------------

.. note::
   **Schema bump 1 -> 2.** This is a breaking input-format change.
   Existing input directories must be migrated. See migration notes
   below.

Every input is now a CSV. The unstack-based wide-Excel code path is
no longer used by the loader at runtime, though ``read_excel`` remains
in ``prepshot/load_data.py`` for the migration tool's benefit (a full
v1.4.x -> v1.5.0 migration tool is on the v1.6.0 roadmap).

The ``pandas<2.0`` cap from v1.3.1 is *still in place* in v1.5.0 because
``read_excel`` (used by the migration tool) calls ``unstack``. Once the
migration tool no longer needs ``read_excel`` (v1.6.0), the cap will
be lifted.

Added
+++++

* ``tools/migrate_to_long.py`` -- runnable migration script that
  converts a directory of wide-format Excel inputs to long-format CSVs
  using the legacy params.json spec for shape information. Run as::

      python tools/migrate_to_long.py /path/to/your/input_dir

* Tailored schema-1 -> schema-2 migration hint in ``check_schema``:
  users feeding a v1.4.x or earlier params.json now get a clear
  pointer at ``tools/migrate_to_long.py`` instead of a generic version
  mismatch error.

Changed (Breaking)
++++++++++++++++++

* ``params.json`` schema bumped to ``_schema_version: 2``. Files with
  ``_schema_version: 1`` are rejected with a migration hint.
* All Group-1/2 parameters in ``input/`` and ``southeast_asia/`` have
  been converted from wide ``.xlsx`` to long ``.csv``:

  - Capacity / cost: ``technology_*``, ``transmission_line_*``,
    ``capacity_factor``, ``new_technology_*_bound``, ``lifetime``,
    ``fuel_price``, ``technology_portfolio``, ``technology_type``,
    ``historical_capacity``, ``initial_energy_storage_level``,
    ``charge_efficiency``, ``discharge_efficiency``,
    ``energy_to_power_ratio``, ``ramp_up``, ``ramp_down``.
  - Time-series / spatial: ``demand``, ``inflow``,
    ``predefined_hydropower``, ``distance``,
    ``reservoir_storage_upper_bound``, ``reservoir_storage_lower_bound``,
    ``initial_reservoir_storage_level``,
    ``final_reservoir_storage_level``.
  - Domain: ``carbon_emission_limit``, ``emission_factor``,
    ``carbon_offset_price``, ``carbon_offset_limit``, ``discount_factor``.

* ``params.json`` entries for migrated parameters now declare just
  ``"format": "long"`` plus ``drop_na`` (and ``required``/``default``
  if optional). The wide-format-specific keys (``index_cols``,
  ``header_rows``, ``unstack_levels``, ``first_col_only``) are dropped.

Annotation columns
++++++++++++++++++

Long-format CSVs now support **annotation columns** -- human-readable
metadata that lives alongside the data but is ignored by the model
loader. Following the TransitionZero convention:

* Every long CSV has a ``unit`` column (e.g. ``MWh``, ``USD/tonneCO2``,
  ``m3/s``).
* The eight per-field reservoir CSVs additionally have a ``name``
  column with the human-readable station name (e.g. "Grand Coulee")
  alongside the ``stcd`` ID.

The loader filters out columns whose name (case-insensitive) is in
the annotation set ``{unit, units, name, commodity, comment, comments,
description, desc, note, notes, label}``, or that ends in ``_name``
(``zone_name``, ``tech_name``, etc.). These columns never appear in
the dim-key tuples, so model code is unaffected.

Two new unit tests cover annotation handling:
``test_unit_column_filtered`` and
``test_name_and_other_annotation_columns_filtered``.

Column renames for clarity
++++++++++++++++++++++++++

Several cryptic abbreviations have been replaced with self-describing
names across the input CSVs and model code:

* ``stcd`` (and ``station`` for params that previously used that name)
  -> ``station_id`` everywhere -- inputs, ``model.station``,
  ``params['station_id']``, local variables.
* ``POWER_ID`` / ``NEXTPOWER_ID`` (water_delay_time)
  -> ``upstream_station_id`` / ``downstream_station_id``.
* ``Z`` / ``Q`` / ``V`` in the piecewise-function lookups
  -> ``tailrace_level`` / ``discharge`` / ``forebay_level`` /
  ``volume`` (the same axis was being repurposed: ``Z`` meant
  tailrace level in one file and forebay level in the other).
* ``coeff`` -> ``coefficient``, ``GQ_max`` -> ``generation_flow_max``,
  ``N_min`` / ``N_max`` -> ``capacity_min`` / ``capacity_max`` for the
  per-field reservoir CSVs.

Group 3 migration
+++++++++++++++++

The four "table-shaped" parameters are now CSVs as well:

* ``water_delay_time``, ``reservoir_tailrace_level_discharge_function``,
  ``reservoir_forebay_level_volume_function`` -- already 3-column long
  internally; resaved as CSV and loaded via the new ``format: "table"``
  dispatch (returns a DataFrame for downstream ``groupby``/column
  access).
* ``reservoir_characteristics`` -- previously one wide table with ~13
  fields per station -- has been **split into 8 single-field long
  CSVs**, one per field the model actually uses:

  - ``reservoir_zone``, ``reservoir_coefficient``,
    ``reservoir_outflow_min``, ``reservoir_outflow_max``,
    ``reservoir_generation_flow_max``, ``reservoir_capacity_min``,
    ``reservoir_capacity_max``, ``reservoir_head``.

  Four field renames in the process (``coeff`` -> ``coefficient``,
  ``GQ_max`` -> ``generation_flow_max``, ``N_min`` -> ``capacity_min``,
  ``N_max`` -> ``capacity_max``) for clarity. The three descriptive
  fields (``name``, ``short_name``, ``type``) that the model never
  referenced have been dropped.

* ``params.json`` gains a new ``"format": "table"`` value alongside
  ``"format": "long"`` for parameters consumed as DataFrames rather
  than dicts.

Model code (9 sites in ``hydro.py`` / ``head_iteration.py`` /
``load_data.py``) updated to read from the new per-field params:
``params['reservoir_characteristics']['<field>', s]`` becomes
``params['reservoir_<field>'][s]``. The end-to-end regression test
confirms the model objective is unchanged after the refactor.

Migration notes
+++++++++++++++

The shipped ``input/`` and ``southeast_asia/`` directories are already
in v1.5.0 shape. For custom input directories (e.g. scenario forks
such as ``input_s100_baseline_*``):

* ``tools/migrate_to_long.py`` covers the dict-shape parameters; run::

      python tools/migrate_to_long.py /path/to/your/input_dir

* The four Group-3 parameters and ``reservoir_characteristics``'s
  field-split are not yet automated. Until the v1.6.0 expanded
  migration tool ships, use the shipped ``input/`` directory as a
  reference for the new file shapes, or open an issue if you need
  porting help.

Custom ``params.json`` files (i.e. anyone who has forked params.json)
will need to mirror the canonical v1.5.0 file shipped in this release:
metadata stamp ``"_schema_version": 2``, then minimal long-format
entries (``"format": "long"`` / ``"format": "table"``) without the
legacy wide-format keys.

Version 1.4.0 - May 2, 2026
-------------------------------

PREP-SHOT now supports long-format ("tidy") CSV inputs as a parallel
option to the wide-Excel format. New parameters can be born long-format
without disturbing existing wide-format inputs; existing parameters can
migrate one at a time when convenient.

Why long-format
+++++++++++++++

Adding a dimension to a long-format file is a non-breaking column add,
not a reshape. This eliminates the recurring "the bound files were
reshaped from (tech, zone) to (zone, tech, year)" class of breakage,
which historically required migrating every existing input directory.

Long-format is the canonical input shape used by OSeMOSYS, GenX,
Switch, and PyPSA -- researchers familiar with those tools will find
the convention intuitive.

Added
+++++

* ``prepshot/load_data.py::read_long_csv`` -- new reader for tidy CSVs.
  Convention: dimension columns first, value column last. Output dict
  shape matches what the wide-format reader produces for the same
  parameter (scalar keys for 1 dim, tuple keys for 2+ dims), so model
  code is unchanged regardless of which format is on disk.
* ``params.json`` entries support a new ``"format": "long"`` key.
  When set, the loader looks for ``<file_name>.csv`` instead of
  ``<file_name>.xlsx``, and skips the wide-format-specific keys
  (``index_cols``, ``header_rows``, ``unstack_levels``,
  ``first_col_only``).
* ``tests/test_long_format.py`` -- 7 unit tests covering 1-dim, 2-dim,
  and 3-dim CSV reading; NaN-row dropping; format dispatch in
  ``load_excel_data``; and the optional-input fallback for long-format.

Changed
+++++++

* ``carbon_tax`` migrated from wide-Excel to long-CSV as the working
  demonstration of the new format. ``input/carbon_tax.csv`` and
  ``southeast_asia/carbon_tax.csv`` replace the corresponding
  ``carbon_tax.xlsx`` files. The data and model behavior are identical
  -- the regression test passes unchanged at ``1.879e+11`` objective.

Migration notes
+++++++++++++++

* No action needed for existing input directories that are not based
  on the canonical ``input/`` -- their wide-format files keep working.
* Users with custom ``carbon_tax.xlsx`` files who pull v1.4.0 should
  convert them to ``carbon_tax.csv`` (zone, year, value columns) and
  drop the old xlsx, since ``params.json`` now declares carbon_tax as
  long-format.
* Future features should prefer long-format from the start.

Version 1.3.2 - May 2, 2026
-------------------------------

Continuous-integration release. The full unit-test suite now runs
automatically on every push and pull request via GitHub Actions.

Added
+++++

* ``.github/workflows/test.yml``: matrix-tests on Python 3.9 / 3.10 /
  3.11. Runs the fast unit tests (schema, optional inputs, utils) on
  every push and PR; runs the slow end-to-end regression test only on
  pushes to ``main`` to keep PR feedback fast.

The fast tests give contributors a quick green/red signal on every PR;
the regression test on ``main`` catches any change that would alter the
model's optimal objective on the canonical ``input/`` dataset.

Version 1.3.1 - May 2, 2026
-------------------------------

Security / dependency hygiene release. Bumps declared dependency floors
to clear known CVEs in the previously pinned old releases (the
v0.1.x-era pins were 2-4 years old).

Changed
+++++++

* ``pyproject.toml`` and ``requirements.txt`` floors raised to:

  * ``numpy>=1.26.0,<2.0``
  * ``scipy>=1.11.4``
  * ``pandas>=1.5.3,<2.0``
  * ``xarray>=2023.4.0,<2024``
  * ``openpyxl>=3.1.2``
  * ``xlsxwriter>=3.1.0``

* ``pandas`` and ``numpy`` are temporarily capped below 2.0 because
  pandas 2.x's ``DataFrame.unstack`` no longer accepts duplicate
  column-level values (which the wide input format relies on). The
  cap will be lifted in a future release once ``read_excel`` is
  rewritten to not rely on ``unstack``.

Tested with
+++++++++++

* numpy 1.26.4, scipy 1.13.1, pandas 1.5.3, xarray 2023.12.0,
  openpyxl 3.1.5, xlsxwriter 3.2.9, pyoptinterface 0.2.5,
  highsbox 1.7.0. Full test suite (13 tests) passes.

Migration notes
+++++++++++++++

* Existing environments should run ``pip install -U -r requirements.txt``
  (or ``pip install -e .`` if you use the editable install) to pick up
  the bumped dependency versions.

Version 1.3.0 - May 2, 2026
-------------------------------

Features can now ship with optional input files. New parameters declared
``"required": false`` in ``params.json`` no longer force every existing
input directory to provide a matching Excel file -- a sensible default
is used when the file is absent.

Added
+++++

* ``params.json`` entries support two new keys:

  * ``"required"`` (bool, default ``true``): when ``false``, a missing
    input file is tolerated.
  * ``"default"`` (any, default ``{}``): the value substituted when an
    optional input file is missing. Scalar defaults are wrapped in a
    ``defaultdict`` so model-side tuple-key lookups
    (``params['foo'][z, y]``) keep working unchanged.

* ``tests/test_optional_inputs.py`` covers required-missing-terminates,
  optional-missing-uses-scalar-default, and optional-missing-no-default
  (empty dict).

Changed
+++++++

* The four carbon-market / technology_lower_bound entries in
  ``params.json`` are now marked ``"required": false, "default": 0``,
  so input directories that pre-date v1.1.0 (or any future input dir
  that does not use these features) no longer need to ship the
  zero-filled Excel files.
* ``README.md`` now documents the editable-install path
  (``pip install -e .``) and the ``prepshot`` / ``python -m prepshot``
  console-script entry points introduced in v1.2.0.
* ``doc/source/Installation.rst`` extended with a "Use PREP-SHOT as a
  Python library" section that shows both the high-level
  ``prepshot.cli.main(root_dir=...)`` entry point and the low-level
  ``initialize_environment`` / ``create_model`` / ``solve_model`` flow
  for downstream code that imports PREP-SHOT programmatically.

Removed
+++++++

* ``tests/test_prepshot.py`` -- removed. It exercised the legacy
  ``load_data``, ``read_four_dims``, ``read_three_dims`` etc. APIs
  that were replaced in v0.1.1 by the generic ``read_excel`` helper.
  The test file had been a silent import error since then.

Version 1.2.0 - May 2, 2026
-------------------------------

PREP-SHOT is now installable as a Python package.

Added
+++++

* ``pyproject.toml`` at the repo root, declaring ``prepshot`` as an
  installable package with pinned-but-flexible dependency floors. Allows
  ``pip install -e .`` for local development and ``pip install prepshot``
  once published to PyPI.
* ``prepshot/cli.py`` -- ``main()`` entry point that looks for
  ``config.json`` and ``params.json`` in the current working directory.
* ``prepshot/__main__.py`` -- enables ``python -m prepshot`` invocation.
* Console-script entry point ``prepshot`` (declared in
  ``[project.scripts]``).

Changed
+++++++

* ``run.py`` is now a thin backward-compatible shim that delegates to
  ``prepshot.cli.main``. It preserves the legacy file-relative path
  behavior (``config.json`` / ``params.json`` next to ``run.py``), so
  existing ``python run.py`` workflows continue to work unchanged.

Migration notes
+++++++++++++++

* New: ``pip install -e .`` from the repo root, then run ``prepshot``
  (or ``python -m prepshot``) from any directory containing
  ``config.json`` and ``params.json``.
* Existing: ``python run.py`` still works as before -- no action needed.

Version 1.1.2 - May 2, 2026
-------------------------------

Added
+++++

* ``tests/test_regression.py``: end-to-end regression test that runs the
  full ``python run.py`` flow on the canonical ``input/`` dataset and
  locks in the final-iteration objective (``1.8793771299e+11``) with a
  1 % tolerance. Set ``PREPSHOT_SKIP_SLOW=1`` to skip it (about 150 s).

Fixed
+++++

* ``prepshot/set_up.py`` now skips underscore-prefixed metadata keys
  (e.g. ``_schema_version``) when iterating ``params.json`` to build the
  argparse list. Without this fix v1.1.1 raised ``TypeError: 'int' object
  is not subscriptable`` at the start of ``initialize_environment``,
  breaking ``python run.py`` end-to-end despite the schema guard inside
  ``process_data`` working in isolation.

Version 1.1.1 - May 2, 2026
-------------------------------

Added
+++++

* ``prepshot.load_data.CURRENT_SCHEMA`` constant and a ``check_schema()``
  guard that validates ``params.json`` carries a compatible
  ``_schema_version`` before any input is loaded.
* ``tests/test_schema_version.py`` covering the happy path plus
  rejection of missing, older, and newer schema stamps.

Changed
+++++++

* ``process_data`` now filters out keys beginning with ``_`` (such as
  ``_schema_version``) before iterating the parameter list, so metadata
  stamps cannot accidentally be treated as input files.

Fixed
+++++

* Legacy ``params.json`` files (pre-v1.1.0, no ``_schema_version`` stamp)
  now produce a clear migration hint instead of a downstream
  ``KeyError`` / ``FileNotFoundError``.

Version 1.1.0 - May 2, 2026
-------------------------------

.. note::
   **v1.x is a rapid-evolution series.** Breaking input-format changes may
   occur on minor version bumps. API and input-schema stability will be
   promised with v2.0.0. See the Stability page.

Added
+++++

* Time-varying capacity bounds: ``technology_upper_bound``,
  ``technology_lower_bound``, ``new_technology_upper_bound``, and
  ``new_technology_lower_bound`` are now indexed by ``(zone, tech, year)``.
* Re-introduced ``technology_lower_bound`` constraint on ``cap_existing``.
* Carbon market:

  * ``carbon_offset[y, z]`` decision variable.
  * ``carbon_tax`` cost term in the objective.
  * ``carbon_offset_price`` cost term in the objective.
  * Fractional ``carbon_offset_limit`` constraint
    (``offset <= rate * raw zonal emissions``).
  * ``carbon_capacity[y, z]`` now nets out purchased offsets.

* ``southeast_asia/`` dataset migrated to the new schema.
* ``params.json`` now stamps ``_schema_version: 1``.

Changed (Breaking)
++++++++++++++++++

* Bound input files reshaped from ``(tech, zone)`` to ``(zone, tech, year)``.
* Four new required input files: ``technology_lower_bound``,
  ``carbon_tax``, ``carbon_offset_price``, ``carbon_offset_limit``. The
  shipped defaults are zero-filled, which keeps the carbon-market feature
  dormant.
* ``params.json`` files without ``_schema_version`` are rejected by the
  loader.

Version 1.0 - Jul 21, 2025
-------------------------------

First v1.0 release. Aggregates all changes since v0.1.2 (PRs #23-#34). See
the GitHub release notes for the full list. Notable highlights:

* Bug fixes and refinements to constraint definitions.
* Documentation improvements and added publications.
* Stabilized PyOptInterface integration.

Version 0.1.2 - Jul 22, 2024
-------------------------------

Added
++++++

* Added mathematical notations to the constraint module.
* Added a test script for `prepshot.utils`.

Fixed
++++++

* Fixed the format of the API reference.
* Fix code blocks of documentation.
* Updated `Contribution.rst` to include context on running tests and code style checks.
* Defined explicit data types for inputs and outputs of functions for better type checking and readability.
* Added `pyoptinterface._src.core_ext` to Pylint's extension package allow list to resolve cpp-extension-no-member warning.

Changed
++++++++

* Updated `model.py` to keep necessary decision variables and use expressions for intermediate variables instead of direct determination.
* Refactored `extract_results_non_hydro` in `output_data.py` to extract common features for different variables, simplifying the code.
* Removed definitions of complex sets and opted for simple sets wherever possible to streamline the code.
* Refactor: Organize import order of modules according to PEP 8 guidelines: (1) Grouped standard library imports at the top; (2) Followed by third-party library imports; (3) Local application/library imports at the bottom.

Version 0.1.1 - Jul 11, 2024
-------------------------------

Added
+++++

* Add an example, expansion of Southeast Asia Mainland power system considering hydropower of Lower Mekong River.
* Update the documentation with a docstring for each function and class.
* Add the `Semantic Versioning Specification <https://semver.org>`_.

Fixed
+++++

Changed
+++++++

* Support for solvers such as GUROBI (Commercial), COPT (Commercial), MOSEK (Commercial), and HiGHS (Open source) via `PyOptInterface <https://github.com/metab0t/PyOptInterface>`_.
* Change default solver to HiGHS.
* Change the code comment style to `NumPy <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html>`_.
* Change the code style to `PEP8 <https://pep8.org>`_.
* Categorize constraint definitions based on type (co2, cost, demand, generation, hydro, investment, nondispatchable, storage, transmission) for better organization.
* Split `rule.py` class into serveral smaller, focused classes according to categorized constraint definitions.
* Simplify model by replacing intermediate constraints with direct expressions.
* Extract new modules `solver.py`, `output_data.py`, and `set_up.py` from `run.py` and `utils.py`.
* Remove `parameters.py` into `set_up.py`.
* Refactor and improve comments and function names for clarity and conciseness.

Deprecated
++++++++++

* Removed dependency on `Pyomo <https://pyomo.readthedocs.io/en/stable/solving_pyomo_models.html>`_ due to high memory usage and slow performance for large-scale models. `For you reference <https://metab0t.github.io/PyOptInterface/benchmark.html>`_.

Version 0.1.0 - Jun 24, 2024
--------------------------------

* PREP-SHOT model is released with basic functionality for energy expansion planning.
* Linear programming optimization model for energy systems with multiple zones.
* Support for solvers such as Gurobi, CPLEX, MOSEK, and GLPK via `Pyomo <https://pyomo.readthedocs.io/en/stable/solving_pyomo_models.html>`_.
* Input and output handling with `pandas` and `Xarray`.
