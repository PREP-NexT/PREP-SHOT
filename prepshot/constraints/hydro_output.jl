function add_hydro_output!(model::Model, inputs::Dict)

    static = inputs["static"]
    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    zone = inputs["zone"]
    station = inputs["stcd"]
    dt = inputs["dt"]
    type = inputs["type"]
    hydro_power_unit = inputs["hydro_power_unit"]

    # output
    @constraint(model, [h=hour,m=month,y=year,s=station], model[:output][y,m,h,s] == 
        static["head", s] * static["coeff", s] * model[:genflow][y,m,h,s] * hydro_power_unit)
    # hydropower output by province
    for (e,class) in type
        if class == "hydro"
            @constraint(model, [h=hour,m=month,y=year,z=zone], model[:gen][h,m,y,z,e] == 
                sum(model[:output][y,m,h,s] for s in station if static["zone", s]==z) * dt)
        end
    end

    return nothing
end