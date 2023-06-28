.. _Installation:

Installation
============

This page provides instructions on how to install PREP-SHOT. 

.. contents::
    :local:
    :depth: 1

Standard Installation
----------------------

For users installing on a local machine or server.

Step 1: Install Gurobi
++++++++++++++++++++++

Gurobi is an optimization solver known for its speed and efficiency. You can obtain a free academic license by following `Gurobi Instructions <https://www.gurobi.com/features/academic-named-user-license/>`_.

Step 2: Install Miniconda
+++++++++++++++++++++++++

Miniconda is a package management tool that helps manage the Python packages required for PREP-SHOT. You can install it by following the official `instructions <https://docs.conda.io/en/latest/miniconda.html>`_.

To verify that Miniconda has been installed successfully, you can run the ``conda -V`` command to check its version.

Step 3: Create the Conda Environment
++++++++++++++++++++++++++++++++++++

The ``prep-shot.yml`` file contains all the dependencies for the project. You can use it to create a new environment for PREP-SHOT. This environment isolates the project and its dependencies from other Python projects to prevent package conflicts.

.. code:: bash

    conda env create -f prep-shot.yml
    conda activate prep-shot

Step 4: Run the Model
+++++++++++++++++++++

Once the environment is activated, you can run your program with the following command:

.. code:: bash

    python run.py

Installation on HPC Systems
----------------------------

For users installing on a High Performance Computing (HPC) system.

Step 1: Load Gurobi
+++++++++++++++++++

For users on the High Performance Computing (HPC) system at the National University of Singapore (NUS), Gurobi is already installed. You can load it with the following commands:

.. code:: bash

    module avail Gurobi
    module load Gurobi/9.5.1

Step 2: Load Miniconda
++++++++++++++++++++++

For users on the HPC system, Miniconda is typically already installed. You can load it with the following commands:

.. code:: bash

    module avail miniconda
    module load miniconda/4.12

Step 3: Create the Conda Environment
++++++++++++++++++++++++++++++++++++

Similar to the standard installation, use the ``prep-shot.yml`` file to create a new environment for PREP-SHOT.

.. code:: bash

    conda env create -f prep-shot.yml
    conda activate prep-shot

Step 4: Run the Model
+++++++++++++++++++++

For HPC users, you need to create a bash script file (e.g., ``prep-shot-1.sh``) to submit your job to the HPC cloud.

.. code:: bash

    #PBS -N PREP-SHOT-1
    #PBS -l select=1:ncpus=24:mem=120gb
    #PBS -q parallel24
    #PBS -l walltime=240:0:0
    #PBS -o ./log/prep-shot-1.out
    #PBS -e ./log/prep-shot-1.err

    cd ${PBS_O_WORKDIR}
    np=$(cat ${PBS_NODEFILE} | wc -l)
    source /etc/profile.d/rec_modules.sh
    bash ~/.bashrc
    module load miniconda/4.12
    module load Gurobi/9.5.1
    source activate prep-shot
    $CONDA_PREFIX/bin/python run.py

To submit your job, use the following command:

.. code:: bash

    qsub prep-shot-1.sh

Manual Installation
-------------------

For users who prefer to manually install Python packages.

Step 1: Install Python
++++++++++++++++++++++

Ensure Python 3.7 is installed on your machine. You can download Python 3.7 from the official Python `website <https://www.python.org/downloads/release/python-370/>`_.

Step 2: Install Gurobi
++++++++++++++++++++++

Gurobi is an optimization solver known for its speed and efficiency. You can obtain a free academic license by following `Gurobi Instructions <https://www.gurobi.com/features/academic-named-user-license/>`_.

Step 3: Install Packages
++++++++++++++++++++++++

You can manually install each package using pip, Python's package installer. Execute the following commands:

.. code:: bash

    pip install gurobipy==9.5.1
    pip install numpy==1.21.6   
    pip install openpyxl==3.0.9
    pip install pandas==1.3.5
    pip install pyomo==6.4.0
    pip install scipy==1.7.3
    pip install xarray==0.20.2

Step 4: Run the Model
+++++++++++++++++++++

Once all the packages are installed, you can run your program with the following command:

.. code:: bash

    python run.py

Troubleshooting
---------------

For any issues encountered during the installation process, please contact `LIU Zhanwei <liuzhanwei@u.nus.edu>`_.
