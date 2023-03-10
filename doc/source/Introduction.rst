Getting Started
=====================

Introduction to PREP-SHOT /ˈprɛpʃɒt/
--------------------------

This article aims to introduce some basic concepts that can help you determine whether PREP-SHOT might be a good fit for your needs. Please note that this is only an overview of the features, and we will cover many more details in other parts of this documentation.

What can the model do?
+++++++++++++++++++++++

PREP-SHOT is a transparent, modular, and open-source energy expansion model. It is specifically designed to help facilitate the cost-effective, multi-scale, and intertemporal expansion of energy systems and transmission lines. You can use PREP-SHOT to address the following questions:

* How to plan an energy portfolio and new transmission capacity for the future (i.e. new-built, retirement) under deep uncertainty?
* How to quantify the impacts of variable hydropower on the generation and capacity of future energy portfolios?

.. note:: PREP-SHOT is primarily a linear programming model unless you plan to expand reservoirs
          to reduce the computational burden of the model. You can read more about this topic here: :ref:`Users_guide`.

How does it work?
++++++++++++++++++

PREP-SHOT was originally developed to study the nexus of water and energy. Its development began in 2021, and it was released as an open-source model in 2022.

Some examples of the model created by xxx.


You can find many more examples in the xxx.

What do I need to know to use PREP-SHOT?
+++++++++++++++++++++++++++++++++++++++++

While PREP-SHOT has many features that may require some learning, we have designed the model to be accessible and user-friendly, even if you don't have a strong programming background. However, being familiar with object-oriented programming concepts such as classes and objects can help you efficiently add custom functions to the model. 

Cost Source
--------------

Electricity Generation Costs = Investment [$/kW](Overnight Capital Costs) + Fixed O&M [$/kW] (e.g., Insurance and Taxes) + Variable O&M [$/kWh] (Fuel + Other O&M)

Model concept
--------------

The energy expansion model mainly aims to answer the following question:

* How to plan an energy portfolio and new transmission capacity for the future? 
* When, where, and which components should be constructed as part of the new build?
* How much electricity can be produced per unit of fuel (such as coal, natural gas, oil, and natural uranium)?

The amount of fuel required to generate electricity is influenced by various factors, including the efficiency (or alternatively, the `heat rate <https://en.wikipedia.org/wiki/Heat_rate_(efficiency)>`_) of the power plant and the `heat content <https://en.wikipedia.org/wiki/Heat_of_combustion>`_ of the fuel.  

Heat Rate
According to `EIA <https://www.eia.gov/tools/faqs/faq.php?id=667&t=2>`_,
Heat Rate measures the efficiency of a generator or power plant and is based on the amount of energy used to generate one kilowatt of electricity, which can be expressed as: 

.. math::
    \text{Heat Rate} = \frac{\text{Thermal Energy In}}{\text{Electrical Energy Out}}

with lower values indicating higher efficiency. For instance, a plant with a Heat Rate of 1 kWh/kWh (or 3.6 MJ/kWh, or 3,412 Btu/kWh) would be considered 100% efficient, meaning that the amount of energy input required to produce 1 kWh of electricity is exactly 1 kWh.

Efficiency of a pwer plant
To express the efficiency of a power plant as a percentage, we can divide the equivalent Btu content of a kWh of electricity (which is 3,412 Btu) by the Heat Rate. For example, if the Heat Rate is 10,500 Btu, the efficiency would be 32.5% (i.e., 3,412 Btu/10,500 Btu = 0.325). On the other hand, if the Heat Rate is 7,500 Btu, the efficiency would be 45.5% (i.e., 3,412 Btu/7,500 Btu = 0.455). Therefore, understanding the Heat Rate and its relationship with efficiency is crucial for optimizing power plant operations and designing sustainable energy systems.

Heat Content
The amount of energy that can be extracted from a fuel source is often referred to as its heat content. For coal, the heat content is relatively high, but the efficiency of coal-fired power generators is limited by the laws of thermodynamics, resulting in a maximum efficiency of around 40%.

 
