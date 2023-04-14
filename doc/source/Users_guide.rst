.. _Users_guide:

Users guide
==============

The following sections will give a general overview and help you getting started from after
the installation.

Prepare inputs
-----------------

.. list-table:: Input files
   :widths: 10 10 10 10 10 50
   :header-rows: 1

   * - Parameters
     - Dimension 
     - Default value
     - Type
     - Range
     - Description
   * - discount factor
     - 1-D (year)
     - 0.07
     - Continuous
     - 0 - 1
     - It is a weighting factor that is used to calculate the present value. Refer to explaination `here <https://www.wallstreetprep.com/knowledge/discount-factor/>`_.
   * - Inflow
     - 3-D (month, hour & station) 
     - None
     - Continuous
     - None
     - Natural local inflow between upstream and downstream reservoirs.
   * - efficiency-in
     - 1-D (year)
     - 0.87 (pumped hydro storage)
     - Continuous
     - 0 - 1
     - The efficiency here is mainly for the type of energy storage. It refers to the charge efficiency of the storage source (i.e., change of storage = efficiency :math:`\times` charge). Refer to explaination `here <https://www.sciencedirect.com/topics/engineering/round-trip-efficiency>`_.
   * - efficiency-out
     - 1-D (year)
     - 0.87 (pumped hydro storage)
     - Continuous
     - 0 - 1
     - The efficiency here is mainly for the type of energy storage. It refers to the discharge efficiency of the storage source (i.e., change of storage = efficiency :math:`\times` discharge).
   * - ramp up
     - 1-D (technology)
     - 0.35 (Coal)
     - Continuous
     - 0 - 1
     - The ramp up (i.e., ramping up speed) refers to the rate at which the plant's output power is increased from a lower level to a higher level. Here, it is measured in ratio of current available capacity power and unit is megawatts per hour. The ramping speed of a plant is a crucial factor in determining the plant's operational ability to respond quickly to changes in demand for electricity or intermittent energy (such wind and solar energy). Refer to explaination `here <https://www.nrel.gov/docs/fy20osti/77639.pdf>`_.
   * - ramp down
     - 1-D (technology)
     - 0.35 (Coal)
     - Continuous
     - 0 - 1
     - Same as the ramp up. It refers to the rate at which the plant's output power is decreased from a higher level to a lower level.

Note: `inf` means Infinity. If you set inf which means no upper bound. `None` means null value for current item.

Run model
----------------

Scenarios
####################

Here I want to talk about how to run PREP-SHOT with multiple-year inflow. First, you need to download scripts in `prepshot-my-flow` branch. Then you need to prepare an individual inflow input file called "input/scenario/inflow_xxx.xlsx". Here "xxx" is the name of the scenario, which need to be the same as the command line `inflow` parameter which will be introduced below. The required inflow input file takes the representative year as the name of the sheet table. For each sheet, you only need to maintain the same format as the `inflow` sheet in the previous total input file.   

After preparing the inflow input files, you must use the command line parameter to specify the scenario name. For example, you design an inflow called drought. You need to prepare an inflow input file called "inflow_drough.xlsx" and then run your scenario with the following shell command `python run.py -- inflow=drought`.

Read output
--------------
