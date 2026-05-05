.. _Tutorial:

Tutorial
=================

In this tutorial, we'll guide you through running your first PREP-SHOT model! This example will illustrate an electricity capacity expansion scenario.

.. seealso::

   For a hands-on walkthrough see the :doc:`Quickstart` notebook
   (3-zone synthetic dataset, 5-minute solve, includes a generation-mix
   plot and an LMP slice).

   For a realistic case study see
   `examples/southeast_asia/SoutheastAsia.ipynb <https://github.com/PREP-NexT/PREP-SHOT/blob/main/examples/southeast_asia/SoutheastAsia.ipynb>`_
   -- a walkthrough of the Lower Mekong dataset (5 countries, 57
   cascading hydropower stations, 2030 carbon cap).
   Open it directly on `Colab <https://colab.research.google.com/github/PREP-NexT/PREP-SHOT/blob/main/examples/southeast_asia/SoutheastAsia.ipynb>`_.

Scenario Background
-------------------

This scenario is inspired by real-world data, drawing primarily from the following resources:

* U.S. Energy Information Administration (`EIA <https://www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/regional/REG-NW>`_)
* U.S. Army Corps of Engineers (`USACE <https://www.nwd-wc.usace.army.mil/dd/common/dataquery/www/>`_)
* U.S. National Renewable Energy Laboratory (`NREL <https://atb.nrel.gov/electricity/2022/data>`_)

In this tutorial, we examine a cascading hydropower system, consisting of a network of 15 interconnected hydropower stations. We shall assume the presence of three balancing authorities (BAs) - BA1, BA2, and BA3. Each of these authorities will have distinct jurisdictional connections with their local reservoirs.

The jurisdictional connections of the stations, reservoirs, and balancing authorities are illustrated below:

.. figure:: ./_static/typology.jpg
   :width: 50 %
   :align: center
   :alt: typology

For this tutorial, we assume that, apart from hydropower, no other existing power generation technologies or transmission lines are in place.

However, we will be exploring the potential of incorporating four additional technologies into our grid:

* Coal-fired plants
* Wind power plants
* Solar power plants
* Energy storage plants

The objective of our scenario is to devise an electric mix pathway from 2020 to 2030 that enables the achievement of zero-carbon emissions. We shall use a 48-hour period as a representative sample for our analysis.
