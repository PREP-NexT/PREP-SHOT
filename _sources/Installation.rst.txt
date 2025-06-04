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

Step 2: Install dependencies
++++++++++++++++++++++++++++++

Assuming you have already `installed Python <https://www.python.org/downloads/>`_, the ``requirements.txt`` file contains all the dependencies for the project (default install open-source solver `HiGHS`). I also recommend `create a new environment <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`_ for PREP-SHOT and installing the dependencies within the new environement. This approach isolates the project and its dependencies, helping to prevent conflicts with other Python projects.

.. code:: bash

    cd PREP-SHOT
    conda create -n prep-shot python=3.8
    conda activate prep-shot
    pip install -r requirements.txt

Step 3: Run an example (Optional)
++++++++++++++++++++++++++++++++++

Once the environment is activated, you can run an example of :ref:`Tutorial` with the following command:

.. code:: bash

    python run.py

You can also run examples using Jupyter notebooks located in the `./example/` directory.

PREP-SHOT default solve models using open-source solver `HiGHS <https://highs.dev/>`_. also support commercial solvers, including `Gurobi <https://www.gurobi.com/features/academic-named-user-license/>`_, `COPT <https://www.copt.de/>`_ and `MOSEK <https://www.mosek.com/>`_. They offer academic licenses. To use these solvers, you need to install them and modify the solver in the `config.json` file.


Step 4: Run your own model
+++++++++++++++++++++++++++

You can prepare your input data referring to the example in the `input` and `southeast` folder. The detailed input data are introduced in the :ref:`Tutorial`. After preparing the input data, you can modify the `config.json` file to set the solver and other parameters. Then you can run your model with the following command:

.. code:: bash

    python run.py









