function add_hydro_bounds!(model::Model, inputs::Dict)

    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    station = inputs["stcd"]
    static = inputs["static"]
    storage_upbound = inputs["storage_upbound"]
    storage_downbound = inputs["storage_downbound"]

    # output, storage, outflow bounds Constraints
    @constraint(model, [h=hour,m=month,y=year,s=station], model[:outflow][y,m,h,s] <= static["outflow_max", s])
    @constraint(model, [h=hour,m=month,y=year,s=station], model[:output][y,m,h,s] <= static["N_max", s])
    @constraint(model, [h=hour,m=month,y=year,s=station], model[:storage_reservoir][y,m,h,s] <= storage_upbound[s, m, h])
    @constraint(model, [h=hour,m=month,y=year,s=station], storage_downbound[s, m, h]<= model[:storage_reservoir][y,m,h,s])

    return nothing 
end