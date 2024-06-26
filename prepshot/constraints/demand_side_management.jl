function add_demand_side_management!(model::Model, inputs::Dict)

    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    zone = inputs["zone"]
    demand = inputs["demand"]
    dsm_ratio = inputs["dsm_ratio"]
    dsm_duration = inputs["dsm_duration"]
    dt = inputs["dt"]
    
    # Demand side management
    # (DSM_balance)
    @constraint(model, [h=hour,m=month,y=year,z=zone; h>1],
            model[:accumu_defer_demand][h,m,y,z] == model[:accumu_defer_demand][h-1,m,y,z] - model[:serve_demand][h,m,y,z] + model[:current_defer_demand][h,m,y,z])
    @constraint(model, [h=hour,m=month,y=year,z=zone; h==1],
            model[:accumu_defer_demand][h,m,y,z] == 0 - model[:serve_demand][h,m,y,z] + model[:current_defer_demand][h,m,y,z])
    # (DSM_limits)
    @constraint(model, [h=hour,m=month,y=year,z=zone],
            model[:current_defer_demand][h,m,y,z] <= demand[z,y,m,h] * dt * dsm_ratio[z, y])
    # (dsm_duration)
    @constraint(model, [h=hour,m=month,y=year,z=zone],
        sum(h_next<=hour[end] ? model[:serve_demand][h_next,m,y,z] : 0 for h_next in h+1:h+dsm_duration[z, y]) >= model[:accumu_defer_demand][h,m,y,z])
        
    return nothing
end