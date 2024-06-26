function add_storage_limits!(model::Model, inputs::Dict)

    storage_tech = inputs["storage_tech"]
    hour = inputs["hour"]
    month = inputs["month"]
    year = inputs["year"]
    zone = inputs["zone"]
    efficiency_out = inputs["efficiency_out"]
    efficiency_in = inputs["efficiency_in"]
    init_storage_level = inputs["init_storage_level"]
    energy_power_ratio = inputs["energy_power_ratio"]

    @constraint(model, [h=hour,m=month,y=year,z=zone,e=storage_tech; h>1],
        model[:storage_energy][h,m,y,z,e] == model[:storage_energy][h-1,m,y,z,e]-model[:gen][h,m,y,z,e]/efficiency_out[e,y] + model[:charge][h,m,y,z,e] * efficiency_in[e,y])
    @constraint(model, [h=hour,m=month,y=year,z=zone,e=storage_tech; h==1],
        model[:storage_energy][h,m,y,z,e] == init_storage_level[e, z] *
                    model[:cap_existing][y,z,e] * energy_power_ratio[e] - model[:gen][h,m,y,z,e]/efficiency_out[e,y] + model[:charge][h,m,y,z,e] * efficiency_in[e,y])
    @constraint(model, [m=month,y=year,z=zone,e=storage_tech], model[:storage_energy][hour[end],m,y,z,e] == init_storage_level[e, z] *
                    model[:cap_existing][y,z,e] * energy_power_ratio[e])
    @constraint(model, [h=hour,m=month,y=year,z=zone,e=storage_tech], model[:storage_energy][h,m,y,z,e] <= model[:cap_existing][y,z,e] * energy_power_ratio[e])
    @constraint(model, [h=hour,m=month,y=year,z=zone,e=storage_tech;h>1], model[:gen][h,m,y,z,e]/efficiency_out[e,y] <= model[:storage_energy][h-1,m,y,z,e])
    @constraint(model, [h=hour,m=month,y=year,z=zone,e=storage_tech;h==1], model[:gen][h,m,y,z,e]/efficiency_out[e,y] <= init_storage_level[e, z] *
                    model[:cap_existing][y,z,e] * energy_power_ratio[e])
    return nothing
end