.. _Model_input_output:

Model Inputs/Outputs
=====================

The model requires several input parameters, provided via input files. These parameters, their dimensions, and descriptions are as follows:

Parameter Representation
------------------------

The parameters used, their desciptions, and their input file name in the model are as follows:

.. list-table::
  :widths: 25 50 25
  :header-rows: 1

  * - Parameter [Unit]
    - Description
    - Input file

  * - historical capacity [#]_ [``MW``]
    - The capacity of each technology in each zone for each year, taking into account the number of years that each technology has been in operation starting from the beginning of the planning period.
    - ``historical_capacity.xlsx``

  * - capacity factor [N/A]
    - Capacity factor of different non-dispatchable technologies.
    - ``capacity_factor.xlsx``
    
  * - carbon emission limit [``tCO2``]
    - Carbon emission limit of different zones.
    - ``carbon_emission_limit.xlsx``
    
  * - emission factor [``tCO2/MWh``]
    - Emission factor of different technologies.
    - ``carbon_content.xlsx``
    
  * - water delay time [N/A]
    - Water delay time of connection between reservoirs.
    - ``water_delay_time.xlsx``
    
  * - demand [``MW``]
    - Demand of different balancing authorities.
    - ``demand.xlsx``
    
  * - discount factor [N/A]
    - Discount factor for each year.
    - ``discount_factor.xlsx``
    
  * - distance [``km``]
    - Distance of different pair of zones.
    - ``distance.xlsx``
    
  * - discharge efficiency [N/A]
    - Discharge efficiency of storage technologies.
    - ``discharge_efficiency.xlsx``
    
  * - charge efficiency [N/A]
    - Charge efficiency of storage technologies.
    - ``charge_efficiency.xlsx``
    
  * - power to energy ratio [``MW/MWh``]
    - Power to energy ratio ratio of storage technologies.
    - ``power_to_energy_ratio.xlsx``
    
  * - fuel price [``dollar/MWh``]
    - Fuel price of different technologies.
    - ``fuel_price.xlsx``
    
  * - hydropower [#]_ [``MW``]
    - Predefined hydropower output of all reservoirs.
    - ``hydropower.xlsx``
    
  * - inflow [``m^3/s``]
    - Inflow of all reservoirs.
    - ``inflow.xlsx``
    
  * - initial energy storage level [``1/MWh``]
    - Initial energy storage level of different storage technologies.
    - ``initial_energy_storage_level.xlsx``
    
  * - lifetime [``yr``]
    - Lifetime of different technologies.
    - ``lifetime.xlsx``
    
  * - new technology lower bound [``MW``]
    - Lower bound of newly-built installed capacity of different technologies for each investment year.
    - ``new_technology_lower_bound.xlsx``
    
  * - new technology upper bound [``MW``]
    - Upper bound of newly-built installed capacity of different technologies for each investment year.
    - ``new_technology_upper_bound.xlsx``
    
  * - ramp down [``1/MW``]
    - Ramp down rate of different technologies.
    - ``ramp_down.xlsx``
    
  * - ramp up [``1/MW``]
    - Ramp up rate of different technologies.
    - ``ramp_up.xlsx``
    
  * - reservoir characteristics [As per data sheet]
    - Reservoir characteristics data includes designed water head, maximum storage, minimum storage, operational efficiency, area of affiliation, installed capacity, maximum power output, minimum power output, maximum outflow, minimum outflow, and maximum generation outflow.
    - ``reservoir_characteristics.xlsx``
    
  * - reservoir storage lower bound [``m^3``]
    - Lower bound of volume of hydropower reservoirs.
    - ``reservoir_storage_lower_bound.xlsx``
    
  * - final reservoir storage level [``m^3``]
    - Final volume of hydropower reservoirs.
    - ``final_reservoir_storage_level.xlsx``
    
  * - initial reservoir storage level [``m^3``]
    - Initial volume of hydropower reservoirs.
    - ``initial_reservoir_storage_level.xlsx``
    
  * - reservoir storage upper bound [``m^3``]
    - Upper bound of volume of hydropower reservoirs.
    - ``reservoir_storage_upper_bound.xlsx``
    
  * - Investmented OM cost [``dollar/MW-yr``]
    - Fixed operation and maintenance cost of different technologies.
    - ``technology_fixed_OM_cost.xlsx``
    
  * - technology investment cost [``dollar/MW``]
    - Investment cost of different technologies.
    - ``technology_investment_cost.xlsx``
    
  * - technology portfolio [``MW``]
    - Existing total installed capacity across all zones.
    - ``technology_portfolio.xlsx``
    
  * - technology upper bound [#]_ [``MW``]
    - Upper bound of installed capacity of different technologies.
    - ``technology_upper_bound.xlsx``
    
  * - technology variable OM cost [``dollar/MWh``]
    - Variable operation and maintenance costs of different technologies.
    - ``technology_variable_OM_cost.xlsx``
    
  * - transmission line investment cost [``dollar/MW-km``]
    - Investment cost of transmission lines (if there is no exising nor planned transmission lines between two specific zones, leave the data entries blank).
    - ``transmission_line_investment_cost.xlsx``
    
  * - transmission line efficiency [N/A]
    - Efficiency of transmission lines across all zones.
    - ``transmission_line_efficiency.xlsx``
    
  * - transmission line fixed OM cost [``dollar/MW``]
    - Fixed operation and maintenance costs of transmission lines.
    - ``transmission_line_fixed_OM_cost.xlsx``
    
  * - transmission line variable OM cost [``dollar/MWh``]
    - Variable operations and maintenance costs of transmission lines.
    - ``transmission_line_variable_cost.xlsx``
    
  * - transmission line lifetime [``yr``]
    - Lifetime of transmission lines.
    - ``transmission_line_lifetime.xlsx``
    
  * - technology type [N/A]
    - Categories of different technologies.
    - ``technology_type.xlsx``
    
  * - reservoir tailrace level-discharge function [``m`` and ``m^3/s``]
    - Relationship between tailrace level and total discharge for different reservoirs.
    - ``reservoir_tailrace_level_discharge_function.xlsx``
    
  * - reservoir forebay level-volume function [``m`` and ``m^3``]
    - Relationship between forebay level and volume for different reservoirs
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

You can also try out the model with the sample data provided in the ``input`` folder. Refer to the :ref:`Model_input_output` page for a walkthrough of this example, inspried by real-world data.

Reading the Output
------------------
The output of the model is stored in a NetCDF file, please refer to this `simple tutorial <https://xiaoganghe.github.io/python-climate-visuals/chapters/data-analytics/xarray-basic.html>`_ and `official documentation <https://docs.xarray.dev/en/stable/>`_ of Xarray to understand how to manipulate NetCDF files.

.. rubric:: Footnotes
.. [#] For instance, assuming the planning period spans from 2020 to 2050, with 2020 being the starting point, let's consider a technology that has been in operation since 2019. In this case, 2020 would mark its 2nd year of operation within the planning period. These inputs are useful for modelling the retirement of existing technologies.
.. [#] To model the simplified hydropower operation.
.. [#] To model the potential of technologies with land, fuel, and water constraints.
