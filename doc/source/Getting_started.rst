Getting Started
===============

Introduction to PREP-SHOT
-------------------------

This introductory guide provides an overview of what this model can do and how it works, enabling you to gauge if PREP-SHOT fits your needs. 

Origins
+++++++

PREP-SHOT was orginally developed to study the nexus between water and energy systems. The development started in 2021, and in 2022, it was released as an open-source model.

The various examples of models created by xxx can be found in the xxx.

Model Capabilities
+++++++++++++++++++

PREP-SHOT is specifically designed to help facilitate the cost-effective, multi-scale, and intertemporal expansion of energy systems and transmission lines. You can use PREP-SHOT to address the following questions:

* How to plan an energy portfolio and new transmission capacity for the future (i.e., new-built, retirement) under deep uncertainty?
* How to quantify the impacts of variable hydropower on the generation and capacity of future energy portfolios?

.. note:: While primarily a linear programming model, PREP-SHOT can also handle the expansion of reservoirs to reduce computational load. More on this topic can be found here: :ref:`Users_guide`.

User Prerequisites
++++++++++++++++++

PREP-SHOT is designed to be accessible and user-friendly, even for users with no strong programming background. However, a basic understanding of object-oriented programming concepts, such as classes and objects, is useful to add custom functions to the model.

Model Concepts
--------------

Understanding Energy Expansion
++++++++++++++++++++++++++++++

The energy expansion model is designed to answer several critical questions:

* How to plan an energy portfolio and new transmission capacity for the future?
* When, where, and which components should be constructed as part of the new build?
* How much electricity can be generated per unit of fuel (such as coal, natural gas, oil, and natural uranium)?

The amount of fuel required to generate electricity is influenced by various factors, including the efficiency (or alternatively, the `Heat Rate <https://en.wikipedia.org/wiki/Heat_rate_(efficiency)>`__) of the power plant and the `Heat Content <https://en.wikipedia.org/wiki/Heat_of_combustion>`_ of the fuel.

Efficiency and Heat Rate
++++++++++++++++++++++++

The `Heat Rate <https://www.eia.gov/tools/faqs/faq.php?id=667&t=2>`__, as defined by EIA, is a measure of a generator or power plant's efficiency. It's based on the amount of energy used to generate one kilowatt of electricity:

.. math::

    \text{Heat Rate} = \frac{\text{Thermal Energy In}}{\text{Electrical Energy Out}}

* Lower values of Heat Rate indicates higher efficiency.
* A power plant with a Heat Rate of 1 kWh/kWh (or 3.6 MJ/kWh, or 3,412 Btu/kWh) is 100% efficient.
    
    * This means the energy input required to produce 1 kWh of electricity equals exactly 1 kWh.

Heat Content
++++++++++++

The heat content of a fuel source refers to the amount of energy that can be extracted from it. For example, while coal has a high heat content, the efficiency of coal-fired power generators is limited by thermodynamics laws, resulting in a maximum efficiency of around 40%.

Model Calculations
------------------

Electricity Generation Costs
++++++++++++++++++++++++++++

The cost of generating electricity is computed using the following formula:

.. code::

    Electricity Generation Costs = Investment + Fixed O&M + Variable O&M

.. note::

    * **Investment** refers to the overnight capital cost.
    * **Fixed Operating & Maintenance** refers to fixed costs such as insurance and taxes.
    * **Variable Operating & Maintenance** refers to variable costs such as fuel.

Power Plant Efficiency
++++++++++++++++++++++

The efficiency of a power plant is calculated as a percentage. It's done by dividing the equivalent Btu content of a kWh of electricity (which is 3,412 Btu) by the heat rate. Let's illustrate this with a couple of examples:

Example 1:
    If the Heat Rate is 10,500 Btu, the efficiency would be calculated as follows::

        Efficiency = (3,412 Btu / 10,500 Btu) x 100 = 32.5%

Example 2:
    If the Heat Rate is 7,500 Btu, the efficiency would be calculated as follows::

        Efficiency = (3,412 Btu / 7,500 Btu) x 100 = 45.5%

Hence, understanding Heat Rate and its relationship with Efficiency is crucial for optimizing power plant operations and designing an efficient energy system.
