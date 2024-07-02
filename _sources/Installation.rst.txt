.. _Installation:

Installation
============

This page provides instructions on how to install and use PREP-SHOT. The installation process is divided into the following steps:

Step 1: Download PREP-SHOT
++++++++++++++++++++++++++

Ensure you have downloaded the PREP-SHOT model from the `GitHub repository <https://github.com/PREP-NexT/PREP-SHOT>`_.

You may either clone the repository using the command:

.. code-block:: bash

    git clone https://github.com/PREP-NexT/PREP-SHOT.git

or download the repository as a zip file `here <https://github.com/PREP-NexT/PREP-SHOT/archive/refs/heads/main.zip>`__.

Step 2: Install conda
++++++++++++++++++++++++++++++++++++++

Conda is a package management tool that helps manage the Python packages required for PREP-SHOT. You can install `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ or 
`Anaconda <https://www.anaconda.com/download>`_ to use it. To verify that Conda has been installed successfully, you can run the ``conda -V`` command to check its version.

Step 3: Install dependencies
++++++++++++++++++++++++++++++

The ``prep-shot.yml`` file contains all the dependencies for the project (default install open-source solver `HiGHS`). You can use it to create a new environment for PREP-SHOT. This environment isolates the project and its dependencies from other Python projects to prevent package conflicts.

.. code:: bash

    cd PREP-SHOT
    conda env create -f prep-shot.yml
    conda activate prep-shot

Step 4: Run an example (Optional)
++++++++++++++++++++++++++++++++++

Once the environment is activated, you can run an example of :ref:`Tutorial` with the following command:

.. code:: bash

    python run.py

PREP-SHOT default solve models using open-source solver `HiGHS <https://highs.dev/>`_. also support commercial solvers, including `Gurobi <https://www.gurobi.com/features/academic-named-user-license/>`_, `COPT <https://www.copt.de/>`_ and `MOSEK <https://www.mosek.com/>`_. They offer academic licenses. To use these solvers, you need to install them and modify the solver in the `config.json` file.


Step 5: Run your own model
+++++++++++++++++++++++++++

You can prepare your input data referring to the example in the `input` and `southeast` folder. The detailed input data are introduced in the :ref:`Tutorial`. After preparing the input data, you can modify the `config.json` file to set the solver and other parameters. Then you can run your model with the following command:

.. code:: bash

    python run.py









