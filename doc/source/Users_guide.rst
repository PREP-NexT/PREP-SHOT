.. _Users_guide:

Users Guide
===========

The model requires several input parameters, provided via input files. These parameters, their dimensions, and descriptions are as follows:

Parameter Representation
------------------------

.. list-table:: Description of Input Parameters
  :widths: 5 45 50
  :header-rows: 1

  * - Parameter
    - Description
    - Purpose

  * - age 
    - Age of existing different technologies.
    - To model the retirement of existing power plants.

  * - capacity factor
    - Capacity factor of different non-dispatchable technologies.
    - To calculate the power output.
    
  * - carbon
    - Carbon emission limit of different balancing authorities
    - To model the policy of carbon emission reductions.
    
  * - carbon content
    - Carbon content of different technologies.
    - To calculate the system cost.
    
  * - connect
    - Water delay time of connection between reservoirs.
    - To model the cascade hydrolic connection.
    
  * - demand
    - Demand of different balancing authorities.
    - To calculate the power balance.
    
  * - discount Factor
    - Discount factor for each year.
    - To calculate the present value of cost.
    
  * - distance
    - Distance of different pair of zones.
    - To calculate the transmission investment cost.
    
  * - efficiency In
    - Discharge efficiency of storage technologies.
    - To calculate charge and discharge loss of energy storage.
    
  * - efficiency Out
    - Charge efficiency of storage technologies.
    - To calculate charge and discharge loss of energy storage.
    
  * - energy power ratio
    - Energy to power ratio of storage technologies.
    - To measure duration of energy storage.
    
  * - fuel price
    - Fuel price of different technologies.
    - To calculate system cost.
    
  * - hydropower
    - Predifined hydropower output of all reservoirs.
    - To model the simplified hydropower operation.
    
  * - inflow
    - Inflow of all reservoirs.
    - To model the simplified hydropower operation.
    
  * - init storage level
    - Initial storage level of different storage technologies.
    - To modelling the initial storage level of energy storage.
    
  * - lifetime
    - Lifetime of different technologies.
    - To calculate the retirement of power plant.
    
  * - new technology lower bound
    - Lower bound of newly-built installed capacity of different technologies for each investment year.
    - To model the limits of technologies constrainted by policy.
    
  * - new technology upper bound
    - Upper bound of newly-built installed capacity of different technologies for each investment year.
    - To model the limits of technologies constrainted by policy.
    
  * - ramp down
    - Ramp down rate of different technologies.
    - To limit the fluctuation of power outputs.
    
  * - ramp up
    - Ramp up rate of different technologies.
    - To limit the fluctuation of power outputs.
    
  * - static
    - Static data of all reservoirs.
    - xxx
    
  * - storage lowbound
    - Lower bound of volume of hydropower reservoirs.
    - To model the operational rule of hydropower reservoirs.
    
  * - storage end
    - Final volume of hydropower reservoirs.
    - To model the operational rule of hydropower reservoirs.
    
  * - initial storage
    - Initial volume of hydropower reservoirs.
    - To model the operational rule of hydropower reservoirs.
    
  * - storage upbound
    - Upper bound of volume of hydropower reservoirs.
    - To model the operation rule of hydropower reservoirs.
    
  * - technology fix cost
    - Fixed operation and maintaince cost of different technologies.
    - To calculate the system cost.
    
  * - technology investment cost
    - Investment cost of different technologies.
    - To calculate the system cost.
    
  * - technology portfolio
    - Existing total installed capacity across all zones.
    - xxx
    
  * - technology upper bound
    - Upper bound of installed capacity of different technologies.
    - To model the potential of technologies with land, fuel, and water constraints.
    
  * - technology variable cost
    - Variable operation and maintaince cost of different technologies.
    - To calculate the system cost.
    
  * - transline
    - Investment cost of transmission lines.
    - To calculate the system cost.
    
  * - transline efficiency
    - Efficiency of transmission lines across all zones.
    - To calculate the transmission loss.
    
  * - transline fix cost
    - Fixed operation and maintaince cost of different technologies.
    - To calculate the system cost.
    
  * - transline investment cost
    - Investment cost of transmission lines.
    - To calculate the system cost.
    
  * - transline variable cost
    - Variable operations and maintenance cost of transmission lines.
    - To calculate the system cost.
    
  * - transline line lifetime
    - Lifetime of transmission lines.
    - To calculate the retirement of transmission lines.
    
  * - type
    - Catelogies of different technologies.
    - To specify ways of modelling different technologies.
    
  * - zq
    - Relationship between tailrace elevation and total discharge for different reservoirs.
    - To calculate tailrace elevation based on the reservoir's discharge.
    
  * - zv
    - Relationship between forebay elevation and volume for different reservoirs
    - To calculate forebay elevation based on the reservoir's volume.

Preparing Inputs
----------------

.. list-table:: Input Parameters and Corresponding Files
  :widths: 5 35 30 30
  :header-rows: 1

  * - Parameter
    - Dimension
    - Unit
    - File

  * - age 
    - 3D (zone, year, technology)
    - ``MW``
    - ``age.xlsx``

  * - capacity factor
    - 5D (technology, zone, year, month, hour)
    - NIL
    - ``capacity_factor.xlsx``
    
  * - carbon
    - 1D (year)
    - ``tCO2``
    - ``carbon.xlsx``
    
  * - carbon content
    - 2D (year, technology)
    - ``tCO2/MWh``
    - ``carbon_content.xlsx``
    
  * - connect
    - 2D (station, downstream station)
    - NIL
    - ``connect.xlsx``
    
  * - demand
    - 5D (technology, zone, year, month, hour)
    - ``MW``
    - ``demand.xlsx``
    
  * - discount Factor
    - 1D (year)
    - NIL
    - ``discount_factor.xlsx``
    
  * - distance
    - 2D (zone1, zone2)
    - NIL
    - ``distance.xlsx``
    
  * - efficiency In
    - 2D (year, storage technology)
    - NIL
    - ``efficiency_in.xlsx``
    
  * - efficiency Out
    - 2D (year, storage technology)
    - NIL
    - ``efficiency_out.xlsx``
    
  * - energy power ratio
    - 1D (storage technology)
    - ``h``
    - ``energy_power_ratio.xlsx``
    
  * - fuel price
    - 2D (year, technology)
    - ``$/MWh``
    - ``fuel_price.xlsx``
    
  * - hydropower
    - 4D (station, year, month, hour)
    - ``MW``
    - ``hydropower.xlsx``
    
  * - inflow
    - 4D (station, year, month, hour)
    - ``m^3/s``
    - ``inflow.xlsx``
    
  * - init storage level
    - 2D (zone, storage level)
    - ``1/MWh``
    - ``init_storage_level.xlsx``
    
  * - lifetime
    - 2D (year, technology)
    - ``year``
    - ``lifetime.xlsx``
    
  * - new technology lower bound
    - 2D (zone, technology)
    - ``MW``
    - ``new_technology_lower_bound.xlsx``
    
  * - new technology upper bound
    - 2D (zone, technology)
    - ``MW``
    - ``new_technology_upper_bound.xlsx``
    
  * - ramp down
    - 1D (technology)
    - ``1/MW``
    - ``ramp_down.xlsx``
    
  * - ramp up
    - 1D (technology)
    - ``1/MW``
    - ``ramp_up.xlsx``
    
  * - static
    - 1D (station)
    - NIL
    - ``static.xlsx``
    
  * - storage lowbound
    - 3D (station, month, hour)
    - ``10^8 m^3``
    - ``storage_lowbound.xlsx``
    
  * - storage end
    - 2D (station, month)
    - ``10^8 m^3``
    - ``storage_end.xlsx``
    
  * - initial storage
    - 2D (station, month)
    - ``10^8 m^3``
    - ``storage_init.xlsx``
    
  * - storage upbound
    - 3D (station, month, hour)
    - ``10^8 m^3``
    - ``storage_upbound.xlsx``
    
  * - technology fix cost
    - 2D (year, technology)
    - ``$/MW``
    - ``technology_fix_cost.xlsx``
    
  * - technology investment cost
    - 2D (year, technology)
    - ``$/MW/km``
    - ``technology_investment_cost.xlsx``
    
  * - technology portfolio
    - 2D (year, zone)
    - ``MW``
    - ``technology_portfolio.xlsx``
    
  * - technology upper bound
    - 2D (zone, technology)
    - ``MW``
    - ``technology_upper_bound.xlsx``
    
  * - technology variable cost
    - 2D (year, technology)
    - ``$/MWh``
    - ``technology_variable_cost.xlsx``
    
  * - transline
    - 2D (zone1, zone2)
    - ``$/MW/km``
    - ``transline.xlsx``
    
  * - transline efficiency
    - 2D (zone1, zone2)
    - NIL
    - ``transline_efficiency.xlsx``
    
  * - transline fix cost
    - 2D (zone1, zone2)
    - ``$/MW``
    - ``transline_fix_cost.xlsx``
    
  * - transline investment cost
    - 2D (zone1, zone2)
    - ``$/MW/km``
    - ``transline_investment_cost.xlsx``
    
  * - transline variable cost
    - 2D (zone1, zone2)
    - ``$/MWh``
    - ``transline_variable_cost.xlsx``
    
  * - transline line lifetime
    - 2D (zone1, zone2)
    - ``year``
    - ``transline_line_lifetime.xlsx``
    
  * - type
    - 1D (technology)
    - NIL
    - ``type.xlsx``
    
  * - zq
    - 2D (station, break point)
    - ``m`` and ``m^3/s``
    - ``zq.xlsx``
    
  * - zv
    - 2D (station, break point)
    - ``m`` and ``10^8 m^3``
    - ``zv.xlsx``

.. note:: 
  
  * `inf` refers to Infinity, indicating that there is no upper bound.
  * `None` refers to a null value for current item.

Run model
----------------

Scenarios
####################

Here I want to talk about how to run PREP-SHOT with multiple-year inflow. First, you need to download scripts in `prepshot-my-flow` branch. Then you need to prepare an individual inflow input file called "input/scenario/inflow_xxx.xlsx". Here "xxx" is the name of the scenario, which need to be the same as the command line `inflow` parameter which will be introduced below. The required inflow input file takes the representative year as the name of the sheet table. For each sheet, you only need to maintain the same format as the `inflow` sheet in the previous total input file.   

After preparing the inflow input files, you must use the command line parameter to specify the scenario name. For example, you design an inflow called drought. You need to prepare an inflow input file called "inflow_drough.xlsx" and then run your scenario with the following shell command `python run.py -- inflow=drought`.

Read output
--------------
The output of the model is stored in a NetCDF file, please refer to the `simple tutorial <https://xiaoganghe.github.io/python-climate-visuals/chapters/data-analytics/xarray-basic.html>`_ and `official documentation <https://docs.xarray.dev/en/stable/>`_ of Xarray for how to manipulate the NetCDF file.

