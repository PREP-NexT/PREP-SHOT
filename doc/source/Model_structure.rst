Model structure
================

Notations
----------

1. Sets
+++++++++++

.. list-table::
   :widths: 10 50
   :header-rows: 0
   :align: left

   * - :math:`\text{te}` 
     - Total cost of whole energy system [USD]
   * - :math:`h`
     - Variable Operation and Maintenance (O&M) cost [USD]
   * - :math:`m` 
     - Fixed O&M cost [USD]
   * - :math:`z`
     - Zone
   * - :math:`y` 
     - Year

2. Variables
++++++++++++++++++++++

.. list-table::
   :widths: 10 80
   :header-rows: 0
   :align: left
  
   * - :math:`\text{cost}`
     - Total cost of whole energy system [USD]
   * - :math:`\text{cost}^\text{var}`
     - Variable Operation and Maintenance (O&M) cost [USD]
   * - :math:`\text{cost}^\text{fix}`
     - Fixed O&M cost [USD]
   * - :math:`\text{cost}^\text{newtech}` 
     - Investment cost of technologies [USD]
   * - :math:`\text{cost}^\text{newline}`
     - Investment cost of transmission lines [RMB]         
   * - :math:`\text{gen}_{h,m,y,z,te}`
     - Generating capacity of :math:`\text{te}`-th technology of :math:`z`-th zone in the :math:`h`-th hour :math:`y`-th year [MWh]
   * - :math:`\text{cap}^\text{existing}_{y,z,te}`
     - Existing installed capacity of :math:`\text{te}`-th technology of the :math:`z`-th zone in the :math:y\ -th year
   * - :math:`\text{cap}^\text{newtech}_{y,z,te}`
     - New-built installed capacity of :math:`\text{te}`-th technology of the :math:`z`-th zone in the :math:`y`-th year
   * - :math:`\text{cap}^\text{newline}_{y,z_s,z_o}`
     - New-built transmission line capacity from the :math:`z_s`-th zone to the :math:`z_o`-th zone in the :math:`y`-th year
   * - :math:`\text{cap}^\text{remaining}_{y,z,te}`
     - Remaining capacity of :math:`\text{te}`-th technology the :math:`z`-th zone in the starting year
   * - :math:`\text{carbon}^\text{tech}_{y,te}`
     - Carbon emission of :math:`\text{te}`-th technology all zones in the :math:`y`-th year
   * - :math:`\text{slack}_{h,y,z}` 
     - Unserved demand of :math:`z`-th zone in the :math:`h`-th hour :math:`y`-th year 
   * - :math:`\text{trans}^\text{import}_{h,y,z1,z}`
     - Generation output imported from the :math:`z1`-th zone to  the :math:`z`-th zone in the :math:`h`-th hour :math:`y`-th year 
   * - :math:`\text{cap}^\text{retire}_{y,z,te}`
     - Retire capacity of the :math:`\text{te}`-th technology in the :math:`z`-th zonein the :math:`y`-th year [MW]  
   * - :math:`\text{storage}^\text{level}_{y,z,te}`
     - Storage level in the :math:`z`-th zone in the :math:`h`-th hour :math:`y`-th year [MW] 
   * - :math:`\text{consumption}_{h,y,z,te}`
     - Costs of fuel consumption in the :math:`z`-th zone in the :math:`h`-th hour :math:`y`-th year [USD]  
   * - :math:`\text{gen}^\text{up}_{h,y,z,te}` 
     - Output of change upward in the :math:`z`-th zone in the :math:`h`-th hour :math:`y`-th year [MW]             
   * - :math:`\text{gen}^\text{down}_{h,y,z,te}`
     - Output of change downward in the :math:`z`-th zone in the :math:`h`-th hour :math:`y`-th year [MW]                 

3. Parameters
++++++++++++++++++++++
.. list-table::
   :widths: 10 80
   :header-rows: 0
   :align: left
   
   * - :math:`C^\text{var}_{y,te}`
     - Variable O&M cost of :math:`\text{te}`-th technology :math:`y`-th year [USD/MWh] 
   * - :math:`C^\text{fix}_{y,te}`
     - Fixed O&M cost of of :math:`\text{te}`-th technology :math:`y`-th year [USD/kWy]
   * - :math:`C^\text{newtech}_{y,te}`
     - Investment cost of :math:`\text{te}`-th technology :math:`y`-th year [USD/KW]
   * - :math:`C^\text{newline}_{y,te}`
     - Investment cost of transmission line in :math:`y`-th year [USD/(MW*km)] 
   * - :math:`\text{DF}_{y}`
     - Discount factor for each year
   * - :math:`\text{Carbon}_{y,te}`
     - Carbon content of :math:`\text{te}`-th technology in :math:`y`-th year [Ton/MWh]
   * - :math:`\overline{\text{Carbon}}_y`
     - Upper bound of carbon dioxide for all zones in :math:`y`-th year [Ton]
   * - :math:`\text{Demand}_{h,z,y}`
     - Load demand of :math:`z`-th zone in :math:`h`-th hour :math:`y`-th year [MW]
   * - :math:`\text{Effi}^\text{trans}_{z1,z,y}`
     - Efficiency of transmission line from :math:`z1`-th zone to :math:`z`-th zone in :math:`y`-th year
   * - :math:`\text{Installed}^\text{init}_{z,te}`
     - Installed capacity of :math:`\text{te}`-th technology :math:`z`-th zone in starting year [MW]
   * - :math:`\text{Effi}^\text{storage}_{y,te}`
     - Energy storage conversion efficiency of :math:`\text{te}`-th technology in :math:`y`-th year
   * - :math:`\text{Storage}^\text{init}_{z}`
     - Storage level of :math:`z`-th zone in starting year [MW]
   * - :math:`\text{Storage}^\text{end}_{y, z}`
     - Minimum storage level of :math:`z`-th zone in the end of each year [MW]
   * - :math:`R^\text{up}_{te}`
     - Maximum upward ramping ratio of :math:`\text{te}`-th technology
   * - :math:`R^\text{down}_{te}`
     - Maximum downward ramping ratio of :math:`\text{te}`-th technology
   * - :math:`\text{Cap}^\text{factor}_{h,z,te}`
     - Capacity factor of the :math:`\text{te}`-th technology in the :math:`h`-th hour :math:`y`-th year

4. Objective function
++++++++++++++++++++++

The objective function of the model is to minimize the net present value of  the cost of the whole system, which includes investment cost, fixed O&M cost, variable cost and fuel cost by cost type, technology cost and transmission line cost by source of cost and operation cost and planning cost by source of cost. As follows:

.. math::
  \text{cost} &= \text{cost}_\text{tech}^\text{var} + \text{cost}_\text{line}^\text{var} + \text{cost}^\text{fuel} + \text{cost}_\text{tech}^\text{fix} + \text{cost}_\text{line}^\text{fix} + \text{cost}_\text{tech}^\text{inv} + \text{cost}_\text{line}^\text{inv} \\
  cost_{tech}^{var} &= \frac{\sum_{t,m,y,z,te}C_{y,z,te}^{tech-var}\times gen_{t,m,y,z,te}}{Weight} \times factor_{y}^{var} \\
  cost_{line}^{var} &= \frac{\sum_{t,m,y,z_s,z_o}C_{y,z}^{line-var}\times export_{t,m,y,z_s,z_o}}{Weight} \times factor_{y}^{var} \\
  cost^{fuel} & = \frac{\sum_{t,m,y,z,te}C_{y,z,te}^{fuel}\times gen_{t,m,y,z,te}}{Weight} \times factor_{y}^{var} \\
  cost_{tech}^{fix} &= \sum_{y,z,te}C_{y,z,te}^{tech-fix}\times cap_{y,z,te}^{existing-tech}\times factor_{y}^{fix} \\
  cost_{line}^{fix} &= \sum_{y,z_s,z_o}C_{y,z_s,z_o}^{line-fix}\times cap_{y,z_s,z_o}^{existing-line}\times factor_{y}^{fix} \\
  cost_{tech}^{inv} &=  \sum_{y,z,te}C_{y,z,te}^{tech-inv}\times cap_{y,z,te}^{tech-inv}\times factor_{y}^{inv} \\
  cost_{line}^{inv} &= \sum_{y,z_s,z_o}C_{y,z_s,z_o}^{line-inv}\times cap_{y,z_s,z_o}^{line-inv}\times factor_{y}^{inv} \times 0.5

where variables

.. list-table::
   :widths: 10 80
   :header-rows: 0
   :align: left

   * - :math:`\text{cost}`
     - total cost [USD]
   * - :math:`\text{cost}_\text{tech}^\text{var}` 
     - variable cost of technologies [USD]
   * - :math:`\text{cost}_\text{line}^\text{var}`
     - variable cost of transmission lines [USD]
   * - :math:`\text{cost}^\text{fuel}`
     - fuel cost of technologies [USD]
   * - :math:`\text{cost}_\text{tech}^\text{fix}`
     - fixed cost of technologies [USD]
   * - :math:`\text{cost}_\text{line}^\text{fix}`
     - fixed cost of transmission lines [USD]
   * - :math:`\text{cost}_{tech}^{inv}` 
     - investment cost of technologies [USD]
   * - :math:`\text{cost}_\text{line}^\text{inv}`
     - investment cost of transmission lines [USD]
   * - :math:`\text{gen}_{t,m,y,z,\text{te}}` 
     - generation electricity of :math:`\text{te}`-th technology in :math:`t`-th hour :math:`m`-th time period :math:`y`-th year :math:`z`-th zone [MWh]
   * - :math:`\text{export}_{t,m,y,z_s,z_o}`
     - transmission electricity from :math:`z_s`-th zone to :math:`z_o`-th zone in :math:`t`-th hour :math:`m`-th time period :math:`y`-th year [MWh]
   * - :math:`\text{cap}^\text{existing-tech}_{y,z,te}`
     - existing installed capacity of :math:`\text{te}`-th technology in :math:`y`-th year :math:`z`-th zone [MW]
   * - :math:`\text{cap}^\text{existing-line}_{y,z_s,z_o}`
     - existing transmission capacity from :math:`z_s`-th zone to :math:`z_o`-th zone in :math:`y`-th year [MW]
   * - :math:`\text{cap}^\text{tech-inv}_{y,z,te}` 
     - new-build installed capacity of :math:`\text{te}`-th technology in :math:`y`-th year :math:`z`-th zone [MW]
   * - :math:`\text{cap}^\text{line-inv}_{y,z_s,z_o}` 
     - new-build capacity of transmission line from :math:`z_s`-th zone to :math:`z_o`-th zone in :math:`y`-th year [MW]
   * - :math:`\text{factor}^\text{var}_{y}` 
     - variable cost economic factor in :math:`y`-th year
   * - :math:`\text{factor}^\text{fix}_{y}`
     - fixed cost economic factor in :math:`y`-th year
   * - :math:`\text{factor}^\text{inv}_{y}` 
     - investment cost economic factor in :math:`y`-th year

where parameters

.. list-table::
   :widths: 10 80
   :header-rows: 0
   :align: left
  
  * - :math:`C_{y,z,te}^\text{tech-var}` 
    - variable cost of unit capacity of :math:`\text{te}`-th technology in :math:`y`-th year :math:`z`-th zone [USD/MW]
  * - :math:`C_{y,z}^\text{line-var}`
    - variable cost of unit capacity of transmission line in :math:`y`-th year :math:`z`-th zone [USD/MW]
  * - :math:`C_{y,z,te}^\text{fuel}`
    - fuel cost of unit generation electricity of :math:`\text{te}`-th technology in :math:`y`-th year :math:`z`-th zone [USD/MWh]
  * - :math:`C_{y,z,te}^\text{tech-fix}`
    - fixed cost of unit capacity of :math:`\text{te}`-th technology in :math:`y`-th year :math:`z`-th zone [USD/MW/y]
  * - :math:`C_{y,z_s,z_o}^\text{line-fix}`
    - fixed cost of unit capacity of transmission line from :math:`z_s`-th zone to :math:`z_o`-th zone [USD/MW/y]
  * - :math:`C_{y,z,te}^\text{tech-inv}` 
    - investment cost of unit capacity of :math:`\text{te}`-th technology in :math:`y`-th year :math:`z`-th zone [USD/MW]
  * - :math:`C_{y,z_s,z_o}^\text{line-inv}`
    - investment cost of transmission lines from :math:`z_s`-th zone to :math:`z_o`-th zone in :math:`y`-th year [USD/MW]
  * - :math:`\text{Weight}`
    - proportion of selected scheduling period in a year (8760 hours) that is :math:`\frac{H\times M}{8760}`

How to account for :math:`\text{factor}_{y}^\text{var}`, :math:`\text{factor}_{y}^\text{fix}` and :math:`\text{factor}_{y}^\text{inv}`?

Convert future value of all costs to net present value. Assume variable cost, fixed cost of non-modeled year are equals to year of last modeled year before them.

4.1 :math:`\text{factor}_{y}^\text{var}`
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

.. image:: ./_static/varcost.png
  :width: 400
  :alt: Calculation of variable costs

Given variable cost of modeled year = :math:`B`, discount rate = :math:`r`, :math:`m`-th modeled year :math:`m=y-y_{min}`, depreciation periods = :math:`n`. Total present value are calculated as follows:

.. math::
  \text{Total present value} &= \frac{B}{(1+r)^m} + \frac{B}{(1+r)^{m+1}} + \cdots + \frac{B}{(1+r)^{(m+k-1)}} \\
   & = B(1+r)^{(1-m)}\frac{1-(1+r)^k}{r}

That is:

.. math::
  \text{factor}_{y}^{var} &= (1+r)^{1-m_y}\frac{1-(1+r)^{k_y}}{r} \\
  m_{y} &= y - y_\text{min} \\
  k_{y} &= y_\text{periods} \\

4.2 :math:`\text{factor}_{y}^\text{fix}`
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

.. math:: \text{factor}_{y}^\text{fix} = factor_{y}^\text{var}

4.3 :math:`\text{factor}_{y}^\text{inv}`
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

.. image:: ./_static/invcost.png
  :width: 400
  :alt: Calculation of investment costs

Given weighted average cost of capital (WACC) (or interest rate) = :math:`i`, discount rate = :math:`r`, :math:`m`-th modeled year :math:`m` = :math:`y-y_\text{min}`, Length of :math:`m`-th planning periods = :math:`k`, Total present value are calculated as follows:

.. math::
  \text{Total present value} &= \frac{P}{(1+r)^m} \\
  & = \frac{\frac{A}{(1+i)} + \frac{A}{(1+i)^2} + \cdots + \frac{A}{(1+i)^n}}{(1+r)^m} \\
  & = A\frac{1-(1+i)^{-n}}{i}\times\frac{1}{(1+r)^m} \\
  \text{Then}& \\
  A &= P\frac{i}{1-(1+i)^{-n}} \\
  \text{Then}& \\
   \text{Capital recovery factor} &= \frac{i}{1-(1+i)^{-n}}

Only calculate the time periods that fall in the modeled time horizon (black color).  Calculated the length of time periods :math:`k = y_{max} - y`, calculated net present value are as follows:

.. math::
  \text{Calculated net present value} &= \frac{\frac{A}{(1+r)} + \frac{A}{(1+r)^2} + \cdots + \frac{A}{(1+r)^{min(n, k)}}}{(1+r)^m} \\
  \text{if }n \le k & \\
  & = \text{Total present value} \\
  \text{if }n > k & \\
   &= \frac{A\frac{1-(1+r)^{-k}}{r}}{(1+r)^m} = P\frac{i}{1-(1+i)^{-n}}\times\frac{1-(1+r)^{-k}}{r(1+r)^m} \\
  \text{Then}& \\
   factor_{y}^{inv} &= \frac{i}{1-(1+i)^{-n}}\times\frac{1-(1+r)^{-min(n,k)}}{r(1+r)^m}

5. Constraints
++++++++++++++++++++++

5.1 Retirement constraints
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

The model simply considers this part. At the beginning, the initial age can be set for the technology according to the capacity ratio. Each planning and scheduling period only considers the currently available capacity, that is, the existing capacity.

Calculate existing capacity of each technology (:math:`cap_{y,z,te}^{existing-tech}`) and existing capacity of transmission lines (:math:`cap_{y,z,te}^{existing-line}`) in each year each zone.

.. math::
  cap_{y, z, te}^{existing-tech} & = \sum_{lifetime-age<y-y_{min})}cap_{age,z,te}^{tech-init} + \sum_{(yy\le y) \& (lifetime>y-yy)}cap_{yy,z,te}^{tech-inv} \text{} \forall y,z,te \\
  cap_{y, z, te}^{existing-line} & = \sum_{lifetime-age<y-y_{min})}cap_{age,z,te}^{line-init} + \sum_{(yy\le y) \& (lifetime>y-yy)}cap_{yy,z,te}^{line-inv} \text{} \forall y,z,te \\

5.2 Carbon dioxide emission restriction
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

.. math::
  carbon_{y,te}^{tech} & = \sum_{t,m,z}Carbon_{y,z,te}\times gen_{t,m,y,z,te} \quad \forall y,te \\
    carbon_{y} & = \sum_{te}carbon_{y,te}^{tech} \forall y\\
    carbon_{y} & \le \overline{Carbon}_y \forall y

5.3 Power balance
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

.. math::
  Demand_{t,m,y,z} = & \sum_{z_s\neq z}import_{t, m, y, z_s, z} - \sum_{z_o\neq z}export_{t, m, y, z, z_o} + \\
                     & \sum_{te}gen_{t, m, y, z, te} - \sum_{te\in storage}charge_{t, m, y, z, te}\quad \forall t,m,y,te

5.4 Transmission loss constraints
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

.. math::
  export_{t, m, y, z_s, z_o} \times Effi_{z_s, z_o}^{trans} = import_{t, m, y, z_s, z_o} \quad \forall t,y,z_s\neq z_o

5.5 Maximum output constraint
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

.. math::
  gen_{t, m, y, z, te} \leq cap_{y, z, te}^{existing-tech} \forall t,m

5.6 Storage constraint
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

.. math::
  storage_{t,y,z, te}^{level} & = storage_{t-1,y,z, te}^{level} - \frac{gen_{t,y,z,te}}{Effi_{y,te}^{storage}} \quad \forall te \in storage, t,y,z \\
    storage_{t,y,z, te}^{level} & = Storage_{z, te}^{init} \quad \forall t,y=INI,z \\
    storage_{t,y,z}^{level} & = Storage_{z, te}^{end} \quad \forall t,y=END,z

5.7 Ramping constraint
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

.. math::
    gen^{up}_{t, m,y,z,te} & \le R^{up}_{te}\times cap_{y,z,te}^{existing-tech} \quad \forall t,m,y,z,te \\
    gen^{down}_{t,m,y,z,te} & \le R^{down}_{te}\times cap_{y,z,te}^{existing-tech} \quad \forall t,m,y,z,te \\
    gen^{up}_{t,m,y,z,te} - gen^{down}_{t,m,y,z,te} & = gen_{t,m,y,z,te} - gen_{t-1,m,y,z,te} \quad \forall t,m,y,z,te

Mathematical documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Continue here if you want to understand the formulation of the objective function and constraints of the model.
