function add_cost_function!(model::Model, inputs::Dict)
    
    weight = inputs["weight"]
    var_cost = inputs["technology_variable_cost"]
    var_factor = inputs["var_factor"]
    fuel_price = inputs["fuel_price"]
    inv_cost = inputs["technology_investment_cost"]
    inv_factor = inputs["inv_factor"]
    fix_cost = inputs["technology_fix_cost"]
    fix_factor = inputs["fix_factor"]
    line_var_cost = inputs["transline_variable_cost"]
    line_inv_cost = inputs["transline_investment_cost"]
    transline = inputs["transline"]
    distance = inputs["distance"]
    trans_inv_factor = inputs["trans_inv_factor"]
    line_fix_cost = inputs["transline_fix_cost"]
    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    zone = inputs["zone"]
    tech = inputs["tech"]

    # Objection function
    # 1. total fuel cost of technologies and variable
    # Operation and maintenance (O&M) cost of technologies and transmission lines.
    model[:var_OM_tech_cost] = @expression(model, sum(var_cost[e,y] * model[:gen][h,m,y,z,e] * var_factor[y] for (h,m,y,z,e) in Iterators.product(hour, month, year, zone, tech))/ weight)

    model[:fuel_cost] = @expression(model, sum(fuel_price[e,y] * model[:gen][h,m,y,z,e] * var_factor[y]
                            for (h,m,y,z,e) in Iterators.product(hour, month, year, zone, tech))/ weight)
    model[:var_OM_line_cost] = @expression(model, 0.5 * sum([line_var_cost[z,z1] * model[:trans_export][h,m,y,z,z1] * var_factor[y] for (z,z1) in keys(transline) for (h,m,y) in Iterators.product(hour, month, year)]) / weight) #  for z1 in keys(transline[z])
    # 2. total investment cost of new technologies and new transmission lines.
    model[:cost_newtech] = @expression(model, sum(inv_cost[e,y] * model[:cap_newtech][y,z,e] * inv_factor[e,y] for (y,z,e) in Iterators.product(year, zone, tech)))
    model[:cost_newline] = @expression(model, 0.5 * sum(line_inv_cost[z,z1] * model[:cap_newline][y,z,z1] * distance[z,z1] * trans_inv_factor[y]
                            for (z,z1) in keys(transline) for y in year)) #for z1 in keys(transline[z])
    # 3. fixed O&M cost of technologies and transmission lines.
    model[:fix_cost_tech] = @expression(model, sum(fix_cost[e,y] * model[:cap_existing][y,z,e] * fix_factor[y] for (y,z,e) in Iterators.product(year, zone, tech)))
    model[:fix_cost_line] = @expression(model, 0.5 * sum(line_fix_cost[z,z1] * model[:cap_lines_existing][y, z, z1] * fix_factor[y] for (z,z1) in keys(transline) for y in year)) # for z1 in keys(transline[z])
    @constraint(model, model[:total_cost] == model[:var_OM_tech_cost] + model[:fuel_cost] + model[:var_OM_line_cost] + 
    model[:cost_newtech] + model[:cost_newline] + model[:fix_cost_tech] + model[:fix_cost_line])

    return nothing
end