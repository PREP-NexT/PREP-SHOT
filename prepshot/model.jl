function add_variables!(model::Model, inputs::Dict)
    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    zone = inputs["zone"]
    tech = inputs["tech"]
    storage_tech = inputs["storage_tech"]
    stcd = inputs["stcd"]
    
    # Variables
    @variable(model, cap_existing[year, zone, tech]>=0)
    @variable(model, cap_newtech[year, zone, tech]>=0)
    @variable(model, cap_newline[year, zone, zone]>=0)
    @variable(model, cap_lines_existing[year, zone, zone]>=0)
    @variable(model, gen[hour, month, year, zone, tech]>=0)
    @variable(model, storage_energy[hour, month, year, zone, storage_tech]>=0)
    @variable(model, charge[hour, month, year, zone, storage_tech]>=0)
    @variable(model, trans_export[hour, month, year, zone, zone]>=0)
    @variable(model, trans_import[hour, month, year, zone, zone]>=0)
    @variable(model, accumu_defer_demand[hour, month, year, zone]>=0)
    @variable(model, serve_demand[hour, month, year, zone]>=0)
    @variable(model, current_defer_demand[hour, month, year, zone]>=0)

    @variable(model, totalinflow[year, month, hour, stcd])
    @variable(model, outflow[year, month, hour, stcd] >=0)
    @variable(model, genflow[year, month, hour, stcd] >=0)
    @variable(model, spillflow[year, month, hour, stcd] >=0)
    @variable(model, storage_reservoir[year, month, hour, stcd] >=0)
    @variable(model, output[year, month, hour, stcd] >=0)

    # intermediate variables
    @variable(model, total_cost)
    
end

function create_model(inputs::Dict)
    elapsed_time = @elapsed begin 
    model = Model()
    add_variables!(model, inputs)
    @objective(model, Min, model[:total_cost])
    # add constraints
    add_cost_function!(model, inputs)
    add_transmission_limits!(model, inputs)  
    add_carbon_limits!(model, inputs)                
    add_existing_tech!(model, inputs)
    add_demand_balance!(model, inputs)
    add_existing_line!(model, inputs)
    add_tech_install_bounds!(model, inputs)
    add_gen_limits!(model, inputs)
    add_storage_limits!(model, inputs)
    add_ramping_limits!(model, inputs)
    # add_demand_side_management!(model, inputs)
    if inputs["isinflow"]
        add_hydrolic_connect!(model, inputs)
        add_water_balance!(model, inputs)
        add_hydro_bounds!(model, inputs)
        add_hydro_output!(model, inputs)
    end
    end
    return model, elapsed_time
end
