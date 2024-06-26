function add_gen_limits!(model::Model, inputs::Dict)
    capacity_factor = inputs["capacity_factor"]
    dt = inputs["dt"]
    nondispatchable_tech = inputs["nondispatchable_tech"]
    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    zone = inputs["zone"]
    tech = inputs["tech"]

    @constraint(model, [h=hour,m=month,y=year,z=zone,e=tech; e ∉ nondispatchable_tech], model[:gen][h,m,y,z,e] <= model[:cap_existing][y,z,e] * dt)
    if length(nondispatchable_tech) > 0
        @constraint(model, [m=month,h=hour,y=year,z=zone,e=nondispatchable_tech], model[:gen][h,m,y,z,e] <= capacity_factor[e, z, y, m, h] * model[:cap_existing][y,z,e] * dt)
    end
    return nothing
end


