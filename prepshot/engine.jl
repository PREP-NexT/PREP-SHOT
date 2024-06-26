module prepshot

using JuMP

include("constraints/cost.jl")
include("constraints/hydro_output.jl")
include("constraints/hydro_bounds.jl")
include("constraints/water_balance.jl")
include("constraints/hydrolic_connect.jl")
# include("constraints/demand_side_management.jl")
include("constraints/ramping_limits.jl")
include("constraints/storage_limits.jl")
include("constraints/gen_limits.jl")
include("constraints/existing_tech.jl")
include("constraints/carbon_limits.jl")
include("constraints/demand_balance.jl")
include("constraints/existing_line.jl")
include("constraints/transmission_limits.jl")
include("constraints/tech_install_bounds.jl")

# include("solver.jl")
# include("retrieve_results.jl")
include("model.jl")

end