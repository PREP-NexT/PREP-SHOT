@doc raw"""
The constraint is created to ensure that the total carbon emissions from the carbon-emission technology do not exceed the specified carbon limit. 
The function also checks whether there are any years with carbon limits specified and only adds the constraint to the model if there are any such years. 
The function does not return anything, it only adds the constraints of model.
"""
function add_carbon_limits!(model::Model, inputs::Dict)
    
    # Retrieve the relevant inputs from the dictionary
    year = inputs["year"]
    hour = inputs["hour"]
    month = inputs["month"]
    zone = inputs["zone"]
    tech = inputs["tech"]
    carbon = inputs["carbon"]
    carbon_content = inputs["carbon_content"]
    # Create a list of years that have a carbon limit specified
    carbon_limit_year = [y for y in year if carbon[y]!="inf"]
    # If there are years with carbon limits, add the carbon limit constraint to the model
    if length(carbon_limit_year) > 0
	    @constraint(model, [y=carbon_limit_year], sum(carbon_content[e,y] * model[:gen][h,m,y,z,e] 
                for (h,m,z,e) in Iterators.product(hour, month, zone, tech)) <= carbon[y])
    end
    # Return nothing
    return nothing 
end
