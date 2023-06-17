.. module:: PREP-SHOT

Welcome to the PREP-SHOT Documentation
=======================================

:Author: `Zhanwei Liu <https://www.researchgate.net/profile/Zhanwei-Liu-4>`_ (Mr), <liuzhanwei@u.nus.edu> and `Xiaogang He <http://hydro.iis.u-tokyo.ac.jp/~hexg/>`_ (Dr), <hexg@nus.edu.sg>
:Organization: `National University of Singapore <https://nus.edu.sg/>`_
:Version: |release|
:Date: |today|
:Copyright:  The model code is licensed under the `GNU General Public License 3.0 <https://github.com/PREP-NexT/PREP-SHOT/blob/main/LICENSE>`_. This documentation is licensed under a `Creative Commons Attribution 4.0 International <http://creativecommons.org/licenses/by/4.0/>`_ license.

Overview
--------
**PREP-SHOT** (**P**\ athways for **R**\ enewable **E**\ nergy **P**\ lanning coupling **S**\ hort-term **H**\ ydropower **O**\ pera\ **T**\ ion) is a transparent, modular, and open-source energy expansion model hosted on `GitHub <https://github.com/PREP-NexT/PREP-SHOT>`_. Offering advanced solutions for multi-scale, intertemporal, and cost-effective expansion of energy systems and transmission lines.

The model sets itself apart from existing energy expansion models through its deeper consideration of hydropower processes. While models such as `urbs <https://urbs.readthedocs.io/en/latest/>`_ might treat hydropower as fixed processes, and others like `GenX <https://genxproject.github.io/GenX/dev/>`_ and `PLEXOS <https://www.energyexemplar.com/plexos>`_ may not fully capture the dynamic nature of water heads or consolidate multiple hydropower stations into a single unit, PREP-SHOT is uniquely designed to address these oversights.

Our model explicitly considers the plant-level water head dynamics (i.e., time-varying water head and storage) and the system-level network topology of all hydropower stations within a regional grid. This results in a more accurate reflection of the multi-scale dynamic feedbacks between hydropower operation and energy system expansion. Furthermore, it enables the realistic simulation of the magnitude and spatial-temporal variability of hydropower output, particularly in regions with a large number of cascade hydropower stations.

With PREP-SHOT, we aim to answer key questions related to the future of energy planning and utilization:

* How can we effectively plan an energy portfolio and new transmission capacity under deep uncertainty?
* How can we quantify the impacts of variable hydropower on the generation and capacity of future energy portfolios?

How It Works
------------

.. figure:: ./_static/overview.png
   :width: 100 %
   :alt: overview of PREP-SHOT

Key Features
------------
* PREP-SHOT is an optimization model based on linear programming for energy systems with multiple zones.
* It aims to minimize costs while meeting the given demand time series.
* By default, it operates on hourly-spaced time steps, but this can be adjusted.
* The input data is in Excel format, while output data is generated in a NetCDF format using ``Xarray``.
* It supports multiple types of solvers such as Gurobi, CPLEX, MOSEK, and GLPK via `Pyomo <https://pyomo.readthedocs.io/en/stable/solving_pyomo_models.html>`_.
* It allows input of multiple scenarios for specific parameters.
* As a pure Python program, it benefits from the use of ``pandas`` and ``Xarray``, simplifying complex data analysis and promoting extensibility.

Let's Get Started
-----------------
We've prepared a comprehensive guide to help you understand and use PREP-SHOT efficiently. Explore the sections below to learn more:

.. toctree::
   :maxdepth: 2

   Installation
   Getting_started
   User_guide
   Tutorial
   Mathematical_notations
   Changelog
