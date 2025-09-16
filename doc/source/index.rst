.. module:: PREP-SHOT

Welcome to the PREP-SHOT Documentation
=======================================

:Authors: `Zhanwei Liu <https://scholar.google.com/citations?user=Zub5y2IAAAAJ>`_ (liuzhanwei@u.nus.edu), `Xiaogang He <http://hydro.iis.u-tokyo.ac.jp/~hexg/>`_ (hexg@nus.edu.sg)
:Contributors: `Bo Xu <http://faculty.dlut.edu.cn/xubo12/zh_CN/index.htm>`_ (xubo_water@dlut.edu.cn), `Jingkai Xie <http://null>`_ (jingkai@nus.edu.sg), `Shuyue Yan <http://null>`_ (shuyue.yan@u.nus.edu) , `Zhouyan Li <http://null>`_ (zhouyan@nus.edu.sg)
:Organization: `National University of Singapore <https://nus.edu.sg/>`_
:Version: |release|
:Date: |today|
:Copyright:  The model code is licensed under the `GNU General Public License 3.0 <https://github.com/PREP-NexT/PREP-SHOT/blob/main/LICENSE>`_. This documentation is licensed under a `Creative Commons Attribution 4.0 International <http://creativecommons.org/licenses/by/4.0/>`_ license.

Overview
--------
**PREP-SHOT** (**P**\ athways for **R**\ enewable **E**\ nergy **P**\ lanning coupling **S**\ hort-term **H**\ ydropower **O**\ pera\ **T**\ ion) is a transparent, modular, and open-source energy expansion model, offering advanced solutions for multi-scale, intertemporal, and cost-effective expansion of energy systems and transmission lines. 

.. video:: https://github.com/PREP-NexT/PREP-SHOT/releases/download/v1.0/20250717_prep_shot.mp4
   :width: 100%
   :poster: ./_static/PREPSHOT_Update07.jpg
   :alt: PREP-SHOT introduction video

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

Source: :cite:t:`liu2023`.

Key Features
------------
* PREP-SHOT is an optimization model based on linear programming for energy systems with multiple zones.
* It aims to minimize costs while meeting the given demand time series.
* By default, it operates on hourly-spaced time steps, but this can be adjusted.
* The input data is in Excel format, while output data is generated in a NetCDF format using `Xarray <https://docs.xarray.dev/en/stable/>`_.
* It supports multiple types of solvers such as `HiGHS <https://github.com/jump-dev/HiGHS.jl>`_ , `GUROBI <https://www.gurobi.com/>`_, `COPT <https://www.copt.de/>`_, and `MOSEK <https://www.mosek.com/>`_ via `PyOptInterface <https://github.com/metab0t/PyOptInterface>`_.
* It allows the input of multiple scenarios for specific parameters.
* As a pure Python program, it benefits from the use of `pandas <https://pandas.pydata.org/>`_ and `Xarray <https://docs.xarray.dev/en/stable/>`_, simplifying complex data analysis and promoting extensibility.

Offline documentation
----------------------
To browse the documentation offline, you can `download a PDF copy <https://github.com/PREP-NexT/PREP-SHOT/raw/gh-pages/_static/PREP-SHOT.pdf>`_ for offline reading (Synchronize updates with online documentation).

.. toctree::
   :hidden:
   :maxdepth: 2

   Overview <self>
   Installation
   Model_input_output
   Tutorial
   Mathematical_notations
   Forum
   Contribution
   Changelog
   api/prepshot
   Citations
   References

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
