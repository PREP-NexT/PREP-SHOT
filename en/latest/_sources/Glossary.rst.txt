.. _Glossary:

Glossary
========

A reference for the energy-modeling, hydropower, and optimization
terminology used throughout PREP-SHOT.

Terminology
-----------

.. glossary::
   :sorted:

   capacity expansion
      The optimization problem of deciding what new generation,
      storage, and transmission to build over a multi-year planning
      horizon, subject to demand, fuel, emission, and budget
      constraints. PREP-SHOT solves a multi-zone, multi-year linear
      capacity-expansion problem.

   capacity factor
      The ratio of a generator's actual output over a period to its
      potential output if it ran at full nameplate capacity for that
      period. Solar photovoltaics typically run at 15-25% capacity
      factor; combined-cycle gas at 40-60%; nuclear at 90%+. In
      PREP-SHOT, time-varying capacity-factor profiles are supplied
      via ``tech_max_gen_profile.csv`` (PyPSA convention:
      ``p_max_pu``).

   carbon cap
      An upper bound on system-wide CO2 emissions, typically declining
      over time. PREP-SHOT supports per-region caps in
      ``policy_carbon_emission_limit.csv``: each row carries a
      comma-separated ``zones`` field that defines the cap's
      jurisdiction.

   carbon offset
      A credit purchased to compensate for emissions, allowing
      generators to exceed an explicit emission cap by paying for
      offsets. PREP-SHOT models offset price (per tonne) and an
      offset purchase limit (per zone, per year).

   carrier
      A free-form string identifying the energy carrier (fuel type)
      of a technology. PREP-SHOT borrows this convention from PyPSA;
      examples include ``coal``, ``gas``, ``hydro``, ``solar``,
      ``wind``, ``biomass``. The ``hydro`` carrier is special-cased
      so the model applies reservoir constraints. Defined in
      ``tech_registry.csv``.

   cascading hydropower
      A sequence of hydropower stations on the same river where the
      outflow of an upstream station is the inflow of a downstream
      station. PREP-SHOT models cascades explicitly with per-station
      mass-balance constraints in ``reservoir_water_delay_time.csv``;
      changes in upstream operation propagate downstream
      automatically.

   commission year
      The calendar year a unit of capacity (a power plant or
      transmission line) was first put into service. Used by
      PREP-SHOT to compute when existing capacity retires (it leaves
      service after ``commission_year + lifetime``). Recorded in
      ``tech_existing.csv`` and ``transmission_existing.csv``.

   demand
      The hourly electric load that must be served at each zone. The
      input file ``demand.csv`` is in MW (instantaneous power);
      PREP-SHOT multiplies by the timestep ``dt`` internally to get
      MWh per timestep, matching ``gen`` and ``charge`` units in the
      output.

   discount factor
      The factor used to compute the present value of a future cash
      flow. PREP-SHOT supports per-zone, per-year discount factors
      via ``economic_discount_factor.csv``, allowing different
      regional cost-of-capital assumptions in the same model.

   dispatch
      The hourly operation of generators and storage to meet demand
      at minimum cost, given the installed capacity. PREP-SHOT
      jointly optimizes investment (capacity expansion) and dispatch.

   dispatchable technology
      A generator whose output can be controlled on demand within
      its ramp limits -- coal, gas, oil, biomass, hydropower with a
      reservoir, etc. Contrasts with :term:`variable renewable energy`
      (VRE).

   forebay level
      The water-surface elevation behind the dam (upstream of the
      generators). Determines the gross head and thus the generation
      efficiency. PREP-SHOT models this as a piecewise-linear
      function of reservoir volume in
      ``reservoir_forebay_level_volume_function.csv``.

   gen
      The model's primary decision variable: generation by each tech,
      zone, hour, month, and year (in MWh per timestep). Output via
      ``ds.gen`` in the result NetCDF.

   generation flow
      The volume of water (m^3/s) routed through a hydropower
      station's turbines, as opposed to spilled around them or stored.
      Bounded above by ``reservoir_generation_flow_max.csv``.

   gross head
      The vertical distance between the forebay level and the
      tailrace level. Drives hydropower generation efficiency
      together with the generation flow:
      ``power = coefficient * head * flow``.

   head iteration
      An outer-loop scheme that successively refines the assumed
      water head until self-consistency is reached. PREP-SHOT solves
      the LP at a fixed head, recomputes head from the resulting
      reservoir trajectory, and re-solves until the head error
      converges (or ``iteration_number`` is reached). The
      ``error_threshold`` setting controls convergence tolerance.

   HiGHS
      An open-source linear-programming solver. PREP-SHOT's default;
      supplied as a wheel by the ``highsbox`` package so no
      separate install is required.

   investment cost
      The capital cost (USD per MW) of building a new unit of
      capacity. PREP-SHOT discounts these to NPV using the relevant
      discount factor (or a project-level WACC if the optional
      finance module is active). Input file:
      ``tech_investment_cost.csv``.

   isinflow
      The toggle in ``config.json`` that activates the per-station
      hydropower / reservoir constraints. Set to ``false`` to model
      hydro as an aggregate dispatchable tech with no reservoir
      physics; set to ``true`` to enable the head-iteration loop.

   linear programming
      An optimization problem with a linear objective and linear
      constraints. PREP-SHOT's capacity-expansion problem is an LP
      (no integer or quadratic terms), which keeps solve times
      tractable for multi-year, multi-zone models. The cost of LP
      vs. MIP is no unit commitment / start-up cost detail.

   LMP
      Locational marginal price. The cost of supplying one extra MWh
      of demand at a specific bus / zone, computed from the dual of
      the demand-balance constraint. Output as
      ``shadow_price_demand`` in the result NetCDF; sign-flipped so
      positive means "more expensive to serve more demand".

   long-format CSV
      The "tidy data" CSV convention used by PREP-SHOT inputs (since
      v1.5): one row per observation, dimension columns first, value
      column last. Replaces the v1.4-era wide-format Excel layout.

   net present value
      The discounted sum of future cash flows expressed in
      present-day terms. PREP-SHOT's objective minimizes the NPV of
      total system cost over the planning horizon. Often abbreviated
      :term:`NPV`.

   NPV
      See :term:`net present value`.

   nominal capacity
      The rated maximum power output of a generator (MW), as opposed
      to its actual output during dispatch. Stored in
      ``tech_existing.csv`` for in-service capacity and bounded in
      ``tech_capacity_max.csv``.

   p_max_pu
      Per-unit upper bound on a generator's dispatch (PyPSA
      convention). For solar, the per-hour capacity-factor profile;
      for thermal techs, usually 1. PREP-SHOT reads this from
      ``tech_max_gen_profile.csv``.

   p_min_pu
      Per-unit lower bound on a generator's dispatch (PyPSA
      convention). Used to model must-run constraints. PREP-SHOT
      reads this from ``tech_min_gen_profile.csv``; default 0.

   PyOptInterface
      The Python wrapper around HiGHS / Gurobi / COPT / MOSEK that
      PREP-SHOT uses as its modeling layer. Faster and lower-memory
      than Pyomo for the same problem class.

   ramp rate
      The hourly fraction of nominal capacity by which a thermal
      generator can change its output. Used to model the operational
      inflexibility of large coal / gas units. Inputs:
      ``tech_ramp_up.csv``, ``tech_ramp_down.csv``.

   representative period
      A subset of hours / months chosen to approximate annual
      operation while keeping the model tractable. PREP-SHOT
      configures this via ``hour`` and ``month`` in ``config.json``.
      The shipped 3-zone scenario uses 48 representative hours x 1
      representative month; the Lower Mekong scenario uses 288 x 1.

   reservoir
      A body of water held behind a dam that provides operational
      flexibility for a hydropower station. PREP-SHOT models per-
      reservoir mass balance, head dynamics, and storage bounds.

   reserve margin
      The fraction of peak demand by which installed capacity must
      exceed peak demand to absorb forecast errors and unplanned
      outages. *Not currently modeled in PREP-SHOT;* legacy v1.4
      data carried a ``reserve_margin`` file that is no longer read.

   shadow price
      The dual variable on a constraint, equal to the rate of change
      of the optimal objective with respect to the constraint's RHS.
      For the demand-balance constraint, the shadow price is the
      :term:`LMP`. Output as ``shadow_price_demand``.

   storage
      A technology that absorbs energy in some hours and releases it
      in others (battery, pumped hydro). PREP-SHOT identifies these
      with ``is_storage=True`` in ``tech_registry.csv``; the model
      tracks state-of-charge per hour with charge / discharge
      efficiency.

   tailrace level
      The water-surface elevation downstream of the dam. Affects
      head together with the forebay level. Modeled as a piecewise-
      linear function of total discharge in
      ``reservoir_tailrace_level_discharge_function.csv``.

   tech_registry
      The CSV file listing every modeled technology with its
      ``carrier``, ``is_storage`` flag, and human-readable ``name``.
      The single source of truth for which techs exist in a scenario.

   transmission existing
      The pre-built transmission capacity between zones at the start
      of the planning horizon. Indexed by ``(zone1, zone2,
      commission_year)`` so age-based retirements work the same way
      as for power plants.

   transmission expansion
      Building new transmission capacity between zones, with bounds
      controlled by ``transmission_candidates.csv``. PREP-SHOT
      models inter-zone transport at the line level (no DC power
      flow / line-impedance constraints).

   variable renewable energy
      Generators with output set by uncontrollable resources -- wind
      and solar most prominently. PREP-SHOT models VRE via the
      ``tech_max_gen_profile.csv`` (per-hour capacity-factor)
      mechanism. Often abbreviated :term:`VRE`.

   VRE
      See :term:`variable renewable energy`.

   WACC
      Weighted-average cost of capital. The blended discount rate
      across a project's debt and equity tranches. Active when the
      v1.9 finance module is enabled (``finance_*.csv`` files
      present); replaces the zonal :term:`discount factor` for
      investment-cost discounting.

   water delay time
      The travel time of water flowing from one reservoir's outlet to
      the next reservoir's inlet in a cascade. Stored in
      ``reservoir_water_delay_time.csv``; lets the model reflect that
      a release upstream takes hours to reach a downstream station.

   zone
      A region modeled as a single bus -- within the zone, supply and
      demand are balanced instantaneously; between zones, electricity
      flows through inter-zone transmission lines with capacity and
      efficiency limits. The ``zone`` set is derived from the keys of
      ``demand.csv``.

Further reading
---------------

Excellent free primers from NREL and DOE, useful as orientation if
the terminology above is new. Read in order: model families first,
then how to read model output, then real-grid grounding.

* `Power Sector Modeling 101
  <https://www.energy.gov/sites/prod/files/2016/02/f30/EPSA_Power_Sector_Modeling_FINAL_021816_0.pdf>`_
  (US DOE EPSA, 2016) -- conceptual tour of the model families
  PREP-SHOT belongs to: capacity expansion vs production cost vs
  unit commitment, what each is for, where their assumptions break.
* `Beginner's Guide to Understanding Power System Model Results for
  Long-Term Resource Plans
  <https://docs.nrel.gov/docs/fy24osti/87105.pdf>`_
  (NREL, 2023) -- companion to PREP-SHOT's output: how to read a
  capacity-expansion result, what the buildouts and dispatch curves
  mean, common pitfalls when interpreting them.
* `Advanced Guide to Understanding Power System Model Results for
  Long-Term Resource Plans
  <https://docs.nrel.gov/docs/fy24osti/88337.pdf>`_
  (NREL, 2024) -- deeper sequel: reliability metrics, reserve
  margin reasoning, transmission congestion interpretation, and
  what differing capacity-expansion studies typically disagree
  about.
* `Electric Grid and Markets 101
  <https://docs.nrel.gov/docs/fy25osti/91864.pdf>`_
  (NREL, 2024) -- how the bulk power system actually works:
  generation, transmission, ISOs/RTOs, day-ahead vs real-time
  markets, ancillary services. Real-world grounding for the
  modeled abstractions.
