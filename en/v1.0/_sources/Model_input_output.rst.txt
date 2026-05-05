.. _Model_input_output:

Model Inputs/Outputs
=====================

The model requires several input parameters, provided via input files. These parameters, their dimensions, and descriptions are as follows:

Inputs
------------------------

The parameters used, their desciptions, and their input file name in the model are as follows:

.. list-table:: Parameters
  :widths: 20 60 20
  :header-rows: 1

  * - Parameter [Unit]
    - Description
    - Input file [#]_ 

  * - historical capacity [#]_ 
  
      [MW]
    - The capacity of each technology in each zone for each year, taking into account the number of years that each technology has been in operation starting from the beginning of the planning period.
    - historical_capacity

  * - capacity factor [N/A]
    - Capacity factor of different non-dispatchable technologies.
    - capacity_factor
    
  * - carbon emission  
  
      limit [tCO2]
    - Carbon emission limit of different zones.
    - carbon_emission_limit
    
  * - emission factor 
  
      [tCO2/MWh]
    - Emission factor of different technologies.
    - emission_factor
    
  * - water delay time [N/A]
    - Water delay time of connection between reservoirs.
    - water_delay_time
    
  * - demand [MW]
    - Demand of different balancing authorities.
    - demand
    
  * - discount factor [N/A]
    - Discount factor for each year.
    - discount_factor
    
  * - distance [km]
    - Distance of different pair of zones.
    - distance
    
  * - discharge efficiency [N/A]
    - Discharge efficiency of storage technologies.
    - discharge\_
    
      efficiency
    
  * - charge efficiency [N/A]
    - Charge efficiency of storage technologies.
    - charge\_
      
      efficiency
    
  * - energy to 
  
      power ratio [MWh/MW]
    - Power to energy ratio ratio of storage technologies.
    - energy_to\_
    
      power_ratio
    
  * - fuel price [dollar/MWh]
    - Fuel price of different technologies.
    - fuel_price
    
  * - Predefined hydropower [#]_ [MW]
    - Predefined hydropower output of all reservoirs.
    - predefined_hydropower
    
  * - inflow [m3/s]
    - Inflow of all reservoirs.
    - inflow
    
  * - initial energy 
      
      storage level [1/MWh]
    - Initial energy storage level of different storage technologies.
    - initial_energy\_
    
      storage_level
    
  * - lifetime [yr]
    - Lifetime of different technologies.
    - lifetime
    
  * - new technology 
  
      lower bound [MW]
    - Lower bound of newly-built installed capacity of different technologies for each investment year.
    - new_technology\_
    
      lower_bound
    
  * - new technology 
  
      upper bound [MW]
    - Upper bound of newly-built installed capacity of different technologies for each investment year.
    - new_technology\_
      
      upper_bound
    
  * - ramp down [1/MW]
    - Ramp down rate of different technologies.
    - ramp_down
    
  * - ramp up [1/MW]
    - Ramp up rate of different technologies.
    - ramp_up
    
  * - reservoir characteristics 
  
      [As per data sheet]
    - Reservoir characteristics data includes designed water head, maximum storage, minimum storage, operational efficiency, area of affiliation, installed capacity, maximum power output, minimum power output, maximum outflow, minimum outflow, and maximum generation outflow.
    - reservoir\_
      
      characteristics

  * - reservoir storage
      
      upper bound [m3]
    - Upper bound of volume of hydropower reservoirs.
    - reservoir_storage
       
      _upper_bound

  * - reservoir storage 
  
      lower bound [m3]
    - Lower bound of volume of hydropower reservoirs.
    - reservoir_storage\_
      
      lower_bound
    
  * - final reservoir 
  
      storage level [m3]
    - Final volume of hydropower reservoirs.
    - final_reservoir\_
    
      storage_level
    
  * - initial reservoir 
  
      storage level [m3]
    - Initial volume of hydropower reservoirs.
    - initial_reservoir\_
      
      storage_level
    
  * - technology fixed OM cost 
  
      [dollar/MW/yr]
    - Fixed operation and maintenance cost of different technologies.
    - technology_fixed\_
    
      OM_cost

  * - technology variable 
      
      OM cost [dollar/MW/yr]
    - Variable operation and maintenance costs of different technologies.
    - technology_variable\_
    
      OM_cost
    
  * - technology investment
      
      cost [dollar/MW]
    - Investment cost of different technologies.
    - technology_investment
    
      _cost
    
  * - technology portfolio [MW]
    - Existing total installed capacity across all zones.
    - technology\_
    
      portfolio
    
  * - technology 
      
      upper bound [#]_ [MW]
    - Upper bound of installed capacity of different technologies.
    - technology_upper\_
    
      bound
    
  * - transmission line

      existing capacity 

      [MW]
    - Capacity of existing transmission lines (if there is no exising nor planned transmission lines between two specific zones, leave the data entries blank).
    - transmission_line\_
       
      existing_capacity   

  * - transmission line 
  
      efficiency [N/A]
    - Efficiency of transmission lines across all zones.
    - transmission_line\_
    
      efficiency

  * - transmission line 
      
      fixed OM cost 
      
      [dollar/MW/yr]
    - Fixed operation and maintenance costs of transmission lines.
    - transmission_line\_
       
      fixed_OM_cost
    
  * - transmission line 
  
      variable OM cost
  
      [dollar/MW/yr]
    - Variable operations and maintenance costs of transmission lines.
    - transmission_line
    
      _variable_cost
    
  * - transmission line

      investment cost 

      [dollar/MW/km]
    - Investment cost of transmission lines.
    - transmission_line\_
       
      investment_cost

  * - transmission line 
  
      lifetime [yr]
    - Lifetime of transmission lines.
    - transmission_line\_
    
      lifetime
    
  * - technology type [N/A]
    - Categories of different technologies.
    - technology_type
    
  * - reservoir tailrace 
  
      level-discharge function 
      
      [m & m3/s]
    - Relationship between tailrace level and total discharge for different reservoirs.
    - reservoir_tailrace\_
    
      level_discharge\_
      
      function
    
  * - reservoir forebay 
  
      level-volume function 
      
      [m & m3]
    - Relationship between forebay level and volume for different reservoirs
    - reservoir_forebay\_
    
      level_volume\_
      
      function

.. note:: 
  
  * `inf` refers to Infinity, indicating that there is no upper bound.
  * `None` refers to a null value for current item.

Outputs
------------------
The output of the model is stored in a NetCDF file, please refer to this `simple tutorial <https://xiaoganghe.github.io/python-climate-visuals/chapters/data-analytics/xarray-basic.html>`_ and `official documentation <https://docs.xarray.dev/en/stable/>`_ of Xarray to understand how to manipulate NetCDF files.

The output file contains the following variables:

.. list-table:: Output Variables
  :widths: 30 70
  :header-rows: 1

  * - Variable name [Unit]
    - Description
  
  * - trans_import [MW]
    - The electrical power transmitted from Zone 1 and effectively received by Zone 2 through the transmission line, after adjusting for transmission losses.

  * - trans_export [MW]
    - The electrical power initially sent out by Zone 1 for transmission to Zone 2 via the transmission line, before adjusting for any transmission and distribution losses during its journey to Zone 2.

  * - gen [MW]
    - Power output of different technologies during user-defined time interval.

  * - install [MW]
    - Existing installed capacity of different technologies.

  * - carbon [Ton]
    - Carbon emissions across different years.

  * - charge [MW]
    - Charged electricity of different storage technologies.

  * - cost [dollar]
    - Total cost (including total investment cost, total variable OM cost, and total fixed OM cost) over the planning period.

  * - cost_breakdown [dollar]
    - Breakdown of total cost (including total investment cost, total variable OM cost, and total fixed OM cost) over the planning period, by zone, year, and technology.

  * - cost_var [dollar]
    - Total variable OM cost (including technology variable OM cost, transmission line variable OM cost, and fuel cost) over the planning period.

  * - cost_var_breakdown [dollar]
    - Breakdown of total variable OM cost (including technology variable OM cost, transmission line variable OM cost, and fuel cost) over the planning period, by zone, year, and technology.

  * - cost_fix [dollar]
    - Total fixed OM cost (including technology fixed OM cost, transmission line fixed OM cost) over the planning period.

  * - cost_fix_breakdown [dollar]
    - Breakdown of total fixed OM cost (including technology fixed OM cost, transmission line fixed OM cost) over the planning period, by zone, year, and technology.

  * - cost_newtech [dollar]
    - Total investment cost of technologies over the planning period.

  * - cost_newtech_breakdown [dollar]
    - Breakdown of total investment cost of technologies over the planning period, by zone, year, and technology.

  * - cost_newline [dollar]
    - Investment cost of transmission lines over the planning period.

  * - cost_newline_breakdown [dollar]
    - Breakdown of total investment cost of transmission lines over the planning period, by zone, year, and technology.

  * - income [dollar]
    - Saved cost due to abstracted water resources over the planning period.

  * - genflow [m3/s]
    - Generated water flow of different reservoirs.

  * - spillflow [m3/s]
    - Spilled water flow of different reservoirs.

Execute various scenarios
-------------------------
By employing command-line parameters, you can execute different scenarios using the model. For example, if you wish to run a scenario referred to as "low demand," you can prepare input data named ``demand_low.xlsx``. Subsequently, when running the model, you can utilize command-line parameters to specify the scenario value. For instance, you can execute the model by executing the command ``python run.py --demand=low``. 

Setting global parameters
--------------------------

This section will guide you on how to tune the PREP-SHOT model parameters to compute the energy system for your needs. After you have prepared your input data based on the previous sections, you can proceed to tune the model parameters before you run it.

Within the root directory of the model, you will find a JSON file containing the parameters that you can tune for the model, named ``config.json``. This file contains the following parameters:

.. list-table::
   :widths: 30 70
   :header-rows: 1
   :align: left

   * - Model Parameter
     - Description

   * - input_folder
     - Specifies the name of the folder containing the input data.

   * - output_filename
     - Specifies the name of the output file.

   * - hour
     - Specifies the number of hours in each time period.

   * - month
     - Specifies the number of months in each time period.

   * - dt
     - Specifies the timestep for the simulation in hours.

   * - hours_in_year
     - Specifies the number of hours in a year. Typically, this is set to 8760.

   * - isinflow
     - Specifies whether to include inflow in the optimization problem. It can be used by assigning `isinflow` = `true` or `false`. 

   * - error_threshold
     - Specifies the error threshold for the model, while iterating for a solution. This parameter controls the convergence of the hydro model.

   * - iteration_number
     - Specifies the maximum number of iterations for the hydro model, while iterating for a solution.

   * - solver
     - Specifies the solver to be used for the optimization problem.

   * - solver_path
     - Specifies the path of the dynamic library of solver. This is required while automatic detection of the installation directory of the solver fails. Please provide refer to `PyOptInterface documentation <https://metab0t.github.io/PyOptInterface/getting_started.html#setup-of-optimizers>`_.

   * - **solver_parameters**
     - Specifies the solver-specific parameters for `mosek <https://docs.mosek.com/latest/capi/parameters.html>`_, `gurobi <https://www.gurobi.com/documentation/11.0/refman/parameters.html>`_, `highs <https://ergo-code.github.io/HiGHS/dev/options/definitions/>`_, and `copt <https://guide.coap.online/copt/en-doc/parameter.html>`_.

After you have tuned the parameters, you can run the model by following the steps in the :ref:`installation` page.

You can also try out the model with the sample data provided in the ``input`` folder. Refer to the :ref:`Model_input_output` page for a walkthrough of this example, inspried by real-world data.

.. rubric:: Footnotes
.. [#] The input files format is ``.xlsx``.
.. [#] For instance, assuming the planning period spans from 2020 to 2050, with 2020 being the starting point, let's consider a technology that has been in operation since 2019. In this case, 2020 would mark its 2nd year of operation within the planning period. These inputs are useful for modelling the retirement of existing technologies.
.. [#] To model the simplified hydropower operation.
.. [#] To model the potential of technologies with land, fuel, and water constraints.

