.. _Users_guide:

Users Guide
===========

The model requires several input parameters, provided via input files. These parameters, their dimensions, and descriptions are as follows:

Parameter Representation
------------------------

The parameters used, their desciptions, and their purpose in the model are as follows:

.. list-table::
  :widths: 5 45 50
  :header-rows: 1

  * - Parameter
    - Description
    - Purpose

  * - historical capacity 
    - The capacity of each technology in each BA for each year, taking into account the number of years that each technology has been in operation starting from the beginning of the planning period. For instance, assuming the planning period spans from 2020 to 2050, with 2020 being the starting point, let's consider a technology that has been in operation since 2019. In this case, 2020 would mark its 2nd year of operation within the planning period. 
    - These inputs are useful for modelling the retirement of existing technologies.

  * - capacity factor
    - Capacity factor of different non-dispatchable technologies.
    - To calculate the power output.
    
  * - carbon emission limit
    - Carbon emission limit of different balancing authorities
    - To model the policy of carbon emission reductions.
    
  * - emission factor
    - Emission factor of different technologies.
    - To calculate the carbon emissions.
    
  * - water delay time
    - Water delay time of connection between reservoirs.
    - To model the cascade hydraulic connection.
    
  * - demand
    - Demand of different balancing authorities.
    - To calculate the power balance.
    
  * - discount factor
    - Discount factor for each year.
    - To calculate the present value of cost.
    
  * - distance
    - Distance of different pair of zones.
    - To calculate the transmission investment cost.
    
  * - discharge efficiency
    - Discharge efficiency of storage technologies.
    - To calculate charge and discharge loss of energy storage.
    
  * - charge efficiency
    - Charge efficiency of storage technologies.
    - To calculate charge and discharge loss of energy storage.
    
  * - power to energy ratio
    - Power to energy ratio ratio of storage technologies.
    - To measure duration of energy storage.
    
  * - fuel price
    - Fuel price of different technologies.
    - To calculate system cost.
    
  * - hydropower
    - Predefined hydropower output of all reservoirs.
    - To model the simplified hydropower operation.
    
  * - inflow
    - Inflow of all reservoirs.
    - To model the high-fidelity hydropower operation.
    
  * - initial energy storage level
    - Initial energy storage level of different storage technologies.
    - To model the initial storage level of energy storage.
    
  * - lifetime
    - Lifetime of different technologies.
    - To calculate the retirement of power plant.
    
  * - new technology lower bound
    - Lower bound of newly-built installed capacity of different technologies for each investment year.
    - To model the limits of technologies constrained by policy.
    
  * - new technology upper bound
    - Upper bound of newly-built installed capacity of different technologies for each investment year.
    - To model the limits of technologies constrained by policy.
    
  * - ramp down
    - Ramp down rate of different technologies.
    - To limit the fluctuation of power outputs.
    
  * - ramp up
    - Ramp up rate of different technologies.
    - To limit the fluctuation of power outputs.
    
  * - reservoir characteristics
    - Reservoir characteristics data includes designed water head, maximum storage, minimum storage, operational efficiency, area of affiliation, installed capacity, maximum power output, minimum power output, maximum outflow, minimum outflow, and maximum generation outflow.
    - To model operation constraints of reservoir and hydropower output.
    
  * - reservoir storage lower bound
    - Lower bound of volume of hydropower reservoirs.
    - To model the operational rule of hydropower reservoirs.
    
  * - final reservoir storage level
    - Final volume of hydropower reservoirs.
    - To model the operational rule of hydropower reservoirs.
    
  * - initial reservoir storage level
    - Initial volume of hydropower reservoirs.
    - To model the operational rule of hydropower reservoirs.
    
  * - reservoir storage upper bound
    - Upper bound of volume of hydropower reservoirs.
    - To model the operation rule of hydropower reservoirs.
    
  * - Investmented OM cost
    - Fixed operation and maintenance cost of different technologies.
    - To calculate the system cost.
    
  * - technology investment cost
    - Investment cost of different technologies.
    - To calculate the system cost.
    
  * - technology portfolio
    - Existing total installed capacity across all zones.
    - To model the status quo and retirement of technologies.
    
  * - technology upper bound
    - Upper bound of installed capacity of different technologies.
    - To model the potential of technologies with land, fuel, and water constraints.
    
  * - technology variable OM cost
    - Variable operation and maintenance costs of different technologies.
    - To calculate the system cost.
    
  * - transmission line investment cost
    - Investment cost of transmission lines (if there is no exising nor planned transmission lines between two specific zones, leave the data entries blank).
    - To calculate the system cost.
    
  * - transmission line efficiency
    - Efficiency of transmission lines across all zones.
    - To calculate the transmission loss.
    
  * - transmission line fixed OM cost
    - Fixed operation and maintenance costs of transmission lines.
    - To calculate the system cost.
    
  * - transmission line lifetime
    - Variable operations and maintenance costs of transmission lines.
    - To calculate the system cost.
    
  * - transmission line lifetime
    - Lifetime of transmission lines.
    - To calculate the retirement of transmission lines.
    
  * - technology type
    - Categories of different technologies.
    - To specify ways of modelling different technologies.
    
  * - reservoir tailrace level-discharge function
    - Relationship between tailrace level and total discharge for different reservoirs.
    - To calculate tailrace level based on the reservoir's discharge.
    
  * - reservoir forebay level-volume function
    - Relationship between forebay level and volume for different reservoirs
    - To calculate forebay level based on the reservoir's volume.

Preparing Inputs
----------------

The description of the units used on this page is as follows:

.. list-table::
   :widths: 10 50
   :header-rows: 1
   :align: left

   * - Unit
     - Description

   * - ``s``
     - Second

   * - ``hr``
     - Hour

   * - ``yr``
     - Year

   * - ``MW``
     - Megawatt

   * - ``MWh``
     - Megawatt-hour

   * - ``MW-km``
     - Megawatt-kilometer

   * - ``tCO2``
     - Tonnes of Carbon Dioxide

   * - ``m``
     - Meter

   * - ``m^3``
     - Cubic meter

   * - ``m^3``
     - 100 million cubic meter

   * - N/A
     - Not Applicable

The input files required for each parameter, and their corresponding dimensions and units are as follows:

.. list-table::
  :widths: 5 35 30 30
  :header-rows: 1

  * - Parameter
    - Dimension
    - Unit
    - File

  * - historical capacity 
    - 3D (zone, year, technology)
    - ``MW``
    - ``historical_capacity.xlsx``

  * - capacity factor
    - 5D (technology, zone, year, month, hour)
    - N/A
    - ``capacity_factor.xlsx``
    
  * - carbon emission limit
    - 1D (year)
    - ``tCO2``
    - ``carbon_emission_limit.xlsx``
    
  * - emission factor
    - 2D (year, technology)
    - ``tCO2/MWh``
    - ``carbon_content.xlsx``
    
  * - demand
    - 5D (technology, zone, year, month, hour)
    - ``MW``
    - ``demand.xlsx``
    
  * - discount Factor
    - 1D (year)
    - N/A
    - ``discount_factor.xlsx``
    
  * - distance
    - 2D (zone1, zone2)
    - ``km``
    - ``distance.xlsx``
    
  * - discharge efficiency
    - 2D (year, storage technology)
    - N/A
    - ``discharge_efficiency.xlsx``
    
  * - charge efficiency
    - 2D (year, storage technology)
    - N/A
    - ``charge_efficiency.xlsx``
    
  * - power to energy ratio
    - 1D (storage technology)
    - ``MW/MWh``
    - ``power_to_energy_ratio.xlsx``
    
  * - fuel price
    - 2D (year, technology)
    - ``dollar/MWh``
    - ``fuel_price.xlsx``
    
  * - hydropower
    - 4D (station, year, month, hour)
    - ``MW``
    - ``hydropower.xlsx``
    
  * - inflow
    - 4D (station, year, month, hour)
    - ``m^3/s``
    - ``inflow.xlsx``
    
  * - initial energy storage level
    - 2D (zone, storage level)
    - ``1/MWh``
    - ``initial_energy_storage_level.xlsx``
    
  * - lifetime
    - 2D (year, technology)
    - ``yr``
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
    
  * - reservoir_characteristics
    - 1D (station)
    - As per data sheet
    - ``reservoir_characteristics.xlsx``
    
  * - reservoir storage lower bound
    - 3D (station, month, hour)
    - ``m^3``
    - ``reservoir_storage_lower_bound.xlsx``
    
  * - final reservoir storage level
    - 2D (station, month)
    - ``m^3``
    - ``final_reservoir_storage_level.xlsx``
    
  * - initial reservoir storage level
    - 2D (station, month)
    - ``m^3``
    - ``initial_reservoir_storage_level.xlsx``
    
  * - reservoir storage upper bound
    - 3D (station, month, hour)
    - ``m^3``
    - ``reservoir_storage_upper_bound.xlsx``
    
  * - Investmented OM cost
    - 2D (year, technology)
    - ``dollar/MW-yr``
    - ``technology_fixed_OM_cost.xlsx``
    
  * - technology investment cost
    - 2D (year, technology)
    - ``dollar/MW``
    - ``technology_investment_cost.xlsx``
    
  * - technology portfolio
    - 2D (year, zone)
    - ``MW``
    - ``technology_portfolio.xlsx``
    
  * - technology upper bound
    - 2D (zone, technology)
    - ``MW``
    - ``technology_upper_bound.xlsx``
    
  * - technology variable OM cost
    - 2D (year, technology)
    - ``dollar/MWh``
    - ``technology_variable_OM_cost.xlsx``
    
  * - transmission line investment cost
    - 2D (zone1, zone2)
    - ``dollar/MW-km``
    - ``transmission_line_investment_cost.xlsx``
    
  * - transmission line efficiency
    - 2D (zone1, zone2)
    - N/A
    - ``transmission_line_efficiency.xlsx``
    
  * - transmission line fixed OM cost
    - 2D (zone1, zone2)
    - ``dollar/MW``
    - ``transmission_line_fixed_OM_cost.xlsx``
    
  * - transmission line lifetime
    - 2D (zone1, zone2)
    - ``dollar/MWh``
    - ``transmission_line_variable_cost.xlsx``
    
  * - transmission line lifetime
    - 2D (zone1, zone2)
    - ``yr``
    - ``transmission_line_lifetime.xlsx``
    
  * - technology type
    - 1D (technology)
    - N/A
    - ``technology_type.xlsx``
    
  * - reservoir tailrace level-discharge function 
    - 2D (station, breakpoint)
    - ``m`` and ``m^3/s``
    - ``reservoir_tailrace_level_discharge_function.xlsx``
    
  * - reservoir forebay level-volume function
    - 2D (station, breakpoint)
    - ``m`` and ``m^3``
    - ``reservoir_forebay_level_volume_function.xlsx``

.. note:: 
  
  * `inf` refers to Infinity, indicating that there is no upper bound.
  * `None` refers to a null value for current item.

Execute various scenarios
-------------------------
By employing command-line parameters, you can execute different scenarios using the model. For example, if you wish to run a scenario referred to as "low demand," you can prepare input data named ``demand_low.xlsx``. Subsequently, when running the model, you can utilize command-line parameters to specify the scenario value. For instance, you can execute the model by executing the command ``python run.py --demand=low``. 

Tuning Model Parameters
-----------------------

This section will guide you on how to tune the PREP-SHOT model parameters to compute the energy system for your needs. After you have prepared your input data based on the previous sections, you can proceed to tune the model parameters before you run it.

Within the root directory of the model, you will find a JSON file containing the parameters that you can tune for the model, named ``config.json``. This file contains the following parameters:

.. list-table::
   :widths: 10 50
   :header-rows: 1
   :align: left

   * - Model Parameter
     - Description

   * - ``input_folder``
     - Specifies the name of the folder containing the input data.

   * - ``output_filename``
     - Specifies the name of the output file.

   * - ``hour``
     - Specifies the number of hours in each time period.

   * - ``month``
     - Specifies the number of months in each time period.

   * - ``dt``
     - Specifies the timestep for the simulation in hours.

   * - ``hours_in_year``
     - Specifies the number of hours in a year. Typically, this is set to 8760.

   * - ``ishydro``
     - Specifies whether to include hydropower in the optimization problem.

   * - ``error_threshold``
     - Specifies the error threshold for the model, while iterating for a solution. This parameter controls the convergence of the hydro model.

   * - ``iteration_number``
     - Specifies the maximum number of iterations for the hydro model, while iterating for a solution.

   * - ``solver``
     - Specifies the solver to be used for the optimization problem.

   * - ``timelimit``
     - Specifies the maximum time limit for the solver to solve the optimization problem in seconds.

After you have tuned the parameters, you can run the model by following the steps in the :ref:`installation` page.

You can also try out the model with the sample data provided in the ``input`` folder. Refer to the :ref:`Tutorial` page for a walkthrough of this example, inspried by real-world data.

Reading the Output
------------------
The output of the model is stored in a NetCDF file, please refer to this `simple tutorial <https://xiaoganghe.github.io/python-climate-visuals/chapters/data-analytics/xarray-basic.html>`_ and `official documentation <https://docs.xarray.dev/en/stable/>`_ of Xarray to understand how to manipulate NetCDF files.
