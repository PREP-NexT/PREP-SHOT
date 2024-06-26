function add_existing_line!(model::Model, inputs::Dict)
    year = inputs["year"]
    transline = inputs["transline"]
    transmission_line_lifetime = inputs["transmission_line_lifetime"]
    y_min = inputs["y_min"]
    for (y,iy) in zip(year, 1:length(year))
        # for z in keys(transline)
            # for z1 in keys(transline[z])
        for (z,z1) in keys(transline)
            remaining_time = transmission_line_lifetime[z,z1] - (y - y_min)
            if  remaining_time <= 1
                remaining_technology = 0
            else
                remaining_technology = transline[z,z1]
            end
            # 2. The remaining in-service installed capacity from the initial technology
        @constraint(model, model[:cap_lines_existing][y, z, z1] == remaining_technology + sum(model[:cap_newline][yy, z, z1] for yy in year[1:iy]  if y - yy < transmission_line_lifetime[z, z1]))
            # end
        end
    end

    return nothing
end