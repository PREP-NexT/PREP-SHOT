.. _Tutorial:

Tutorial
========

In this tutorial, we'll guide you through running your first PREP-SHOT model! This example will illustrate an electricity capacity expansion scenario.

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
   :alt: typology

For this tutorial, we assume that, apart from hydropower, no other existing power generation technologies or transmission lines are in place.

However, we will be exploring the potential of incorporating four additional technologies into our grid:

* Coal-fired plants
* Wind power plants
* Solar power plants
* Energy storage plants

The objective of our scenario is to devise an electric mix pathway from 2020 to 2030 that enables the achievement of zero-carbon emissions. We shall use a 48-hour period as a representative sample for our analysis.

Run the Model
-------------

Step 1: Download PREP-SHOT
++++++++++++++++++++++++++

Ensure you have downloaded the PREP-SHOT model from the `GitHub repository <https://github.com/PREP-NexT/PREP-SHOT>`_.

You may either clone the repository using the command:

.. code-block:: bash

    git clone https://github.com/PREP-NexT/PREP-SHOT.git

or download the repository as a zip file `here <https://github.com/PREP-NexT/PREP-SHOT/archive/refs/heads/main.zip>`__.

Step 2: Create the Conda Environment
++++++++++++++++++++++++++++++++++++

Navigate to the root directory of the PREP-SHOT model and create a conda environment with the required packages:

.. code-block:: bash

    conda env create -f prep-shot.yml

Activate the newly-created conda environment:

.. code-block:: bash

    conda activate prep-shot

Step 3: Download Input Files
++++++++++++++++++++++++++++

If you have followed the instructions in Step 1, you may omit this step, as the input files for this tutorial are already included in the repository.

Otherwise, download the input files for this tutorial from `here <./_static/input.zip>`__.

Extract the contents of the zip file and place all the data files *(in .xlsx)* into the ``input`` folder of the PREP-SHOT model.

.. note:: The ``input`` folder will be used to store all input files *(in .xlsx)* for the model to run your scenarios.

Step 4: Run the Model
+++++++++++++++++++++

Finally, launch the model by running the following command in the root directory of the PREP-SHOT model.

.. code-block:: bash

    python run.py
