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

  * - age 
    - The capacity of each technology in each BA for each year, taking into account the number of years that each technology has been in operation starting from the beginning of the planning period. For instance, assuming the planning period spans from 2020 to 2050, with 2020 being the starting point, let's consider a technology that has been in operation since 2019. In this case, 2020 would mark its 2nd year of operation within the planning period. 
    - These inputs are useful for modelling the retirement of existing technologies.

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
    
  * - efficiency in
    - Discharge efficiency of storage technologies.
    - To calculate charge and discharge loss of energy storage.
    
  * - efficiency out
    - Charge efficiency of storage technologies.
    - To calculate charge and discharge loss of energy storage.
    
  * - energy power ratio
    - Energy to power ratio of storage technologies.
    - To measure duration of energy storage.
    
  * - fuel price
    - Fuel price of different technologies.
    - To calculate system cost.
    
  * - hydropower
    - Predefined hydropower output of all reservoirs.
    - To model the simplified hydropower operation.
    
  * - inflow
    - Inflow of all reservoirs.
    - To model the simplified hydropower operation.
    
  * - init storage level
    - Initial storage level of different storage technologies.
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
    
  * - static
    - Static data of all reservoirs includes designed water head, maximum storage, minimum storage, operational efficiency, area of affiliation, installed capacity, maximum power output, minimum power output, maximum outflow, minimum outflow, and maximum generation outflow.
    - To model operation constraints of reservoir and hydropower output.
    
  * - storage low bound
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
    
  * - technology variable cost
    - Variable operation and maintenance costs of different technologies.
    - To calculate the system cost.
    
  * - transline
    - Investment cost of transmission lines.
    - To calculate the system cost.
    
  * - transline efficiency
    - Efficiency of transmission lines across all zones.
    - To calculate the transmission loss.
    
  * - transline fix cost
    - Fixed operation and maintenance costs of different technologies.
    - To calculate the system cost.
    
  * - transline investment cost
    - Investment cost of transmission lines.
    - To calculate the system cost.
    
  * - transline variable cost
    - Variable operations and maintenance costs of transmission lines.
    - To calculate the system cost.
    
  * - transline line lifetime
    - Lifetime of transmission lines.
    - To calculate the retirement of transmission lines.
    
  * - type
    - Categories of different technologies.
    - To specify ways of modelling different technologies.
    
  * - zq
    - Relationship between tailrace elevation and total discharge for different reservoirs.
    - To calculate tailrace elevation based on the reservoir's discharge.
    
  * - zv
    - Relationship between forebay elevation and volume for different reservoirs
    - To calculate forebay elevation based on the reservoir's volume.

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

   * - ``USD``
     - US Dollar

   * - ``RMB``
     - Chinese Yuan

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

   * - ``10^8 m^3``
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

  * - age 
    - 3D (zone, year, technology)
    - ``MW``
    - ``age.xlsx``

  * - capacity factor
    - 5D (technology, zone, year, month, hour)
    - N/A
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
    - N/A
    - ``connect.xlsx``
    
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
    - N/A
    - ``distance.xlsx``
    
  * - efficiency In
    - 2D (year, storage technology)
    - N/A
    - ``efficiency_in.xlsx``
    
  * - efficiency Out
    - 2D (year, storage technology)
    - N/A
    - ``efficiency_out.xlsx``
    
  * - energy power ratio
    - 1D (storage technology)
    - ``hr``
    - ``energy_power_ratio.xlsx``
    
  * - fuel price
    - 2D (year, technology)
    - ``USD/MWh``
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
    
  * - static
    - 1D (station)
    - N/A
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
    - ``USD/MW``
    - ``technology_fix_cost.xlsx``
    
  * - technology investment cost
    - 2D (year, technology)
    - ``USD/MW-km``
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
    - ``USD/MWh``
    - ``technology_variable_cost.xlsx``
    
  * - transline
    - 2D (zone1, zone2)
    - ``USD/MW-km``
    - ``transline.xlsx``
    
  * - transline efficiency
    - 2D (zone1, zone2)
    - N/A
    - ``transline_efficiency.xlsx``
    
  * - transline fix cost
    - 2D (zone1, zone2)
    - ``USD/MW``
    - ``transline_fix_cost.xlsx``
    
  * - transline investment cost
    - 2D (zone1, zone2)
    - ``RMB/MW-km``
    - ``transline_investment_cost.xlsx``
    
  * - transline variable cost
    - 2D (zone1, zone2)
    - ``USD/MWh``
    - ``transline_variable_cost.xlsx``
    
  * - transline line lifetime
    - 2D (zone1, zone2)
    - ``yr``
    - ``transline_line_lifetime.xlsx``
    
  * - type
    - 1D (technology)
    - N/A
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
