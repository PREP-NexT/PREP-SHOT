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

   * - ``RMB``
     - Chinese Yuan

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

   * - ``tonnes``
     - Tonnes

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

   * - :math:`te`
     - Technology
     - N/A

   * - :math:`h` or :math:`t`
     - Hour
     - ``hr``

   * - :math:`y`
     - Year
     - ``yr``

   * - :math:`m`
     - Time period
     - N/A

   * - :math:`z`
     - Zone
     - N/A

Variable List
-------------

.. list-table::
   :widths: 10 80 5
   :header-rows: 1
   :align: left
  
   * - Variable
     - Description
     - Unit

   * - :math:`\text{cost}`
     - Total cost of whole energy system.
     - ``USD``

   * - :math:`\text{cost}^\text{var}`
     - Variable Operation and Maintenance (O&M) cost.
     - ``USD``

   * - :math:`\text{cost}^\text{fix}`
     - Fixed O&M cost.
     - ``USD``

   * - :math:`\text{cost}^\text{newtech}` 
     - Investment cost of technologies.
     - ``USD``

   * - :math:`\text{cost}^\text{newline}`
     - Investment cost of transmission lines.
     - ``RMB``

   * - :math:`\text{gen}_{h,m,y,z,te}`
     - Generating capacity of the :math:`te`-th technology, in the :math:`z`-th zone, in the :math:`y`-th year, for the :math:`m` time period, and in the :math:`h`-th hour.
     - ``MWh``

   * - :math:`\text{cap}^\text{existing}_{y,z,te}`
     - Existing installed capacity of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`\text{cap}^\text{newtech}_{y,z,te}`
     - Newly-built installed capacity of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`\text{cap}^\text{newline}_{y,z_s,z_o}`
     - Newly-built transmission line capacity from the :math:`z_s`-th zone to the :math:`z_o`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`\text{cap}^\text{remaining}_{y,z,te}`
     - Remaining capacity of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`\text{carbon}^\text{tech}_{y,te}`
     - Carbon emission of the :math:`te`-th technology for all zones, and in the :math:`y`-th year
     - ``tonnes``

   * - :math:`\text{slack}_{h,y,z}` 
     - Unserved demand in the :math:`z`-th zone, in the :math:`y`-th year, and in the :math:`h`-th hour.
     - ``MWh``

   * - :math:`\text{trans}^\text{import}_{h,y,z1,z}`
     - Generation output imported from the :math:`z1`-th zone to the :math:`z`-th zone, in the :math:`y`-th year, and in the :math:`h`-th hour.
     - ``MWh``

   * - :math:`\text{cap}^\text{retire}_{y,z,te}`
     - Retiring capacity of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`\text{storage}^\text{level}_{y,z,te}`
     - Storage level of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`\text{consumption}_{h,y,z,te}`
     - Cost of fuel consumption of the :math:`te`-th technology, in the :math:`z`-th zone, in the :math:`y`-th year, and in the :math:`h`-th hour.
     - ``USD``

   * - :math:`\text{gen}^\text{up}_{h,y,z,te}` 
     - Output of change upward of the :math:`te`-th technology, in the :math:`z`-th zone, in the :math:`y`-th year, and in the :math:`h`-th hour.
     - ``MW``

   * - :math:`\text{gen}^\text{down}_{h,y,z,te}`
     - Output of change downward of the :math:`te`-th technology, in the :math:`z`-th zone, in the :math:`y`-th year, and in the :math:`h`-th hour.
     - ``MW``

Parameter List
--------------

.. list-table::
   :widths: 10 74 16
   :header-rows: 1
   :align: left
   
   * - Parameter
     - Description
     - Unit

   * - :math:`C^\text{var}_{y,te}`
     - Variable O&M cost of the :math:`te`-th technology, and in the :math:`y`-th year.
     - ``USD/MW``

   * - :math:`C^\text{fix}_{y,te}`
     - Fixed O&M cost of the :math:`te`-th technology, and in the :math:`y`-th year.
     - ``USD/kW``

   * - :math:`C^\text{newtech}_{y,te}`
     - Investment cost of the :math:`te`-th technology, and in the :math:`y`-th year.
     - ``USD/KW``

   * - :math:`C^\text{newline}_{y,te}`
     - Investment cost of the :math:`te`-th technology, and in the :math:`y`-th year.
     - ``USD/MW-km``

   * - :math:`\text{DF}_{y}`
     - Discount factor in the :math:`y`-th year.
     - N/A

   * - :math:`\text{carbon}_{y}`
     - Carbon emission in the :math:`y`-th year.
     - ``ton/MWh``

   * - :math:`\overline{\text{carbon}}_y`
     - Upper bound of carbon emission for all zones in the :math:`y`-th year.
     - ``tonnes``

   * - :math:`\text{Demand}_{t,m,y,z}`
     - Load demand in the :math:`z`-th zone, in the :math:`y`-th year, for the :math:`m` time period, and in the :math:`t`-th hour.
     - ``MW``

   * - :math:`\text{Effi}^\text{trans}_{z1,z,y}`
     - Efficiency of transmission line in the :math:`y`-th year, and from the :math:`z_1`-th zone to the :math:`z`-th zone
     - N/A

   * - :math:`\text{Installed}^\text{init}_{z,te}`
     - Installed capacity of the :math:`te`-th technology, and in the :math:`z`-th zone.
     - ``MW``

   * - :math:`\text{Effi}^\text{storage}_{y,te}`
     - Energy storage conversion efficiency of the :math:`te`-th technology, and in the :math:`y`-th year.
     - N/A

   * - :math:`\text{Storage}^\text{init}_{z}`
     - Storage level in the :math:`z`-th zone.
     - ``MW``

   * - :math:`\text{Storage}^\text{end}_{y, z}`
     - Minimum storage level in the :math:`z`-th zone, and in the :math:`y`-th year.
     - ``MW``

   * - :math:`R^\text{up}_{te}`
     - Maximum upward ramping ratio of the :math:`te`-th technology.
     - N/A

   * - :math:`R^\text{down}_{te}`
     - Maximum downward ramping ratio of the :math:`te`-th technology.
     - N/A

   * - :math:`\text{cap}^\text{factor}_{h,z,te}`
     - Capacity factor of the :math:`te`-th technology, in the :math:`z`-th zone, and in the :math:`h`-th hour.
     - N/A

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
