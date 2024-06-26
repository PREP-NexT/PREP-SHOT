function add_transmission_limits!(model::Model, inputs::Dict)
    
    transline = inputs["transline"]
    year = inputs["year"]
    transline_efficiency = inputs["transline_efficiency"]
    dt = inputs["dt"]
    hour = inputs["hour"]
    month = inputs["month"]
    filter_tuple = []
    for (z,z1) in keys(transline)
        # for z1 in keys(transline[z])
        if (z,z1) ∉ filter_tuple
            @constraint(model, [y=year], model[:cap_newline][y, z, z1] == model[:cap_newline][y, z1, z])
                push!(filter_tuple,(z,z1))
                push!(filter_tuple,(z1,z))
        end
	    @constraint(model, [h=hour,m=month,y=year], transline_efficiency[z, z1] * model[:trans_export][h,m,y,z,z1] == model[:trans_import][h,m,y,z,z1])
	    @constraint(model, [h=hour,m=month,y=year], model[:trans_export][h,m,y,z,z1] <= model[:cap_lines_existing][y,z,z1] * dt)
        # end
    end

    return nothing
end
