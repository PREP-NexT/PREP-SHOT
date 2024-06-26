@doc raw"""


"""
function add_demand_balance!(model::Model, inputs::Dict)
  
    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    zone = inputs["zone"]
    transline = inputs["transline"]
    demand = inputs["demand"]
    dt = inputs["dt"]
    tech = inputs["tech"]
    storage_tech = inputs["storage_tech"]
    @constraint(model, [h=hour,m=month,y=year,z=zone],     
		(demand[z,y,m,h]  - model[:current_defer_demand][h,m,y,z] + model[:serve_demand][h, m, y, z]) * dt == 
		sum(model[:trans_import][h, m, y, z1, z] for (z1, z2) in keys(transline) if z==z2) - 
		sum(model[:trans_export][h, m, y, z, z1] for (z2, z1) in keys(transline) if z==z2) + 
		sum(model[:gen][h,m,y,z,e] for e in tech) - 
		sum(model[:charge][h,m,y,z,e] for e in storage_tech))
    return nothing
end