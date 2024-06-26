@doc raw"""
	add_remain_cap!(model::Model, inputs::Dict)
This function adds the constraints to calculate the existing capacity of all technologies in the each investment year.
```math
cap_{y, z, te}^{existing-tech} & = \sum_{lifetime-age<y-y_{min})}cap_{age,z,te}^{tech-init} + \sum_{(yy\le y) \& (lifetime>y-yy)}cap_{yy,z,te}^{tech-inv} \text{} \forall y,z,te 
```
"""
function add_existing_tech!(model::Model, inputs::Dict)
    year = inputs["year"]
    age = inputs["age"]
    tech = inputs["tech"]
    zone = inputs["zone"]
    lifetime = inputs["lifetime"]
    y_min = inputs["y_min"]
    for (y,iy) in zip(year, 1:length(year))
	for (e,z) in Iterators.product(tech, zone)
	    remaining_time = lifetime[e, y] - (y - y_min)
            if  remaining_time <= 1
                remaining_technology = 0
            else
		remaining_technology = sum(age[z, e, a] for a in 1:remaining_time-1)
            end
            # 2. The remaining in-service installed capacity from the initial technology
	    @constraint(model, model[:cap_existing][y,z,e] == remaining_technology + sum(model[:cap_newtech][yy, z, e] for yy in year[1:iy] if y - yy < lifetime[e, y]))
        end
    end
end