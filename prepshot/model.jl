#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
This module defines the PREP-SHOT model. The model is created using 
the pyoptinterface library.
"""
# import logging
# from itertools import product
# import pyoptinterface as poi
# from pyoptinterface import mosek
# from pyoptinterface import gurobi
# from pyoptinterface import highs
# from pyoptinterface import copt
# from prepshot.rules import RuleContainer
# from prepshot.logs import timer

function define_model(para)
    """This function defines the model using the pyoptinterface library.

    Parameters
    ----------
    para : dict
        parameters for the model

    Returns
    -------
    pyoptinterface._src.mosek.Model
        A pyoptinterface Model object

    Raises
    ------
    ValueError
        Unsupported solver
    """
    # solver_map = {
    #     "mosek": mosek,
    #     "gurobi": gurobi,
    #     "highs": highs,
    #     "copt": copt
    # }

    # solver = para["solver"]["solver"]
    # if solver in solver_map:
    #     poi_solver = solver_map[solver]
    # else:
    #     raise ValueError(f"Unsupported solver: {solver}")
    # if not poi_solver.autoload_library():
    #     logging.warning(
    #         "%s library failed to load automatically." 
    #         + "Attempting to load manually.", solver
    #     )
    #     if not poi_solver.load_library(para["solver"]["solver_path"]):
    #         raise ValueError(f"Failed to load {solver} library.")
    #     logging.info("Loaded %s library manually.", solver)
    # else:
    #     logging.info("Loaded %s library automatically.", solver)

    # model = poi_solver.Model()

    # # set the value of the solver-specific parameters
    # for key, value in para["solver"].items():
    #     if key not in ("solver", "solver_path"):
    #         model[:set_raw_parameter](key, value)
    model = Model(Gurobi.Optimizer; add_bridges = false)
    set_time_limit_sec(model, 0.0)
    return model
end

function define_basic_sets(model, para)
    """Define sets for the model.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    para : dict
        Dictionary of parameters for the model.

    Returns
    -------
    None
    """
    basic_sets = ["year", "zone", "tech", "hour", "month"]
    tech_types = ["storage", "nondispatchable", "dispatchable", "hydro"]
    model[:tech_types] = tech_types
    for set_name in basic_sets
        model[Symbol(set_name)] = para[set_name]
    end
    model[:hour_p] = append!([0], para["hour"])
    tech_category = para["technology_type"]
    # tech_category: {
    #    "Coal": "dispatchable",
    #    "Solar": "nondispatchable",
    #    ...
    # }
    for tech_type in tech_types
        tech_set = [k for (k, v) in tech_category if v == tech_type]
        model[Symbol("$(tech_type)_tech")] = tech_set
    end
    if para["isinflow"]
        model[:station] = para["stcd"]
    end
end

function define_complex_sets(model, para)
    """Create complex sets based on simple sets and some conditations.
    Note: The existing capacity between two zones is set to empty 
    (i.e., No value is filled in the Excel cell), which means that these two 
    zones cannot have newly built transmission lines. If you want to enable 
    two zones which do not have any existing transmission lines, 
    to build new transmission lines in the planning horizon, you need to set 
    their capacity as zero explicitly.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.

    Returns
    -------
    None
    """
    function cartesian_product(args...)
        # [1, 2], [7, 8] -> [(1, 7), (1, 8), (2, 7), (2, 8)]
        collect(Base.Iterators.product(args...))
    end
    h = model[:hour]
    hp = model[:hour_p]
    m = model[:month]
    y = model[:year]
    z = model[:zone]
    te = model[:tech]
    st = model[:storage_tech]
    nd = model[:nondispatchable_tech]

    model[:hour_month_year_tuples] = cartesian_product(h, m, y)
    model[:hour_month_tuples] = cartesian_product(h, m)
    model[:hour_month_year_zone_storage_tuples] =
        cartesian_product(h, m, y, z, st)
    model[:hour_month_year_zone_nondispatchable_tuples] =
        cartesian_product(h, m, y, z, nd)
    model[:hour_month_year_zone_tech_tuples] = cartesian_product(h, m, y, z, te)
    model[:hour_month_year_zone_tuples] = cartesian_product(h, m, y, z)
    trans_sets = para["transmission_line_existing_capacity"]
    model[:year_zone_zone_tuples] = [
        (y_i, z_i, z1_i) for y_i in y, z_i in z, z1_i in z
        if haskey(trans_sets, (z_i, z1_i))
    ]
    model[:hour_month_year_zone_zone_tuples] = [
        (h_i, m_i, y_i, z_i, z1_i)
        for h_i in h, m_i in m, y_i in y, z_i in z, z1_i in z
        if haskey(trans_sets, (z_i, z1_i))
    ]
    model[:hour_month_tech_tuples] = cartesian_product(h, m, te)
    model[:hour_p_month_year_zone_tuples] = cartesian_product(hp, m, y, z)
    model[:hour_p_month_year_zone_tech_tuples] =
        cartesian_product(hp, m, y, z, te)
    model[:hour_p_month_year_zone_storage_tuples] =
        cartesian_product(hp, m, y, z, st)
    model[:month_year_zone_tuples] = cartesian_product(m, y, z)
    model[:month_year_zone_storage_tuples] = cartesian_product(m, y, z, st)
    model[:year_zone_tuples] = cartesian_product(y, z)
    model[:year_zone_tech_tuples] = cartesian_product(y, z, te)
    model[:year_tech_tuples] = cartesian_product(y, te)

    if para["isinflow"]
        s = model[:station]
        model[:station_hour_month_year_tuples] = cartesian_product(s, h, m, y)
        model[:station_hour_p_month_year_tuples] = cartesian_product(s, hp, m, y)
        model[:station_month_year_tuples] = cartesian_product(s, m, y)
    end
end

function define_variables(model, para)
    """Define variables for the model.

    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    para : dict
        Dictionary of parameters for the model.
    """
    @variable(model, cost >= 0)
    @variable(model, cost_var >= 0)
    @variable(model, cost_fix >= 0)
    @variable(model, cost_newtech >= 0)
    @variable(model, cost_newline >= 0)
    @variable(model, income >= 0)
    
    @variable(model, cap_existing[model[:year_zone_tech_tuples]] >= 0)
    @variable(model, cap_newtech[model[:year_zone_tech_tuples]] >= 0)
    @variable(model, cap_newline[model[:year_zone_zone_tuples]] >= 0)
    @variable(model, cap_lines_existing[model[:year_zone_zone_tuples]] >= 0)
    @variable(model, carbon[model[:year]] >= 0)
    @variable(model, carbon_capacity[model[:year_zone_tuples]] >= 0)
    @variable(model, gen[model[:hour_month_year_zone_tech_tuples]] >= 0)
    @variable(model, storage[model[:hour_p_month_year_zone_tech_tuples]] >= 0)
    @variable(model, charge[model[:hour_month_year_zone_tech_tuples]] >= 0)
    @variable(model, trans_export[model[:hour_month_year_zone_zone_tuples]] >= 0)
    @variable(model, trans_import[model[:hour_month_year_zone_zone_tuples]] >= 0)
    @variable(model, remaining_technology[model[:year_zone_tech_tuples]] >= 0)

    if para["isinflow"]
        @variable(model, naturalinflow[model[:station_hour_month_year_tuples]])
        @variable(model, inflow[model[:station_hour_month_year_tuples]])
        @variable(model, outflow[model[:station_hour_month_year_tuples]] >= 0)
        @variable(model, genflow[model[:station_hour_month_year_tuples]] >= 0)
        @variable(model, spillflow[model[:station_hour_month_year_tuples]] >= 0)
        @variable(model, withdraw[model[:station_hour_month_year_tuples]] >= 0)
        @variable(model, storage_reservoir[model[:station_hour_p_month_year_tuples]] >= 0)
        @variable(model, output[model[:station_hour_month_year_tuples]] >= 0)
    end
end

function define_constraints(model, para)
    """Define constraints for the model.
    
    Parameters
    ----------
    model : pyoptinterface._src.mosek.Model
        Model to be solved.
    para : dict
        Dictionary of parameters for the model.

    Returns:
    None
    """
    container = Dict("model"=>model, "para"=>para)
    function generate_constraints(constraints)
        map(constraint -> 
        begin
            attr, tuples, rule_func = constraint
            if isempty(tuples)
                model[Symbol(attr)] = rule_func(container)
            else
                model[Symbol(attr)] = map(item -> rule_func(container, item...), tuples)
            end
        end, constraints)
    end

    # rewrite the constraints in the rules.jl file
    constraints = [
        (:total_cost_cons, (), cost_rule),
        (:power_balance_cons, model[:hour_month_year_zone_tuples], power_balance_rule),
        (:trans_capacity_cons, model[:year_zone_zone_tuples], trans_capacity_rule),
        (:trans_physical_cons, model[:year_zone_zone_tuples], trans_physical_rule),
        (:trans_balance_cons, model[:hour_month_year_zone_zone_tuples], trans_balance_rule),
        (:trans_up_bound_cons, model[:hour_month_year_zone_zone_tuples], trans_up_bound_rule),
        (:gen_up_bound_cons, model[:hour_month_year_zone_tech_tuples], gen_up_bound_rule),
        (:tech_up_bound_cons, model[:year_zone_tech_tuples], tech_up_bound_rule),
        (:new_tech_up_bound_cons, model[:year_zone_tech_tuples], new_tech_up_bound_rule),
        (:new_tech_low_bound_cons, model[:year_zone_tech_tuples], new_tech_low_bound_rule),
        (:tech_lifetime_cons, model[:year_zone_tech_tuples], tech_lifetime_rule),
        (:ramping_up_cons, model[:hour_month_year_zone_tech_tuples], ramping_up_rule),
        (:ramping_down_cons, model[:hour_month_year_zone_tech_tuples], ramping_down_rule),
        (:cost_var_cons, (), var_cost_rule),
        (:newtech_cost_cons, (), newtech_cost_rule),
        (:newline_cost_cons, (), newline_cost_rule),
        (:fix_cost_cons, (), fix_cost_rule),
        (:remaining_capacity_cons, model[:year_zone_tech_tuples], remaining_capacity_rule),
        (:emission_limit_cons, model[:year], emission_limit_rule),
        (:emission_calc_cons, model[:year], emission_calc_rule),
        (:emission_calc_by_zone_cons, model[:year_zone_tuples], emission_calc_by_zone_rule),
        (:hydro_output_cons, model[:hour_month_year_zone_tuples], hydro_output_rule),
    ]
    if model[:nondispatchable_tech] != 0
        append!(constraints, [
            (:renew_gen_cons, model[:hour_month_year_zone_nondispatchable_tuples], renew_gen_rule),
        ])
    end
    if model[:storage_tech] != 0
        append!(constraints, [
            (:energy_storage_balance_cons, model[:hour_month_year_zone_storage_tuples], energy_storage_balance_rule),
            (:init_energy_storage_cons, model[:month_year_zone_storage_tuples], init_energy_storage_rule),
            (:end_energy_storage_cons, model[:month_year_zone_storage_tuples], end_energy_storage_rule),
            (:energy_storage_up_bound_cons, model[:hour_month_year_zone_storage_tuples], energy_storage_up_bound_rule),
            (:energy_storage_gen_cons, model[:hour_month_year_zone_storage_tuples], energy_storage_gen_rule),
        ])
    end

    if para["isinflow"]
        append!(constraints, [
            (:natural_inflow_cons, model[:station_hour_month_year_tuples], natural_inflow_rule),
            (:total_inflow_cons, model[:station_hour_month_year_tuples], total_inflow_rule),
            (:water_balance_cons, model[:station_hour_month_year_tuples], water_balance_rule),
            (:discharge_cons, model[:station_hour_month_year_tuples], discharge_rule),
            (:outflow_low_bound_cons, model[:station_hour_month_year_tuples], outflow_low_bound_rule),
            (:outflow_up_bound_cons, model[:station_hour_month_year_tuples], outflow_up_bound_rule),
            (:storage_low_bound_cons, model[:station_hour_month_year_tuples], storage_low_bound_rule),
            (:storage_up_bound_cons, model[:station_hour_month_year_tuples], storage_up_bound_rule),
            (:output_low_bound_cons, model[:station_hour_month_year_tuples], output_low_bound_rule),
            (:output_up_bound_cons, model[:station_hour_month_year_tuples], output_up_bound_rule),
            (:output_calc_cons, model[:station_hour_month_year_tuples], output_calc_rule),
            (:init_storage_cons, model[:station_month_year_tuples], init_storage_rule),
            (:end_storage_cons, model[:station_month_year_tuples], end_storage_rule),
            (:income_cons, (), income_rule),
        ])
    end
    append!(constraints, [
        (:cost_var_breakdown, model[:year_zone_tech_tuples], cost_var_breakdown_ep),
        (:cost_fix_breakdown, model[:year_zone_tech_tuples], cost_fix_breakdown_ep),
        (:cost_newtech_breakdown, model[:year_zone_tech_tuples], cost_newtech_breakdown_ep),
        (:cost_newline_breakdown, model[:year_zone_zone_tuples], cost_newline_breakdown_ep),
        (:carbon_breakdown, model[:year_zone_tech_tuples], carbon_breakdown_ep),
    ])
    
    # generate constraints
    generate_constraints(constraints)
end

function create_model(para)
    """Create the PREP-SHOT model.

    Parameters
    ----------
    para : dict
        Dictionary of parameters for the model.

    Returns
    -------
    pyoptinterface._src.mosek.Model
        A pyoptinterface Model object.
    """
    elapsed_time = @elapsed begin
    
    # Define a model according to the given solver.
    model = define_model(para)
    define_basic_sets(model, para)
    define_complex_sets(model, para)
    define_variables(model, para)
    # Define objective function for the model.
    @objective(model, Min,  model[:cost])
    define_constraints(model, para)
    optimize!(model)
    end
    println("Model created in $(elapsed_time) seconds.")
    Base.exit()
    
    return model
end
