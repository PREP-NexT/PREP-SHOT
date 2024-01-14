.. _Installation:

Installation
============

This page provides instructions on how to install and use PREP-SHOT. The installation process is divided into the following steps:

Step 1: Install Gurobi
++++++++++++++++++++++

Gurobi is an optimization solver known for its speed and efficiency. You can obtain a free academic license by following `Gurobi Instructions <https://www.gurobi.com/features/academic-named-user-license/>`_.

Step 2: Install Miniconda
+++++++++++++++++++++++++

Miniconda is a package management tool that helps manage the Python packages required for PREP-SHOT. You can install it by following the official `instructions <https://docs.conda.io/en/latest/miniconda.html>`_.

To verify that Miniconda has been installed successfully, you can run the ``conda -V`` command to check its version.

Step 3: Download PREP-SHOT
++++++++++++++++++++++++++

Ensure you have downloaded the PREP-SHOT model from the `GitHub repository <https://github.com/PREP-NexT/PREP-SHOT>`_.

You may either clone the repository using the command:

.. code-block:: bash

    git clone https://github.com/PREP-NexT/PREP-SHOT.git

or download the repository as a zip file `here <https://github.com/PREP-NexT/PREP-SHOT/archive/refs/heads/main.zip>`__.

Step 4: Create the Conda Environment
++++++++++++++++++++++++++++++++++++

The ``prep-shot.yml`` file contains all the dependencies for the project. You can use it to create a new environment for PREP-SHOT. This environment isolates the project and its dependencies from other Python projects to prevent package conflicts.

.. code:: bash

    conda env create -f prep-shot.yml
    conda activate prep-shot

Step 5: Run the Model
+++++++++++++++++++++

Once the environment is activated, you can run an example with the following command:

.. code:: bash

    python run.py
