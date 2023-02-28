Getting Started
=====================

Introduction to PREP-SHOT
--------------------------

This article is here to introduce some basic concepts which help you to verify whether PREP-SHOT might be a good fit for you. This is only an overview of features. We will cover many more details of features in other parts of this documentation.

What can the model do?
+++++++++++++++++++++++

PREP-SHOT is an a transparent, modular, and open-source energy expansion model designed to support the multi-scale, intertemporal cost-effective expansion of energy systems and transmission lines. You can use it to answer the following question:

* How to plan an energy portfolio and new transmission capacity for the future (i.e. new-built, retirement) under deep uncertainty?
* Quantifying the impacts of variable hydropower on generation and capacity of future energy portfolio?

.. note:: The PREP-SHOT is an linear programming model unless you plan to expand reservoirs
          to reduce the computational burden of the model. You can read more on that here: :ref:`Users_guide`.

How does it work?
++++++++++++++++++

PREP-SHOT was initially developed to investigate the nexus of water and energy. Its
development started in 2021, and was open-source release in 2022.

Some examples of model created by xxx.


You can find many more examples in the xxx.

What do I need to know to use PREP-SHOT?
+++++++++++++++++++++++++++++++++++++++++

PREP-SHOT has many features and there is a lot to learn. But we already try to make the model accessible, you do not need good programming foundations to make the most of it. 

PREP-SHOT relies on the object-oriented programming paradigm. Being comfortable with
concepts such as classes and objects will help you add custom functions efficiently in it.

Cost Source
--------------

Electricity Generation Costs = Investment [$/kW](Overnight Capital Costs) + Fixed O&M [$/kW] (e.g., Insurance and Taxes) + Variable O&M [$/kWh] (Fuel + Other O&M)

Model concept
--------------

The energy expansion model mainly aims to answer the following question:

* How to plan an energy portfolio and new transmission capacity for the future? 
* When, which, where should be new build?

How much electricity can per unit of fuel (coal, natural gas, oil, natural uranium et al.) produce?

The amount of fuel used to generate electricity depends on the efficiency (or `heat rate <https://en.wikipedia.org/wiki/Heat_rate_(efficiency)>`_) of the power plant and the `heat content <https://en.wikipedia.org/wiki/Heat_of_combustion>`_ of the fuel.

.. math::
    \text{Heat Rate} = \frac{\text{Thermal Energy In}}{\text{Electrical Energy Out}}

which is the inverse of the efficiency and a lower heat rate is better. A 100% efficiency implies equal input and output: for 1 kWh of output, the input is 1 kWh. This thermal energy input of 1 kWh = 3.6 MJ = 3,412 Btu. Therefore, the heat rate of a 100% efficient plant is simply 1, or 1 kWh/kWh, or 3.6 MJ/kWh, or 3,412 Btu/kWh. To express the efficiency of a generator or power plant as a percentage, divide the equivalent Btu content of a kWh of electricity (3,412 Btu) by the heat rate. For example, if the heat rate is 10,500 Btu, the efficiency is 33%. If the heat rate is 7,500 Btu, the efficiency is 45%.

heat content = The efficiency of coal-fired power generators is about 40 percentthe limited by laws of thermodynamics.
Heat rate = According to `EIA <https://www.eia.gov/tools/faqs/faq.php?id=667&t=2>`_. 
Heat rate measures the efficiency of a generator or power plant and is based on the amount of energy used to generate one kilowatt of electricity. Heat rates (power plant efficiencies) depend on generator type, power plant emission controls, and some other factors. One metric ton of coal can generate 1,927 kilowatt hours of electricity, in comparison to 1,000 cubic feet of natural gas which can generate 99 kilowatt hours.  
