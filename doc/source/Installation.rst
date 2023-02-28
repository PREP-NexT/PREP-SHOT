Installation
==================

Installation Steps
-------------------


1. Install Gurobi
++++++++++++++++++++
Gurobi is taken as a fastest solver which supports a free, full-featured academic license for students, faculty, and researchers. You can follow  `Gurobi instructions <https://www.gurobi.com/features/academic-named-user-license/>`_ to obtain your free academic named-user license.

If you are using High Performance Computing (HPC) of National University of Singapore (NUS), Gurobi was already installed. You run command ``module avail Gurobi`` to view available Gurobi.

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

2. Install Miniconda
+++++++++++++++++++++++

Conda is a package management tool which can help you manage all required ``Python`` packages of PREP-SHOT. Install Miniconda following offical `instructions <https://docs.conda.io/en/latest/miniconda.html>`_. 

If you are using HPC, Miniconda was usually already installed. You run command ``module avail miniconda`` to check if existing avail Miniconda. If HPC has installed Miniconda, you run command ``module load specific_conda_version`` to load Miniconda to your personal environment instead of reinstalling it. 

To verify that conda is installed, run command ``conda -V``. Conda version will be printed out.

.. code:: bash

    [username@atlas8-c01 ~]$ module avail miniconda
    ---------------------  /app1/modules/bioinfo --------------------
    miniconda/3.6            miniconda/3.8             miniconda/4.12
    [username@atlas8-c01 ~]$ module load miniconda/4.12
    [username@atlas8-c01 ~]$ conda -V 
    conda 4.12.0

3. Create the Conda Environment
++++++++++++++++++++++++++++++++++++

The prep-shot.yml file is provided to readily to create conda environment including all project dependencies. Run command ``conda env create -f prep-shot.yml`` to create a new envirnoment called prep-shot. Once installed, run command ``conda activate prep-shot`` to activate the new ``prep-shot`` environment.

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
    The installation of the ``prep-shot`` environment also will install ``gurobipy`` by default, which is Python package of the Gurobi Optimizer. If you already install full-featured license following first step, you can directly use gurobi to launch PREP-SHOT.


4. Run a Model
+++++++++++++++++++++++

After activating your envirnoment, you can directly run your program by running command ``python run.py –storage=1``.

For HPC user (PBS Job Scheduler), you first need to create a new bash script file (prep-shot-1.sh) with the following contents.

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

Then you run the commond ``qsub prep-shot-1.sh`` to submit your Job in HPC Cloud. 

.. note::
    To know more commands about Job Submission and Management using PBS Job Scheduler to refer `HPC instructions <https://bobcat.nus.edu.sg/hpc/HPC/pbs/index.html>`_. You can also check above instructions by run command ``hpc pbs help`` after log into HPC cluster at anytime.

Troubleshooting
-------------------

Sometimes the installation doesn’t always go as planned. If you experience any issues concat `LIU Zhanwei <liuzhanwei@u.nus.edu>`_.

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

* ``PREP-SHOT`` is a linear programming optimization model for multi-zone energy
  systems.
* It finds the minimum cost energy system to satisfy given demand timeseries.
* By default, operates on hourly-spaced timesteps (configurable).
* Excel file as input and NetCDF file as output data (based on ``Xarray``)
* Support multiple kind of solvers (Gurobi, CPLEX, MOSEK and GLPK ..., based on Pyomo)
* Support multiple scenarios input for specific parameters
* Pure Python program
* Thanks to ``pandas`` and ``xarray``, complex data analysis code is short and extensible.
