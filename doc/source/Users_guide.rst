.. _Users_guide:

Users guide
==============

The following sections will give a general overview and help you getting started from after
the installation.

Prepare inputs
-----------------

.. list-table:: Input files
   :widths: 10 10 80
   :header-rows: 1
   
   * - Parameters
     - Dimension
     - Description
   * - technology portfolio
     - 2D (year, zone)
     - Existing installed capacity of technologies across each zone (or bus) at the beginning of the reference year, showcasing status quo in those areas. 
   * - distance
     - 2D (zone1, zone2)
     - Distance between two zones.
   * - transmission line
     - 2D (zone1, zone2)
     - The existing capacity of transmission lines between `zone1` and `zone2` represents the current ability to transmit power between these two zones. If you leave this parameter as null, the model will not consider any expansion of the capacity between the corresponding zones except for you set this parameter to a value equal to or greater than zero.
   * - transline efficiency
     - 2D (zone1, zone2)
     - The transmission efficiency between `zone1` and `zone2` represents the effectiveness of power transfer through transmission lines connecting these zones. It is used to consider transmission losses, which are calculated as follows: transmission loss = transferred electricity * (1 - transmission line efficiency).
   * - discount factor
     - 1D (year)
     - It is a weighting factor that is used to calculate the present value. Refer to explaination `here <https://www.wallstreetprep.com/knowledge/discount-factor/>`_.
   * - technology fixed cost
     - 2D (year, technology)
     - The fixed Operation and Maintenance (O&M) cost of technologies for each year refers to the expenses associated with the regular upkeep and management of energy generation systems, regardless of their generation, expressed on a per-unit basis. These costs typically include routine maintenance, inspections, repairs, and personnel expenses necessary for the safe and efficient operation of the facility.
   * - technology variable cost
     - 2D (year, technology)
     - The variable Operation and Maintenance (O&M) cost of technologies for each year refers to the expenses that vary according to the electricity generation, expressed on a per-unit basis.
   * - technology investment cost
     - 2D (year, technology)
     - 
   * - carbon content
     - 2D (year, technology)
     - 
   * - fuel price
     - 2D (year, technology)
     -
   * - efficiency in
     - 2D (year, storage technology)
     - The efficiency here is mainly for the type of energy storage. It refers to the charge efficiency of the storage source (i.e., change of storage = efficiency :math:`\times` charge). Refer to explaination `here <https://www.sciencedirect.com/topics/engineering/round-trip-efficiency>`_.
   * - efficiency out
     - 2D (year, storage technology)
     - The efficiency here is mainly for the type of energy storage. It refers to the discharge efficiency of the storage source (i.e., change of storage = efficiency :math:`\times` discharge).
   * - energy power ratio
     - 1D (storage technology)
     -
   * - lifetime
     - 2D (year, technology)
     -  
   * - transmission line lifetime
     - 
     - 
   * - capacity factor
     - 5D (technology, zone, year, month, hour)
     -
   * - demand
     - 5D (technology, zone, year, month, hour)
     - 
   * - ramp up
     - 1D (technology)
     - The ramp up (i.e., ramping up speed) refers to the rate at which the plant's output power is increased from a lower level to a higher level. Here, it is measured in ratio of current available capacity power and unit is megawatts per hour. The ramping speed of a plant is a crucial factor in determining the plant's operational ability to respond quickly to changes in demand for electricity or intermittent energy (such wind and solar energy). Refer to explaination `here <https://www.nrel.gov/docs/fy20osti/77639.pdf>`_.
   * - ramp down
     - 1D (technology)
     - Same as the ramp up. It refers to the rate at which the plant's output power is decreased from a higher level to a lower level.
   * - carbon
     - 1D (year)
     - 
   * - transmission line investment cost
     -
     - 
   * - transmission line fixed cost
     - 
     - 
   * - transmission line variable cost
     - 
     -    
   * - technology upper bound
     -
     - 
   * - new technology upper bound
     -
     - 
   * - new technology lower bound
     - 
     - 
   * - init storage level
     -
     - 
   * - zv
     -
     - elevation - storage relationship of reservoir
   * - zq
     -
     - tailrace - discharge relationship of reservoir
   * - type
     - 1D (technology)
     -
   * - age
     -
     -
   * - storage upper bound
     -
     -   
   * - storage lower bound
     -
     -
   * - initial storage
     -
     -
   * - terminal storage
     -
     -
   * - hydropower
     -
     -
   * - inflow
     - 4D (station, year, month, hour) 
     - Natural local inflow between upstream and downstream reservoirs.
   * - connect
     -
     -
   * - static
     -
     -

Note: `inf` means Infinity. If you set inf which means no upper bound. `None` means null value for current item.

Run model
----------------

Scenarios
####################

Here I want to talk about how to run PREP-SHOT with multiple-year inflow. First, you need to download scripts in `prepshot-my-flow` branch. Then you need to prepare an individual inflow input file called "input/scenario/inflow_xxx.xlsx". Here "xxx" is the name of the scenario, which need to be the same as the command line `inflow` parameter which will be introduced below. The required inflow input file takes the representative year as the name of the sheet table. For each sheet, you only need to maintain the same format as the `inflow` sheet in the previous total input file.   

After preparing the inflow input files, you must use the command line parameter to specify the scenario name. For example, you design an inflow called drought. You need to prepare an inflow input file called "inflow_drough.xlsx" and then run your scenario with the following shell command `python run.py -- inflow=drought`.

Read output
--------------
The output of the model is stored in a NetCDF file, please refer to the `simple tutorial <https://xiaoganghe.github.io/python-climate-visuals/chapters/data-analytics/xarray-basic.html>`_ and `official documentation <https://docs.xarray.dev/en/stable/>`_ of Xarray for how to manipulate the NetCDF file.

