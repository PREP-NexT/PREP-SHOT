Mathematical Notations
======================

This page provides a detailed description of the mathematical notations used for formulating the model's objective function and constraints.

Unit List
---------

The description of the units used in this page are as follows:

.. list-table::
   :widths: 10 50
   :header-rows: 1
   :align: left

   * - Unit
     - Description

   * - ``hr``
     - Hour

   * - ``yr``
     - Year

   * - ``USD``
     - US Dollar

   * - ``kW``
     - Kilowatt

   * - ``MW``
     - Megawatt

   * - ``MWh``
     - Megawatt-hour

   * - ``MWy``
     - Megawatt-year

   * - ``MW-km``
     - Megawatt-kilometer

   * - ``tonne``
     - Tonne
   
   * - ``m``
     - Meter

   * - ``s``
     - Second

   * - N/A
     - Not Applicable

Set List
--------

.. list-table::
   :widths: 10 50 5
   :header-rows: 1
   :align: left

   * - Set
     - Description
     - Unit

   * - :math:`e \in \mathcal{E}`
     - Technology
     - N/A

   * - :math:`h, h_{\rm{start}}, h_{\rm{end}} \in \mathcal{H}`
     - Hour
     - ``hr``

   * - :math:`y, y_{\rm{next}}, y_{\rm{pre}}, y_{\rm{start}}, y_{\rm{end}} \in \rm \mathcal{Y}`
     - Year
     - ``yr``

   * - :math:`m \in \rm \mathcal{M}`
     - Month
     - N/A

   * - :math:`z, z_{\rm{from}}, z_{\rm{to}} \in \mathcal{Z}`
     - Zone
     - N/A

   * - :math:`{\rm{age}} \in \mathcal{AGE}`
     - Operation time
     - ``yr``

   * - :math:`s, {\rm{su}} \in \mathcal{S}`
     - Hydropower station
     - N/A

   * - :math:`\mathcal{IU}_{\it{s}} \in \mathcal{S}`
     - Immediate upstream hydropower stations of hydropower station :math:`s`
     - N/A

   * - :math:`\mathcal{SZ}_{\it{z}} \in \mathcal{S}`
     - Subset of hydropower stations located in zone :math:`z`
     - N/A

   * - :math:`\mathcal{DISP} \in \mathcal{E}`
     - Subset of dispatchable technology
     - N/A

   * - :math:`\mathcal{NDISP} \in \mathcal{E}`
     - Subset of non-dispatchable technology
     - N/A

   * - :math:`\mathcal{STOR} \in \mathcal{E}`
     - Subset of storage technology
     - N/A

Variable List
-------------

.. list-table::
   :widths: 10 80 5
   :header-rows: 1
   :align: left
  
   * - Symbol
     - Description
     - Unit

   * - :math:`\rm{cost}^{\rm{total}}`
     - System-wide total cost.
     - ``USD``

   * - :math:`\rm{cost}^{\rm{var}}_{\rm{tech}}`
     - System-wide variable Operation and Maintenance (O&M) cost of technologies.
     - ``USD``

   * - :math:`\rm{cost}^{\rm{fuel}}`
     - System-wide fuel cost of technologies.
     - ``USD``

   * - :math:`\rm{cost}^{\rm{fix}}_{\rm{tech}}`
     - System-wide fixed O&M cost of technologies.
     - ``USD``

   * - :math:`\rm{cost}^{\rm{fix}}_{\rm{line}}` 
     - System-wide fixed O&M cost of transmission lines.
     - ``USD``

   * - :math:`\rm{cost}^{\rm{inv}}_{\rm{tech}}`
     - System-wide investment cost of technologies.
     - ``USD``

   * - :math:`\rm{cost}^{\rm{inv}}_{\rm{line}}`
     - System-wide investment cost of transmission lines.
     - ``USD``

   * - :math:`\rm{cost}^{\rm{annualfuel}}_{\it{y}}`
     - Fuel cost of technologies in the modelled year:math:`y` (the present value of modelled year :math:`y`).
     - ``USD``

   * - :math:`\rm{cost}^{\rm{fuel}}_{\it{y}}`
     - Fuel cost of technologies accumulated from modelled year :math:`y` to a non-modelled year before the immediate next modelled year (the present value of modelled year :math:`y`).
     - ``USD``

   * - :math:`\rm{gen}_{\it{h,m,y,z,e}}`
     - Power generation of technology :math:`e` in zone :math:`z` in hour :math:`h` in month :math:`m` of year :math:`y`.
     - ``MWh``

   * - :math:`\rm{charge}_{\it{h,m,y,z,e}}`
     - Charging electricity of storage technology :math:`e` in zone :math:`z` in hour :math:`h` in month :math:`m` of year :math:`y`.
     - ``MWh``

   * - :math:`\rm{export}_{{\it{h,m,y,z}}_{\rm{from}},{\it{z}}_{\rm{to}}}`
     - Electric energy exported from zone :math:`z_{\rm{from}}` to zone :math:`z_{\rm{to}}` in hour :math:`h` in month :math:`m` of year :math:`y`.
     - ``MWh``

   * - :math:`\rm{import}_{{\it{h,m,y,z}}_{\rm{from}},{\it{z}}_{\rm{to}}}`
     - Electric energy imported from zone :math:`z_{\rm{from}}` to zone :math:`z_{\rm{to}}`  in hour :math:`h` in month :math:`m` of year :math:`y`.
     - ``MWh``

   * - :math:`\rm{storage}_{\it{h,m,y,z,e}}^{\rm{energy}}`
     - Energy storage level of storage technology :math:`e` in hour :math:`h` in month :math:`m` of year :math:`y` in zone :math:`z`.
     - ``MWh``

   * - :math:`\rm{storage}_{\it{s,h,m,y}}^{\rm{reservoir}}` 
     - Reservoir storage corresponding to hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`.
     - :math:`\text{m}^\text{3}`

   * - :math:`\rm{power}_{\it{h,m,y,z,e}}` 
     - Overall power output of technology :math:`e` in zone :math:`z` in hour :math:`h` in month :math:`m` of year :math:`y`.
     - ``MW``

   * - :math:`\rm{power}_{\it{h,m,y,z,e}}^{\it{c}}` 
     - Charging power of storage technology :math:`e` in zone :math:`z` in hour :math:`h` in month :math:`m` of year :math:`y`.
     - ``MW``

   * - :math:`\rm{power}_{\it{h,m,y,z,e}}^{\rm{up}}`
     - Increment in power output of technology :math:`e` in zone :math:`z` from hour :math:`h`-1 to hour :math:`h` in month :math:`m` of year :math:`y`.
     - ``MW``

   * - :math:`\rm{power}_{\it{h,m,y,z,e}}^{\rm{down}}`
     - Decrement in power output of technology :math:`e` in zone :math:`z` from hour :math:`h`-1 to hour :math:`h` in month :math:`m` of year :math:`y`.
     - ``MW``

   * - :math:`\rm{power}_{\it{s,h,m,y}}^{\rm{hydro}}`
     - Power output of hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`.
     - ``MW``

   * - :math:`\rm{cap}_{\it{y,z,e}}^{\rm{existingtech}}`
     - Existing installed capacity of technology :math:`e` in year :math:`y` in zone :math:`z`.
     - ``MW``

   * - :math:`\rm{cap}_{{\it{y,z}}_{\rm{from}},{\it{z}}_{\rm{to}}}^{\rm{existingline}}` 
     - Existing transmission capacity in year :math:`y` from zone :math:`z_{\rm{from}}` to zone :math:`z_{\rm{to}}`.
     - ``MW``

   * - :math:`\rm{cap}_{\it{y,z,e}}^{invtech}`
     - Installed capacity of newly built technology :math:`e` in year :math:`y` in zone :math:`z`.
     - ``MW``
   * - :math:`\rm{cap}_{{\it{y,z}}_{\rm{from}},{\it{z}}_{\rm{to}}}^{\rm{invline}}` 
     - Capacity of newly built transmission lines from zone :math:`z_{\rm{from}}` to zone :math:`z_{\rm{to}}` in year :math:`y`
     - ``MW``
  
   * - :math:`\rm{cap}_{\it{y,z,e}}^{\rm{remaining}}`
     - Remaining installed capacity of technology :math:`e` in year :math:`y` in zone :math:`z`
     - ``MW``

   * - :math:`\rm{carbon}_{\it{y,e}}^{\rm{tech}}`
     - Carbon dioxide equivalent emissions of technology :math:`e` in year :math:`y`
     - ``tonne``
   
   * - :math:`\rm{carbon}_{\it y}`
     - Carbon dioxide equivalent emissions of the entire energy system in year :math:`y`
     - ``tonne``

   * - :math:`\rm{inflow}_{\it{s,h,m,y}}^{\rm{total}}`
     - Total inflow of reservoir corresponding to hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`
     - :math:`\text{m}^\text{3}/\text{s}` 
 
   * - :math:`\rm{outflow}_{\it{s,h,m,y}}^{\rm{total}}`
     - Total outflow of reservoir corresponding to hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`
     - :math:`\text{m}^\text{3}/\text{s}`   

   * - :math:`\rm{outflow}_{\it{s,h,m,y}}^{\rm{gen}}`
     - Generation outflow of reservoir corresponding to hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`
     - :math:`\text{m}^\text{3}/\text{s}` 

   * - :math:`\rm{outflow}_{\it{s,h,m,y}}^{\rm{withdraw}}`
     - Water withdrawal of reservoir corresponding to hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`
     - :math:`\text{m}^\text{3}/\text{s}`

   * - :math:`\rm{outflow}_{\it{s,h,m,y}}^{\rm{spillage}}`
     - Spillage outflow of reservoir corresponding to hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`
     - :math:`\text{m}^\text{3}/\text{s}`

   * - :math:`\rm{head}_{\it{s,h,m,y}}^{\rm{net}}`
     - Net water head of hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`
     - ``m`` 

   * - :math:`\rm{head}_{\it{s,h,m,y}}^{\rm{loss}}`
     - Water head loss of hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y` 
     - ``m`` 

   * - :math:`z_{\it{s,h,m,y}}^{\rm{forebay}}`
     - Forebay water level of reservoir corresponding to hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`
     - ``m`` 

   * - :math:`z_{\it{s,h,m,y}}^{\rm{tailrace}}`
     - Tailrace water level of reservoir corresponding to hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`
     - ``m`` 

Parameter List
--------------

.. list-table::
   :widths: 10 74 16
   :header-rows: 1
   :align: left
   
   * - Symbol
     - Description
     - Unit

   * - :math:`{{C}}_{\it{y,z,e}}^{{\rm{vartech}}}`
     - Variable O&M cost per unit power generation from technology :math:`e` in year :math:`y` in zone :math:`z`.
     - ``USD/MWh``

   * - :math:`{{C}}_{\it{y,z,e}}^{\rm{fuel}}`
     - Fuel cost per unit power generation from technology :math:`e` in year :math:`y` in zone :math:`z`.
     - ``USD/MWh``

   * - :math:`{{C}}_{\it{y,z,e}}^{\rm{fixtech}}`
     - Fixed O&M cost per year per unit existing capacity of technology :math:`e` in year :math:`y` in zone :math:`z`.
     - ``USD/MW-yr``

   * - :math:`{{C}}_{\it{y,z,e}}^{\rm{invtech}}`
     - Investment cost per unit installed capacity of technology :math:`e` in year :math:`y` in zone :math:`z`.
     - ``USD/MW``

   * - :math:`{{C}}_{y,z_{\rm{from}},z_{\rm{to}}}^{\rm{varline}}`
     - Variable O&M cost per unit transmitted electricity from zone :math:`z_{\rm{from}}` to zone :math:`z_{\rm{to}}` in year :math:`y`.
     - ``USD/MWh``

   * - :math:`{{C}}_{y,z_{\rm{from}},z_{\rm{to}}}^{\rm{fixline}}`
     - Fixed O&M cost per year per unit existing capacity of transmission line from zone :math:`z_{\rm{from}}` to zone :math:`z_{\rm{to}}` in year :math:`y`.
     - ``USD/MW-yr``

   * - :math:`{{C}}_{y,z_{\rm{from}},z_{\rm{to}}}^{\rm{invline}}`
     - Investment cost per unit expansion of transmission line from zone :math:`z_{\rm{from}}` to zone :math:`z_{\rm{to}}` in year :math:`y`.
     - ``USD/MW``

   * - :math:`{\rm{CARBON}}_{\it{y,z,e}}`
     - Carbon dioxide equivalent emission per unit power generation from technology :math:`e` in year :math:`y` in zone :math:`z`.
     - ``tonne/MWh``

   * - :math:`\overline{{\rm{CARBON}}}_{y}`
     - Upper bound of carbon dioxide equivalent emission summed across all zones and technologies in year :math:`y`.
     - tonne

   * - :math:`{{\rm{DEMAND}}}_{h,m,y,z}`
     - Average power demand in hour :math:`h` in month :math:`m` of year :math:`y` in zone :math:`z`.
     - ``MW``

   * - :math:`{{\rm{CAP}}}_{\rm{age},{\it{z,e}}}^{{\rm{inittech}}}`
     - Initial installed capacity of technology :math:`e` with the operation time of :math:`\rm{age}` years in zone :math:`z`.
     - N/A

   * - :math:`{{\rm{CAP}}}_{\rm{age},{\it{z}}_{\rm{from}},{\it{z}}_{\rm{to}}}^{\rm{initline}}`
     - Initial installed capacity of transmission lines with the operation time of :math:`\rm{age}` years from zone :math:`z_{\rm{from}}` to zone :math:`{\it{z}}_{\rm{to}}`.
     - ``MW``

   * - :math:`{{\rm{CAP}}}_s^{\rm{hydro}}`
     - Nameplate capacity of hydropower station :math:`s`.
     - ``MW``

   * - :math:`{\underline{{\rm{POWER}}}}_s^{\rm{hydro}}`
     - Guaranteed minimum power output of hydropower station :math:`s`.
     - N/A

   * - :math:`{\underline{{\rm{POWER}}}}_{\it{h,m,y,z,e}}^{\it{c}}`
     - Minimum charge power of storage technology :math:`e` in hour :math:`h` in month :math:`m` of year :math:`y` in zone :math:`z`, expressed as a percentage of the existing capacity of storage technology :math:`e`.
     - N/A

   * - :math:`{{\rm{STORAGE}}}_{\it{m,y,z,e}}^{\rm{energy}}`
     - Energy storage level of technology :math:`e` at the beginning of month :math:`m` of year :math:`y` in zone :math:`z`, expressed as a percentage of the maximum energy storage capacity of storage technology :math:`e`.
     - N/A

   * - :math:`{R}_e^{\rm{up}}`
     - Allowed maximum ramping up capacity of technology :math:`e` in two successive periods, expressed as a percentage of the existing capacity of storage technology :math:`e`.
     - ``1/hr``

   * - :math:`{R}_e^{\rm{down}}`
     - Allowed maximum ramping down capacity of technology :math:`e` in two successive periods, expressed as a percentage of the existing capacity of storage technology :math:`e`.
     - ``1/hr``

   * - :math:`{{\rm{STORAGE}}}_{s,m,y}^{\rm{initreservoir}}`
     - Initial reservoir storage corresponding to hydropower station :math:`s` in month :math:`m` of year :math:`y`.
     - :math:`{\rm m}^{\rm 3}`

   * - :math:`{{\rm{STORAGE}}}_{s,m,y}^{\rm{endreservoir}}`
     - Terminal reservoir storage corresponding to hydropower station :math:`s` in month :math:`m` of year :math:`y`.
     - :math:`{\rm m}^{\rm 3}`

   * - :math:`{\overline{{\rm{STORAGE}}}}_s^{\rm{reservoir}}`
     - Upper bound of reservoir storage corresponding to hydropower station :math:`s`.
     - :math:`{\rm m}^{\rm 3}`

   * - :math:`{\underline{{\rm{STORAGE}}}}_s^{\rm{reservoir}}`
     - Lower bound of reservoir storage corresponding to hydropower station :math:`s`.
     - :math:`{\rm m}^{\rm 3}`

   * - :math:`{{\rm{INFLOW}}}_{\it{s,h,m,y}}^{\rm{net}}`
     - Net inflow of reservoir corresponding to hydropower station :math:`s` in hour :math:`h` in month :math:`m` of year :math:`y`.
     - :math:`{\rm m}^{\rm 3}/{\rm s}`

   * - :math:`{\rm{OUTFLOW}}_s^{\rm{gen}}`
     - Maximum outflow that can be released through turbines of hydropower station :math:`s`.
     - :math:`{\rm m}^{\rm 3}/{\rm s}`

   * - :math:`{\rm{OUTFLOW}}_s^{\rm{spillage}}`
     - Maximum outflow that can be released through spillway of reservoir corresponding to hydropower station :math:`s`.
     - :math:`{\rm m}^{\rm 3}/{\rm s}`

   * - :math:`{\rm{OUTFLOW}}_s`
     - Minimum outflow of reservoir corresponding to hydropower station :math:`s` to meet water supply, environmental flow requirements, flood management, and others.
     - :math:`{\rm m}^{\rm 3}/{\rm s}`

   * - :math:`\omega`
     - Weight factor to extrapolate representative operation day(s) to a full year (8760 hours).
     - N/A

   * - :math:`\rho`
     - Density of water.
     - :math:`\rm{kg}/\rm{m}^\text{3}`

   * - :math:`g`
     - Acceleration of gravity.
     - :math:`\rm{m}/\rm{s}^\text{2}`

   * - :math:`\eta_{y,e}^{\rm{in}}`
     - Charging efficiency of storage technology :math:`e` in year :math:`y`.
     - N/A

   * - :math:`\eta_{y,e}^{\rm{out}}`
     - Generation efficiency of technology :math:`e` in year :math:`y`.
     - N/A

   * - :math:`\eta_s`
     - Generation efficiency of converting water energy to electric energy in hydropower station :math:`s`.
     - N/A

   * - :math:`\eta_{z_{\rm{from}},z_{\rm{to}}}^{\rm{trans}}`
     - Transmission efficiency of transmission lines from zone :math:`z_{\rm{from}}` to zone :math:`z_{\rm{to}}`.
     - N/A

   * - :math:`\tau_{{\rm{su}},s}`
     - Water travel (or propagation) time from the upstream hydropower station :math:`{\rm{su}}` to the immediate downstream hydropower station :math:`s`.
     - ``hr``

   * - :math:`\Delta h`
     - Time step.
     - ``hr``

   * - :math:`r`
     - Discount rate.
     - N/A

   * - :math:`{T}_e`
     - Lifetime of technology :math:``e``.
     - ``yr``

   * - :math:`{T}_{\rm{line}}`
     - Lifetime of transmission line.
     - ``yr``

   * - :math:`{\rm{EP}}_e`
     -  Power to energy ratio of storage technology :math:`e`.
     - ``hr``

Objective Functions
-------------------

Costs
+++++

The objective function of the model is to minimize the net present value of the system's cost. This includes investment cost, fixed O&M cost, variable cost and fuel cost by cost type, technology cost, transmission line cost by the source of cost, and operation cost and planning cost by the source of cost.

The cost equations are defined as follows:

.. math::
  \rm{cost} &= \rm{cost}_\rm{tech}^\rm{var} + \rm{cost}_\rm{line}^\rm{var} + \rm{cost}^\rm{fuel} + \rm{cost}_\rm{tech}^\rm{fix} + \rm{cost}_\rm{line}^\rm{fix} + \rm{cost}_\rm{tech}^\rm{inv} + \rm{cost}_\rm{line}^\rm{inv} \\
  \\
  \rm{cost}_\rm{tech}^\rm{var} &= \frac{\sum_{t,m,y,z,\rm{te}}C_{y,z,\rm{te}}^\rm{tech-var}\times \rm{gen}_{t,m,y,z,\rm{te}}}\rm{Weight} \times \rm{factor}_{y}^\rm{var} \\
  \\
  \rm{cost}_\rm{line}^\rm{var} &= \frac{\sum_{t,m,y,z_s,z_o}C_{y,z}^\rm{line-var}\times \rm{export}_{t,m,y,z_s,z_o}}\rm{Weight} \times \rm{factor}_{y}^\rm{var} \\
  \\
  \rm{cost}^\rm{fuel} & = \frac{\sum_{t,m,y,z,\rm{te}}C_{y,z,\rm{te}}^\rm{fuel}\times \rm{gen}_{t,m,y,z,\rm{te}}}\rm{Weight} \times \rm{factor}_{y}^\rm{var} \\
  \\
  \rm{cost}_\rm{tech}^\rm{fix} &= \sum_{y,z,\rm{te}}C_{y,z,\rm{te}}^\rm{tech-fix}\times \rm{cap}_{y,z,\rm{te}}^\rm{existing-tech}\times \rm{factor}_{y}^\rm{fix} \\
  \\
  \rm{cost}_\rm{line}^\rm{fix} &= \sum_{y,z_s,z_o}C_{y,z_s,z_o}^\rm{line-fix}\times \rm{cap}_{y,z_s,z_o}^\rm{existing-line}\times \rm{factor}_{y}^\rm{fix} \\
  \\
  \rm{cost}_\rm{tech}^\rm{inv} &=  \sum_{y,z,\rm{te}}C_{y,z,\rm{te}}^\rm{tech-inv}\times \rm{cap}_{y,z,\rm{te}}^\rm{tech-inv}\times \rm{factor}_{y}^\rm{inv} \\
  \\
  \rm{cost}_\rm{line}^\rm{inv} &= \sum_{y,z_s,z_o}C_{y,z_s,z_o}^\rm{line-inv}\times \rm{cap}_{y,z_s,z_o}^\rm{line-inv}\times \rm{factor}_{y}^\rm{inv} \times 0.5 \\
  \\

The variables are defined as follows:

.. list-table::
   :widths: 10 80 5
   :header-rows: 1
   :align: left

   * - Variable
     - Description
     - Unit

   * - :math:`\text{cost}`
     - Total cost.
     - ``USD``

   * - :math:`\text{cost}_\text{tech}^\text{var}` 
     - Variable cost of technologies.
     - ``USD``

   * - :math:`\text{cost}_\text{line}^\text{var}`
     - Variable cost of transmission lines.
     - ``USD``

   * - :math:`\text{cost}^\text{fuel}`
     - Fuel cost of technologies.
     - ``USD``

   * - :math:`\text{cost}_\text{tech}^\text{fix}`
     - Fixed cost of technologies.
     - ``USD``

   * - :math:`\text{cost}_\text{line}^\text{fix}`
     - Fixed cost of transmission lines.
     - ``USD``

   * - :math:`\text{cost}_{tech}^{inv}` 
     - Investment cost of technologies.
     - ``USD``

   * - :math:`\text{cost}_\text{line}^\text{inv}`
     - Investment cost of transmission lines.
     - ``USD``

   * - :math:`\text{gen}_{t,m,y,z,te}` 
     - Generation electricity of the :math:`te`-th technology, in the :math:`z`-th zone, in the :math:`y`-th year, for the :math:`m` time period, and in the :math:`t`-th hour.
     - ``MWh``

   * - :math:`\text{export}_{t,m,y,z_s,z_o}`
     - Transmission electricity from the :math:`z_s`-th zone to the :math:`z_o`-th zone, in the :math:`y`-th year, for the :math:`m` time period, and in the :math:`t`-th hour.
     - ``MWh``

   * - :math:`\text{cap}^\text{existing-tech}_{y,z,te}`
     - Existing installed capacity of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`\text{cap}^\text{existing-line}_{y,z_s,z_o}`
     - Existing transmission capacity from the :math:`z_s`-th zone to the :math:`z_o`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`\text{cap}^\text{tech-inv}_{y,z,te}` 
     - Newly-build installed capacity of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`\text{cap}^\text{line-inv}_{y,z_s,z_o}` 
     - Newly-build capacity of transmission line from the :math:`z_s`-th zone to the :math:`z_o`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`\text{factor}^\text{var}_{y}` 
     - Variable cost economic factor in the :math:`y`-th year.
     - N/A

   * - :math:`\text{factor}^\text{fix}_{y}`
     - Fixed cost economic factor in the :math:`y`-th year.
     - N/A

   * - :math:`\text{factor}^\text{inv}_{y}` 
     - Investment cost economic factor in the :math:`y`-th year.
     - N/A

The parameters are defined as follows:

.. list-table::
   :widths: 10 80 5
   :header-rows: 1
   :align: left
  
   * - Parameter
     - Description
     - Unit

   * - :math:`C_{y,z,te}^\text{tech-var}` 
     - Variable cost of unit capacity of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``USD/MW``

   * - :math:`C_{y,z}^\text{line-var}`
     - Variable cost of unit capacity of transmission line in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``USD/MW``

   * - :math:`C_{y,z,te}^\text{fuel}`
     - Fuel cost of unit generation electricity of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``USD/MWh``

   * - :math:`C_{y,z,te}^\text{tech-fix}`
     - Fixed cost of unit capacity of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``USD/MWy``

   * - :math:`C_{y,z_s,z_o}^\text{line-fix}`
     - Fixed cost of unit capacity of transmission line from the :math:`z_s`-th zone to the :math:`z_o`-th zone, and in the :math:`y`-th year.
     - ``USD/MWy``

   * - :math:`C_{y,z,te}^\text{tech-inv}` 
     - Investment cost of unit capacity of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``USD/MW``

   * - :math:`C_{y,z_s,z_o}^\text{line-inv}`
     - Investment cost of transmission lines from the :math:`z_s`-th zone to the :math:`z_o`-th zone, and in the :math:`y`-th year.
     - ``USD/MW``

   * - :math:`\text{Weight}`
     - Proportion of selected scheduling period in a year (8760 hours) that is :math:`\frac{H\times M}{8760}`.
     - N/A

Factors
+++++++

To account for the variable factor, fixed factor, and investment factor, we need to convert all future costs to their net present value. This means adjusting for the time value of money so that all costs are expressed in terms of today's dollars. 

We also assume that variable cost and fixed cost for non-modelled years are assumed to be equal to the cost of the last modelled year preceding them. This allows for consistent comparison across different time periods and technologies.

**Variable Factor**

.. image:: ./_static/varcost.png
  :width: 400
  :alt: Calculation of variable costs

Given the following:

* Variable cost of modeled year: :math:`B`
* Discount rate: :math:`r`
* :math:`m`-th modeled year: :math:`m = y - y_\text{min}`
* Depreciation periods: :math:`n`

The total present value can be calculated as follows:

.. math::

  \begin{align*}
  \text{total present value} &= \frac{B}{(1+r)^m} + \frac{B}{(1+r)^{m+1}} + \cdots + \frac{B}{(1+r)^{(m+k-1)}} \\
  \\
  &= B(1+r)^{(1-m)}\frac{1-(1+r)^k}{r} \\
  \\
  \end{align*}

And we can calculate the variable factor as follows:

.. math::

  \begin{align*}
  \text{factor}_{y}^{var} &= (1+r)^{1-m_y}\frac{1-(1+r)^{k_y}}{r} \\
  \\
  m_{y} &= y - y_\text{min} \\
  \\
  k_{y} &= y_\text{periods} \\
  \\
  \end{align*}

**Fixed Factor**

We can equate the fixed factor with the variable factor as follows:

.. math:: \text{factor}_{y}^\text{fix} = factor_{y}^\text{var}

**Investment Factor**

.. image:: ./_static/invcost.png
  :width: 400
  :alt: Calculation of investment costs

Given the following:

* Weighted Average Cost of Capital (WACC, or otherwise known as the interest rate): :math:`i`
* Discount rate: :math:`r`
* :math:`m`-th modeled year: :math:`m = y - y_\text{min}`
* Length of :math:`m`-th planning periods: :math:`k`

The total present value can be calculated as follows:

.. math::

  \begin{align*}
  \text{total present value} &= \frac{P}{(1+r)^m} \\
  \\
  &= \frac{\frac{A}{(1+i)} + \frac{A}{(1+i)^2} + \cdots + \frac{A}{(1+i)^n}}{(1+r)^m} \\
  \\
  &= A\frac{1-(1+i)^{-n}}{i}\times\frac{1}{(1+r)^m} \\
  \\
  \end{align*}

From the above, we can solve for the annualized cost of depreciation periods, :math:`A`, as:

.. math::

  A = P\frac{i}{1-(1+i)^{-n}} \\
  \\

The capital recovery factor is then calculated as:

.. math::

  \text{capital recovery factor} = \frac{i}{1-(1+i)^{-n}} \\
  \\

Let's focus on the time periods that fall within the modelled time horizon (indicated in black colour). We can calculate the length of time periods, :math:`k`, as follows:

.. math::
  
  k = y_{max} - y \\
  \\

Using :math:`k`, we can calculate the net present value as follows:

.. math::

  \text{net present value} =
  \begin{cases} 
  \frac{\frac{A}{(1+r)} + \frac{A}{(1+r)^2} + \cdots + \frac{A}{(1+r)^{min(n, k)}}}{(1+r)^m} & \text{if }n \le k \\
  \\
  \text{total present value} & \text{if }n > k \\
  \\
  \frac{A\frac{1-(1+r)^{-k}}{r}}{(1+r)^m} = P\frac{i}{1-(1+i)^{-n}}\times\frac{1-(1+r)^{-k}}{r(1+r)^m} & \text{otherwise} \\
  \\
  \end{cases}

And we can calculate the investment factor as follows:

.. math::

  factor_{y}^{inv} = \frac{i}{1-(1+i)^{-n}}\times\frac{1-(1+r)^{-min(n,k)}}{r(1+r)^m} \\
  \\

Constraints
-----------

Retirement
++++++++++

The model computes the retirement of each technology and transmission line with these considerations:

* The initial age of the technology and transmission line is based on its capacity ratio.
* Each planning and scheduling period is based on the existing capacity.

The existing capacity for each year, in each zone, for each technology, is as follows:

.. math::

  cap_{y, z, te}^{existing-tech} = \sum_{lifetime-age<y-y_{min})}cap_{age,z,te}^{tech-init} + \sum_{(yy\le y) \& (lifetime>y-yy)}cap_{yy,z,te}^{tech-inv} \text{, for all } y,z,te \\
  \\

The existing capacity of the transmission lines for each year, from :math:`z_s`-th zone to :math:`z_o`-th zone, is as follows:

.. math::

  cap_{y, z_s, z_o}^{existing-line} = \sum_{lifetime-age<y-y_{min})}cap_{age,z_s,z_o}^{line-init} + \sum_{(yy\le y) \& (lifetime>y-yy)}cap_{yy,z_s,z_o}^{line-inv} \text{, for all } y,z_s,z_o \\
  \\

Carbon Emission
+++++++++++++++

The model computes the carbon emissions for each year, based on the sum of carbon emissions from each zone, and from each technology.

The carbon emission for each technology, for each year, and in each zone, is as follows:

.. math::

  carbon_{y,te}^{tech} = \sum_{t,m,z}Carbon_{y,z,te}\times gen_{t,m,y,z,te} \quad \forall y,te \\
  \\


The carbon emission for each year is as follows:

.. math::

  carbon_{y} = \sum_{te}carbon_{y,te}^{tech} \forall y \\
  \\

Where, the calculated carbon emission for each year, must be lower than its upper bound, as follows:

.. math::

  carbon_{y} \le \overline{carbon}_y \forall y \\
  \\

Power Balance
+++++++++++++

The model computes the power balance for each hour, in each time period, for each year, and in each zone, as follows:

.. math::

  Demand_{t,m,y,z} = & \sum_{z_s\neq z}import_{t, m, y, z_s, z} - \sum_{z_o\neq z}export_{t, m, y, z, z_o} + \\
                     \\
                     & \sum_{te}gen_{t, m, y, z, te} - \sum_{te\in storage}charge_{t, m, y, z, te}\quad \forall t,m,y,te

Transmission Loss
+++++++++++++++++

The model computes the transmission loss for each hour, in each time period, for each year, from :math:`z_s`-th zone to :math:`z_o`-th zone, as follows:

.. math::

  export_{t, m, y, z_s, z_o} \times Effi_{z_s, z_o}^{trans} = import_{t, m, y, z_s, z_o} \quad \forall t,y,z_s\neq z_o \\
  \\

Maximum Output
++++++++++++++

The model computes the maximum output for each hour, in each time period, for each year, in each zone, and for each technology, as follows:

.. math::

  gen_{t, m, y, z, te} \leq cap_{y, z, te}^{existing-tech} \forall t,m \\
  \\

Energy Storage
++++++++++++++

The model computes the energy storage level for each hour, for each year, in each zone, and for each technology, as follows:

.. math::

  storage_{t,y,z,te}^{level} = storage_{t-1,y,z, te}^{level} - \frac{gen_{t,y,z,te}}{Effi_{y,te}^{storage}} \quad \forall te \in storage, t,y,z \\
  \\

Where, the starting energy storage level is set to the initial storage level, as follows:

.. math::

  storage_{t,y,z,te}^{level} = Storage_{z, te}^{init} \quad \forall t,y=INI,z \\
  \\

And the final energy storage level is set to the ending storage level, as follows:

.. math::

  storage_{t,y,z}^{level} = Storage_{z, te}^{end} \quad \forall t,y=END,z \\
  \\

Ramping Ratio
+++++++++++++

The model computes the generated power and ensures it is less than the product of the ramping ratio and the existing capacity of each technology.

Where, the upper bound of the generated power is defined, as follows:

.. math::

  gen^{up}_{t,m,y,z,te} \le R^{up}_{te}\times cap_{y,z,te}^{existing-tech} \quad \forall t,m,y,z,te \\
  \\

And the lower bound of the generated power is defined, as follows:

.. math::

  gen^{down}_{t,m,y,z,te} \le R^{down}_{te}\times cap_{y,z,te}^{existing-tech} \quad \forall t,m,y,z,te \\
  \\

Finally, the difference between the upper and lower bound of the generated power, in the current hour, is equal to the difference between the generated power in the current hour and the previous hour, as follows:

.. math::

  gen^{up}_{t,m,y,z,te} - gen^{down}_{t,m,y,z,te} = gen_{t,m,y,z,te} - gen_{t-1,m,y,z,te} \quad \forall t,m,y,z,te \\
  \\
