function add_hydrolic_connect!(model::Model, inputs::Dict)

    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    station = inputs["stcd"]
    connect = inputs["connect"]
    inflow = inputs["inflow"]

    # hydrolic connect
    # existing direct upstream reservoirs
    @constraint(model, [h=hour,m=month,y=year,s=station;s ∈ keys(connect)], model[:totalinflow][y,m,h,s] == inflow[s, y, m, h] + 
        sum(h-connect[s][ups]>=1 ? model[:outflow][y,m,h-connect[s][ups],ups] : 
            model[:outflow][y,m,hour[end]+h-connect[s][ups],ups] for ups in keys(connect[s])))
    # no existing direct upstream reservoirs
    @constraint(model, [h=hour,m=month,y=year,s=station;s ∉ keys(connect)], model[:totalinflow][y,m,h,s] == inflow[s, y, m, h])

    return nothing
    
end