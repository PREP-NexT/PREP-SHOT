function add_tech_install_bounds!(model::Model, inputs::Dict)
    year = inputs["year"]
    zone = inputs["zone"]
    tech = inputs["tech"]
    technology_upper_bound = inputs["technology_upper_bound"]
    new_technology_upper_bound = inputs["new_technology_upper_bound"]
    new_technology_lower_bound = inputs["new_technology_lower_bound"]
    @constraint(model, [y=year,z=zone,e=tech; technology_upper_bound[e,z]!=Inf], model[:cap_existing][y,z,e] <= technology_upper_bound[e,z])
    @constraint(model, [y=year,z=zone,e=tech; new_technology_upper_bound[e,z]!=Inf], model[:cap_newtech][y,z,e] <= new_technology_upper_bound[e,z])
    @constraint(model, [y=year,z=zone,e=tech; new_technology_lower_bound[e,z]!=Inf], model[:cap_newtech][y,z,e] >= new_technology_lower_bound[e,z])
    return nothing
end