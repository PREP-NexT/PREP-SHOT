function add_water_balance!(model::Model, inputs::Dict)
    
    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    station = inputs["stcd"]
    storage_init = inputs["storage_init"]
    storage_end = inputs["storage_end"]
    seconds_in_hour = inputs["seconds_in_hour"]
    hydro_storage_unit = inputs["hydro_storage_unit"]
    
    # water_balance
    @constraint(model, [m=month,y=year,s=station], model[:storage_reservoir][y,m,hour[end],s] == storage_end[m, s])
    @constraint(model, [h=hour,m=month,y=year,s=station;h>1], model[:storage_reservoir][y,m,h,s] == model[:storage_reservoir][y,m,h-1,s] + 
        seconds_in_hour*(model[:totalinflow][y,m,h,s] - model[:outflow][y,m,h,s])* hydro_storage_unit)
    @constraint(model, [h=hour,m=month,y=year,s=station;h==1], model[:storage_reservoir][y,m,h,s] == storage_init[m, s] + 
        seconds_in_hour*(model[:totalinflow][y,m,h,s] - model[:outflow][y,m,h,s])* hydro_storage_unit)
    # totalflow = spill + gen
    @constraint(model, [h=hour,m=month,y=year,s=station], model[:outflow][y,m,h,s] == model[:genflow][y,m,h,s] + model[:spillflow][y,m,h,s]) 
    
end