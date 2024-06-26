function add_ramping_limits!(model::Model, inputs::Dict)

    nondispatchable_tech = inputs["nondispatchable_tech"]
    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    zone = inputs["zone"]
    tech = inputs["tech"]
    dt = inputs["dt"]
    ramp_up = inputs["ramp_up"]
    ramp_down = inputs["ramp_down"]

    # Ramping
    @constraint(model, [h=hour,m=month,y=year,z=zone,e=tech; h>1 && e ∉ nondispatchable_tech && ramp_up[e]*dt < 1], model[:gen][h,m,y,z,e] - model[:gen][h-1,m,y,z,e] <= ramp_up[e] * dt * model[:cap_existing][y,z,e])
    @constraint(model, [h=hour,m=month,y=year,z=zone,e=tech; h>1 && e ∉ nondispatchable_tech && ramp_down[e]*dt < 1], model[:gen][h-1,m,y,z,e] - model[:gen][h,m,y,z,e] <= ramp_down[e]* dt * model[:cap_existing][y,z,e])
    return nothing
end
