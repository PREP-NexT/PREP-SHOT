#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""  
This module contains the class RuleContainer which is used to define the rules 
"""

function cost_rule(container)
    """Objective function of the model, to minimize total cost.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Model with cost constraints.
    """
    model = container["model"]
    @expression(
        model, total_cost, (model[:cost_var] + model[:cost_newtech]
        + model[:cost_fix] + model[:cost_newline] - model[:income])
    )
    @constraint(model, model[:cost] == total_cost)
end

function income_rule(container)
    """Income from water withdrawal.
    Reference: https://www.nature.com/articles/s44221-023-00126-0

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    if container["para"]["isinflow"]
        coef = 3600 * container["para"]["dt"] * container["para"]["price"]
        lhs = @expression(model, model[:income] - sum(
            model[:withdraw][(s, h, m, y)] * coef
            for (s, h, m, y) in model[:station_hour_month_year_tuples]
        ))
        @constraint(model, lhs == 0)
    else
        @constraint(model, model[:income] == 0)
    end
end

function var_cost_rule(container)
    """Calculate total variable cost, which is sum of the fuel cost of 
        technologies and variable Operation and maintenance (O&M) cost of 
        technologies and transmission lines.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    tvc = container["para"]["technology_variable_OM_cost"]
    lvc = container["para"]["transmission_line_variable_OM_cost"]
    dt = container["para"]["dt"]
    w = container["para"]["weight"]
    vf = container["para"]["var_factor"]
    fp = container["para"]["fuel_price"]
    var_om_tech_cost = @expression(model, 1  / w * sum(
        tvc[(te, y)] * model[:gen][(h, m, y, z, te)] * dt * vf[y]
        for (h, m, y, z, te) in model[:hour_month_year_zone_tech_tuples]
    ))

    fuel_cost = @expression(model, 1  / w * sum(
        fp[(te, y)] * model[:gen][(h, m, y, z, te)] * dt * vf[y]
        for (h, m, y, z, te) in model[:hour_month_year_zone_tech_tuples]
    ))

    var_om_line_cost = @expression(model, 0.5 / w * sum(
        lvc[(z, z1)] * model[:trans_export][(h, m, y, z, z1)] * dt * vf[y]
        for (h, m, y, z, z1) in model[:hour_month_year_zone_zone_tuples]
    ))
    @constraint(model, 
        model[:cost_var] - (var_om_tech_cost + fuel_cost
        + var_om_line_cost) == 0
        )
end

function newtech_cost_rule(container)
    """Total investment cost of new technologies.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    tic = container["para"]["technology_investment_cost"]
    ivf = container["para"]["inv_factor"]
    lhs = @expression(model, model[:cost_newtech] - sum(
        tic[(te, y)] * model[:cap_newtech][(y, z, te)] * ivf[(te, y)]
        for (y, z, te) in model[:year_zone_tech_tuples]
    ))
    @constraint(model, lhs == 0)
end


function newline_cost_rule(container)
    """Total investment cost of new transmission lines.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    lc = container["para"]["transmission_line_existing_capacity"]
    d = container["para"]["distance"]
    ivf = container["para"]["trans_inv_factor"]
    lhs = @expression(model, model[:cost_newline] - 0.5 * sum(
        lc[(z, z1)] * model[:cap_newline][(y, z, z1)] * d[(z, z1)] * ivf[y]
        for (y, z, z1) in model[:year_zone_zone_tuples]
    ))
    @constraint(model, lhs == 0)
end


function fix_cost_rule(container)
    """Fixed O&M cost of technologies and transmission lines.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    fc = container["para"]["technology_fixed_OM_cost"]
    ff = container["para"]["fix_factor"]
    lfc = container["para"]["transmission_line_fixed_OM_cost"]
    @expression(model, fix_cost_tech, sum(
        fc[(te, y)] * model[:cap_existing][(y, z, te)] * ff[y]
        for (y, z, te) in model[:year_zone_tech_tuples]
    ))
    @expression(model, fix_cost_line, 0.5 * sum(
        lfc[(z, z1)] * model[:cap_lines_existing][(y, z, z1)] * ff[y]
        for (y, z1, z) in model[:year_zone_zone_tuples]
    ))
    @constraint(model, model[:cost_fix] - (fix_cost_tech+fix_cost_line) == 0)
end

function remaining_capacity_rule(container, y, z, te)
    """Remaining capacity of initial technology due to lifetime 
    restrictions.
    Note: Where in modeled year y, the available technology consists of 
    the following.
    1. The remaining in-service installed capacity from the initial 
    technology.
    2. The remaining in-service installed capacity from newly built 
    technology in the previous modelled years.

    Parameters
    ----------
    y : int
        Planned year.
    z : str
        Zone.
    te : str
        technology.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    year = container["para"]["year"]
    lt = container["para"]["lifetime"]
    y_ix = findfirst(x -> x == y, year)
    new_tech = @expression(model, 
        sum(model[:cap_newtech][(yy, z, te)] for yy in year[1:y_ix]
        if y - yy < lt[(te, y)])
    )
    @constraint(model, 
        model[:cap_existing][(y, z, te)] 
        - (model[:remaining_technology][(y, z, te)] + new_tech) == 0
    )
end


function emission_limit_rule(container, y)
    """Annual carbon emission limits across all zones and technologies.
    
    Parameters
    ----------
    y : int
        Planned year.
        
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    limit = container["para"]["carbon_emission_limit"]
    if limit[y] == Inf
        return nothing
    end
    @constraint(model, model[:carbon][y] - limit[y] <= 0)
end

function emission_calc_rule(container, y)
    """Calculation of annual carbon emission across all zones and
        technologies.

    Parameters
    ----------
    y : int
        Planned year.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    @constraint(model, model[:carbon][y] - sum(
        model[:carbon_capacity][(y, z)]
        for z in model[:zone]
    ) == 0)
end


function emission_calc_by_zone_rule(container, y, z)
    """Calculation of annual carbon emissions by zone.

    Parameters
    ----------
    y : int
        Planned year.
    z : str
        Zone.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    ef = container["para"]["emission_factor"]
    dt = container["para"]["dt"]
    @constraint(model, model[:carbon_capacity][(y, z)] - sum(
        ef[(te, y)] * model[:gen][(h, m, y, z, te)] * dt
        for (h, m, te) in model[:hour_month_tech_tuples]
    ) == 0)
end


function power_balance_rule(container, h, m, y, z)
    """Power balance.
    Note: The total electricity demand for each time period and in each 
    zone should be met by the following.
    1. The sum of imported power energy from other zones.
    2. The generation from zone z minus the sum of exported power 
    energy from zone z to other zones.
    3. The charging power energy of storage technologies in zone z.

    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    lc = container["para"]["transmission_line_existing_capacity"]
    load = container["para"]["demand"]
    imp_z = @expression(model, sum(
        model[:trans_import][(h, m, y, z1, z)]
        for z1 in model[:zone] if haskey(lc, (z, z1))
    ))
    exp_z = @expression(model, sum(
        model[:trans_export][(h, m, y, z, z1)]
        for z1 in model[:zone] if haskey(lc, (z, z1))
    ))
    gen_z = @expression(model, sum(
        model[:gen][(h, m, y, z, te)] for te in model[:tech]
    ))
    charge_z = @expression(model, sum(
        model[:charge][(h, m, y, z, te)] for te in model[:storage_tech]
    ))
    demand_z = load[(z, y, m, h)]
    supply = AffExpr(0.0)
    add_to_expression!(supply, imp_z)
    add_to_expression!(supply, gen_z)
    add_to_expression!(supply, -1, charge_z)
    add_to_expression!(supply, -1, exp_z)
    @constraint(model, demand_z == supply)
end


function trans_physical_rule(container, y, z, z1)
    """Physical transmission lines.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    z1 : str
        Zone.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    @constraint(model,
        model[:cap_newline][(y, z, z1)] - model[:cap_newline][(y, z1, z)]
        == 0
    )
end


function trans_capacity_rule(container, y, z, z1)
    """Transmission capacity equal to the sum of the existing capacity 
        and the new capacity in previous planned years.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    z1 : str
        Zone.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    year = container["para"]["year"]
    lc = container["para"]["transmission_line_existing_capacity"]
    remaining_capacity_line = lc[(z, z1)]
    new_capacity_line = @expression(model, sum(
        model[:cap_newline][(yy, z, z1)] for yy in year[1:findfirst(x -> x == y, year)]
    ))
    @constraint(model, 
        model[:cap_lines_existing][(y, z, z1)]
        - (remaining_capacity_line + new_capacity_line) == 0
    )
end


function trans_balance_rule(container, h, m, y, z, z1)
    """Transmission balance, i.e., the electricity imported from zone z1 
        to zone z should be equal to the electricity exported from zone z 
        to zone z1 multiplied by the transmission line efficiency.

    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    z1 : str
        Zone.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    eff = container["para"]["transmission_line_efficiency"][(z, z1)]
    @constraint(model, 
        model[:trans_import][(h, m, y, z, z1)]
        - eff * model[:trans_export][(h, m, y, z, z1)] == 0
    )
end


function trans_up_bound_rule(container, h, m, y, z, z1)
    """Transmitted power is less than or equal to the transmission line 
        capacity.

    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    z1 : str
        Zone.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    @constraint(model, 
        model[:trans_export][(h, m, y, z, z1)]
        - model[:cap_lines_existing][(y, z, z1)] <= 0
    )
end


function gen_up_bound_rule(container, h, m, y, z, te)
    """Generation is less than or equal to the existing capacity.

    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.
        
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    @constraint(model,
        model[:gen][(h, m, y, z, te)] - model[:cap_existing][(y, z, te)]
        <= 0
    )
end


function tech_up_bound_rule(container, y, z, te)
    """Allowed capacity of commercial operation technology is less than or 
        equal to the predefined upper bound.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.
        
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    tub =  container["para"]["technology_upper_bound"][(te, z)]
    if tub != Inf
        @constraint(model, model[:cap_existing][(y, z, te)] - tub <= 0)
    end
end


function new_tech_up_bound_rule(container, y, z, te)
    """New investment technology upper bound in specific year and zone.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.
        
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    ntub = container["para"]["new_technology_upper_bound"][(te, z)]
    if ntub != Inf
        @constraint(model, model[:cap_newtech][(y, z, te)] - ntub <= 0)
    end
end


function new_tech_low_bound_rule(container, y, z, te)
    """New investment technology lower bound.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    ntlb = container["para"]["new_technology_lower_bound"][(te, z)]
    @constraint(model, 0 <= model[:cap_newtech][(y, z, te)] - ntlb)
end


function renew_gen_rule(container, h, m, y, z, te)
    """Renewable generation is determined by the capacity factor and 
        existing capacity.
    
    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    cf = container["para"]["capacity_factor"][(te, z, y, m, h)]
    dt = container["para"]["dt"]
    @constraint(model, 
        model[:gen][(h, m, y, z, te)] 
        - model[:cap_existing][(y, z, te)] * cf * dt 
        <= 0
    )
end


function tech_lifetime_rule(container, y, z, te)
    """Caculation of remaining technology capacity based on lifetime 
        constraints.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    lifetime = container["para"]["lifetime"][(te, y)]
    service_time = y - container["para"]["year"][1]
    hcap = container["para"]["historical_capacity"]
    rt = model[:remaining_technology][(y, z, te)]
    remaining_time = Int(lifetime - service_time)
    if remaining_time <= 0
        lhs = @expression(model, model[:remaining_technology][(y, z, te)])
    else
        lhs = @expression(model, rt - sum(
            hcap[(z, te, a)] for a in 0:remaining_time-1
        ))
    end
    @constraint(model, lhs == 0)
end


function energy_storage_balance_rule(container, h, m, y, z, te)
    """Energy storage balance.

    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.
        
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    de = container["para"]["discharge_efficiency"][(te, y)]
    dt = container["para"]["dt"]
    ce = container["para"]["charge_efficiency"][(te, y)]
    @constraint(model, model[:storage][(h, m, y, z, te)] - (
        model[:storage][(h-1, m, y, z, te)] 
        - model[:gen][(h, m, y, z, te)] * de * dt 
        + model[:charge][(h, m, y, z, te)] * ce * dt) == 0
    )
end


function init_energy_storage_rule(container, m, y, z, te)
    """Initial energy storage.

    Parameters
    ----------
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.
        
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    esl = container["para"]["initial_energy_storage_level"][(te, z)]
    epr = container["para"]["energy_to_power_ratio"][te]
    @constraint(model, 
        model[:storage][(0, m, y, z, te)] 
        - esl * model[:cap_existing][(y, z, te)] * epr == 0
    )
end


function end_energy_storage_rule(container, m, y, z, te)
    """End energy storage.

    Parameters
    ----------
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.
        
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    h_init = container["para"]["hour"][end]
    @constraint(model, model[:storage][(h_init, m, y, z, te)] 
        - model[:storage][(0, m, y, z, te)] == 0)
end


function energy_storage_up_bound_rule(container, h, m, y, z, te)
    """Energy storage upper bound.

    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    epr = container["para"]["energy_to_power_ratio"][te]
    @constraint(model, model[:storage][(h, m, y, z, te)] 
        - model[:cap_existing][(y, z, te)] * epr <= 0)
end


function energy_storage_gen_rule(container, h, m, y, z, te)
    """Energy storage generation.

    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.
        
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    de = container["para"]["discharge_efficiency"][(te, y)]
    dt = container["para"]["dt"]
    @constraint(model, 
        model[:gen][(h, m, y, z, te)] * de * dt
        - model[:storage][(h-1, m, y, z, te)] <= 0)
end


function ramping_up_rule(container, h, m, y, z, te)
    """Ramping up limits.

    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.
        
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    rp = container["para"]["ramp_up"][te] * container["para"]["dt"]
    if h > 1 && rp < 1
        @constraint(model,
            model[:gen][(h, m, y, z, te)] - model[:gen][(h-1, m, y, z, te)]
            - rp * model[:cap_existing][(y, z, te)] <= 0
        )
    end
end


function ramping_down_rule(container, h, m, y, z, te)
    """Ramping down limits.

    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.
        
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    rd = container["para"]["ramp_down"][te] * container["para"]["dt"]
    if h > 1 && rd < 1
        @constraint(model,
            model[:gen][(h-1, m, y, z, te)] - model[:gen][(h, m, y, z, te)] 
            - rd * model[:cap_existing][(y, z, te)] <= 0
        )
    end
end


function natural_inflow_rule(container, s, h, m, y)
    """Natural inflow.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    inflow = container["para"]["inflow"][(s, y, m, h)]
    @constraint(model, model[:naturalinflow][(s, h, m, y)] - inflow == 0)
end


function total_inflow_rule(container, s, h, m, y)
    """Total inflow.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    hour = container["para"]["hour"]
    wdt = container["para"]["water_delay_time"]
    dt = container["para"]["dt"]
    up_stream_outflow = AffExpr(0.0)
    if haskey(wdt, s)
        for (ups, delay) in zip(
            wdt[s][1],
            wdt[s][2]
        )
            delay = Int(Int(delay)/dt)
            if (h - delay >= hour[1])
                t = h-delay
            else
                t = hour[end] - delay + h
            end
            add_to_expression!(up_stream_outflow, model[:outflow][(ups, t, m, y)])
        end
    end
    @constraint(model, 
        (model[:inflow][(s, h, m, y)] - 
        (model[:naturalinflow][(s, h, m, y)] + up_stream_outflow)
        ) == 0
    )
end


function water_balance_rule(container, s, h, m, y)
    """Water balance of reservoir.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    dt = container["para"]["dt"]
    netflow = @expression(model,
        model[:inflow][(s, h, m, y)]
        - model[:outflow][(s, h, m, y)]
        - model[:withdraw][(s, h, m, y)]
    )
    @constraint(model, model[:storage_reservoir][(s, h, m, y)] - (
        model[:storage_reservoir][(s, h-1, m, y)] + 3600 * dt * netflow
    ) == 0)
end


function discharge_rule(container, s, h, m, y)
    """Total outflow of reservoir is equal to the sum of generation and 
        spillage.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    @constraint(model, model[:outflow][(s, h, m, y)] - (
        model[:genflow][(s, h, m, y)] + model[:spillflow][(s, h, m, y)]
    ) == 0)
end


function outflow_low_bound_rule(container, s, h, m, y)
    """Total outflow lower bound.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]        
    @constraint(model, 
        0 <= model[:outflow][(s, h, m, y)] 
        - container["para"]["reservoir_characteristics"]["outflow_min", s]
    )
end


function outflow_up_bound_rule(container, s, h, m, y)
    """Total outflow upper bound.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    @constraint(model, 
        model[:outflow][(s, h, m, y)] 
        - container["para"]["reservoir_characteristics"]["outflow_max", s] 
        <= 0
    )
end


function storage_low_bound_rule(container, s, h, m, y)
    """Storage lower bound.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    min_storage = container["para"]["reservoir_storage_lower_bound"][(s, m, h)]
    @constraint(model, 0 <= model[:storage_reservoir][(s, h, m, y)] - min_storage)
end


function storage_up_bound_rule(container, s, h, m, y)
    """Storage upper bound.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    max_storage = container["para"]["reservoir_storage_upper_bound"][(s, m, h)]
    @constraint(model, model[:storage_reservoir][(s, h, m, y)] - max_storage <= 0)
end


function output_low_bound_rule(container, s, h, m, y)
    """Power output of hydropower lower bound.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    min_output = container["para"]["reservoir_characteristics"]["N_min", s]
    @constraint(model, 0 <= model[:output][(s, h, m, y)] - min_output)
end


function output_up_bound_rule(container, s, h, m, y)
    """Power output of hydropower upper bound.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    max_output = container["para"]["reservoir_characteristics"]["N_max", s]
    @constraint(model, model[:output][(s, h, m, y)] - max_output <= 0)
end


function output_calc_rule(container, s, h, m, y)
    """Hydropower production calculation.
    Head parameter is specified after building the model.

    Parameters
    ----------
    s : str
        hydropower plant.
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    efficiency = container["para"]["reservoir_characteristics"]["coeff", s]
    lhs = @expression(model,
        model[:output][(s, h, m, y)]
        - model[:genflow][(s, h, m, y)] * efficiency * 1e-3 #  * head_param
    )
    @constraint(model, lhs == 0)
end


function init_storage_rule(container, s, m, y)
    """Initial storage of reservoir.

    Parameters
    ----------
    s : str
        hydropower plant.
    m : int
        Month.
    y : int
        Year.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    hour_period = model[:hour_p]
    init_storage = container["para"]["initial_reservoir_storage_level"][(m, s)]
    @constraint(model, model[:storage_reservoir][(s, hour_period[1], m, y)] - init_storage == 0)
end

function end_storage_rule(container, s, m, y)
    """End storage of reservoir.

    Parameters
    ----------
    s : str
        hydropower plant.
    m : int
        Month.
    y : int
        Year.

    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    hour_period = model[:hour_p]
    final_storage = container["para"]["final_reservoir_storage_level"][(m, s)]
    @constraint(model, 
        model[:storage_reservoir][(s, hour_period[end], m, y)] - final_storage 
        == 0
    )
end


function hydro_output_rule(container, h, m, y, z)
    """Hydropower output constraints.

    Parameters
    ----------
    h : int
        Hour.
    m : int
        Month.
    y : int
        Year.
    z : str
        Zone.
    
    Returns
    -------
    pyoptinterface._src.core_ext.ConstraintIndex
        Constraint index of the model.
    """
    model = container["model"]
    # tech_type = container["para"]["technology_type"]
    res_char = container["para"]["reservoir_characteristics"]
    dt = container["para"]["dt"]
    predifined_hydro = container["para"]["predefined_hydropower"]
    hydro_type = model[:hydro_tech]
    if length(hydro_type) == 0
        return nothing
    end
    if container["para"]["isinflow"]
        hydro_output = @expression(model, sum(
            model[:output][(s, h, m, y)] * dt
            for s in model[:station] if res_char["zone", s] == z
        ))
    else
        hydro_output = predifined_hydro["Hydro", z, y, m, h] * dt
        
    end
    @constraint(model,
        model[:gen][(h, m, y, z, hydro_type[1])] - hydro_output == 0
    )
end

function cost_var_breakdown_ep(container, y, z, te)
    """Variable operation and maintenance cost breakdown.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.

    Returns
    -------
    pyoptinterface._src.core_ext.ExprBuilder
        index of expression of the model.
    """
    model = container["model"]
    tvc = container["para"]["technology_variable_OM_cost"][(te, y)]
    dt = container["para"]["dt"]
    vf = container["para"]["var_factor"][y]
    cost_var_breakdown = @expression(model, sum(
        tvc * model[:gen][(h, m, y, z, te)] * dt * vf
        for (h, m) in model[:hour_month_tuples]
    ))
    return cost_var_breakdown
end

function cost_fix_breakdown_ep(container, y, z, te)
    """Fixed operation and maintenance cost breakdown.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.

    Returns
    -------
    pyoptinterface._src.core_ext.ExprBuilder
        index of expression of the model.
    """
    model = container["model"]
    tfc = container["para"]["technology_fixed_OM_cost"][(te, y)]
    ff = container["para"]["fix_factor"][y]
    cost_fix_breakdown = @expression(model,
         tfc * model[:cap_existing][(y, z, te)] * ff
    )
    return cost_fix_breakdown
end

function cost_newtech_breakdown_ep(container, y, z, te)
    """New technology investment cost breakdown.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.

    Returns
    -------
    pyoptinterface._src.core_ext.ExprBuilder
        index of expression of the model.
    """
    model = container["model"]
    tic = container["para"]["technology_investment_cost"][(te, y)]
    ivf = container["para"]["inv_factor"][(te, y)]
    cost_newtech_breakdown = @expression(model, 
        tic * model[:cap_newtech][(y, z, te)] * ivf
    )
    return cost_newtech_breakdown
end

function cost_newline_breakdown_ep(container, y, z, z1)
    """New transmission line investment cost breakdown.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    z1 : str
        Zone.

    Returns
    -------
    pyoptinterface._src.core_ext.ExprBuilder
        index of expression of the model.
    """
    model = container["model"]
    lic = container["para"]["transmission_line_investment_cost"][(z, z1)]
    cost_newline_breakdown = @expression(model, 
        lic * model[:cap_newline][(y, z, z1)]
    )
    return cost_newline_breakdown
end

function carbon_breakdown_ep(container, y, z, te)
    """Carbon emission cost breakdown.

    Parameters
    ----------
    y : int
        Year.
    z : str
        Zone.
    te : str
        Technology.

    Returns
    -------
    pyoptinterface._src.core_ext.ExprBuilder
        index of expression of the model.
    """
    model = container["model"]
    ef = container["para"]["emission_factor"][(te, y)]
    dt = container["para"]["dt"]
    
    carbon_breakdown = @expression(model, sum(
        ef * model[:gen][(h, m, y, z, te)] * dt
        for (h, m) in model[:hour_month_tuples]
    ))
    return carbon_breakdown
end