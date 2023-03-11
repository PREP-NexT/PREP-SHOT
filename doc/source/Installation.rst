Installation
==================

Installation Steps
-------------------


Step 1. Install Gurobi
++++++++++++++++++++
Gurobi is a solver known for its speed and efficiency, and it supports a free, full-featured academic license for students, faculty, and researchers. To obtain your free academic named-user license, you can follow  `Gurobi Instructions <https://www.gurobi.com/features/academic-named-user-license/>`_ on their website.

If you are using the High Performance Computing (HPC) system at the National University of Singapore (NUS), Gurobi is already installed. You can run the command ``module avail Gurobi`` to view available Gurobi.

.. code:: bash

    [username@atlas8-c01 ~]$ module avail Gurobi
    ---------------------  /app1/modules/centos6.3 --------------------
    Gurobi/8.0.0            Gurobi/8.0.1            Gurobi/9.5.1
    [username@atlas8-c01 ~]$ module load Gurobi/9.5.1
    [username@atlas8-c01 ~]$ gurobi_cl
    Set parameter TokenServer to value "lion11"
    Set parameter LogFile to value "gurobi.log"
    Using license file /app1/ia32-64/Gurobi/gurobi.lic

    Usuage: gurobi_cl [--command]* [param=value]* filename
    Type 'gurobi_cl --help' for more information.

Step 2. Install Miniconda
+++++++++++++++++++++++

Conda is a package management tool that can be used to manage all the required ``Python`` packages for PREP-SHOT. To get started, you can install Miniconda following offical `instructions <https://docs.conda.io/en/latest/miniconda.html>`_. 

If you are using HPC system, is typically already installed. You can run the command ``module avail miniconda`` to check if Miniconda is available. If Miniconda is installed, you can load it into your personal environment by running the command ``module load specific_conda_version`` instead of reinstalling it.

To verify that Conda is installed, you can run the command ``conda -V`` and the Conda version will be printed out.

.. code:: bash

    [username@atlas8-c01 ~]$ module avail miniconda
    ---------------------  /app1/modules/bioinfo --------------------
    miniconda/3.6            miniconda/3.8             miniconda/4.12
    [username@atlas8-c01 ~]$ module load miniconda/4.12
    [username@atlas8-c01 ~]$ conda -V 
    conda 4.12.0

Step 3. Create the Conda Environment
++++++++++++++++++++++++++++++++++++

The "prep-shot.yml" file contains all the project dependencies and can be used to create a Conda environment quickly. To create a new environment called "prep-shot", simply run the command ``conda env create -f prep-shot.yml``. Once the environment is installed, you can activate it by running the command ``conda activate prep-shot`` to activate the new ``prep-shot`` environment.

.. code:: bash

    [username@atlas8-c01 prepshot]$ conda env create -f prep-shot.yml
    Collecting package metadata (repodata.json): done
    Solving environment: done
    Downloading and Extracting Packages
    openssl-1.1.1s       | 1.9 MB    | ####################################### | 100% 
    python-3.7.13        | 40.7 MB   | ####################################### | 100% 
    setuptools-65.6.3    | 619 KB    | ####################################### | 100% 
    ...
    [username@atlas8-c01 prepshot]$ source activate prep-shot
    (prep-shot) [username@atlas8-c01 prepshot]$

.. note::
    
When you install the ``prep-shot`` environment, the ``gurobipy`` Python package will be installed by default. ``gurobipy`` is the Python package for the Gurobi Optimizer. If you have already installed the full-featured Gurobi license by following Step 1, you can use Gurobi to launch PREP-SHOT directly.

Step 4. Run a Model
+++++++++++++++++++++++

Once you have activated your environment, you can run your program directly by executing the command ``python run.py –storage=1``.
For HPC users who are using the PBS Job Scheduler, you will need to create a new bash script file called "prep-shot-1.sh" with the following contents:

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
    $CONDA_PREFIX/bin/python run.py --storage=1

After creating the "prep-shot-1.sh" bash script file, you can submit your job to the HPC cloud by running the command ``qsub prep-shot-1.sh``.

.. note::

To learn more about Job Submission and Management using the PBS Job Scheduler, you can refer to `HPC instructions <https://bobcat.nus.edu.sg/hpc/HPC/pbs/index.html>`_. You can also run the command ``hpc pbs help`` at any time after logging into the HPC cluster to access the instructions.

Troubleshooting
-------------------

If you encounter any issues during the installation process, please feel free to contact `LIU Zhanwei <liuzhanwei@u.nus.edu>`_.

Dependencies
-------------------

* ``Python`` 3.7
* ``pyomo`` 6.4 for building model
* ``numpy`` 1.21
* ``scipy`` 1.21 for interpolation
* ``pandas`` 1.3 for input and result data handling
* ``xarray`` 0.20 for result data handling and report generation

Features
-------------------

* ``PREP-SHOT`` is an optimization model based on linear programming for energy systems with multiple zones.
* Its objective is to find the energy system with the minimum cost to satisfy given demand time series.
* It is designed to operate on hourly-spaced time steps by default, but this can be configured.
* The input data is provided in an Excel file format, and the output data is generated in a NetCDF file format based on ``Xarray``.
* It supports multiple types of solvers, such as Gurobi, CPLEX, MOSEK, and GLPK, based on Pyomo.
* It allows for the input of multiple scenarios for specific parameters.
* It is a pure Python program that benefits from the use of pandas and xarray, which make complex data analysis code concise and extensible.
