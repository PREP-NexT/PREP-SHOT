.. module:: PREP-SHOT

Welcome to the PREP-SHOT Documentation
=======================================

:Authors: `Zhanwei Liu <https://scholar.google.com/citations?user=Zub5y2IAAAAJ>`_ (liuzhanwei@u.nus.edu), `Xiaogang He <http://hydro.iis.u-tokyo.ac.jp/~hexg/>`_ (hexg@nus.edu.sg)
:Contributors: `Bo Xu <http://faculty.dlut.edu.cn/xubo12/zh_CN/index.htm>`_ (xubo_water@dlut.edu.cn), `Jingkai Xie <http://null>`_ (jingkai@nus.edu.sg), `Shuyue Yan <http://null>`_ (shuyue.yan@u.nus.edu) , `Zhouyan Li <http://null>`_ (zhouyan@nus.edu.sg), `Quan Yuan <http://null>`_ (quanyuan@nus.edu.sg), `Kewei Zhang <http://null>`_ (kewei_zhang@u.nus.edu), `Yaozhong Cui <http://null>`_ (cuiyaozhong@u.nus.edu)
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
* The input data is in long-format ("tidy") CSV, while output data is generated in a NetCDF format using `Xarray <https://docs.xarray.dev/en/stable/>`_.
* It supports multiple types of solvers such as `HiGHS <https://github.com/jump-dev/HiGHS.jl>`_ , `GUROBI <https://www.gurobi.com/>`_, `COPT <https://www.copt.de/>`_, and `MOSEK <https://www.mosek.com/>`_ via `PyOptInterface <https://github.com/metab0t/PyOptInterface>`_.
* It allows the input of multiple scenarios for specific parameters.
* As a pure Python program, it benefits from the use of `pandas <https://pandas.pydata.org/>`_ and `Xarray <https://docs.xarray.dev/en/stable/>`_, simplifying complex data analysis and promoting extensibility.

New to power-system modeling?
-----------------------------
Four free primers we recommend reading alongside PREP-SHOT:

* `Power Sector Modeling 101 <https://www.energy.gov/sites/prod/files/2016/02/f30/EPSA_Power_Sector_Modeling_FINAL_021816_0.pdf>`_ (US DOE EPSA, 2016) -- the model families PREP-SHOT belongs to and where their assumptions break.
* `Beginner's Guide to Understanding Power System Model Results for Long-Term Resource Plans <https://docs.nrel.gov/docs/fy24osti/87105.pdf>`_ (NREL, 2023) -- how to read a capacity-expansion result.
* `Advanced Guide to Understanding Power System Model Results for Long-Term Resource Plans <https://docs.nrel.gov/docs/fy24osti/88337.pdf>`_ (NREL, 2024) -- deeper sequel: reliability metrics, reserve margin, transmission congestion.
* `Electric Grid and Markets 101 <https://docs.nrel.gov/docs/fy25osti/91864.pdf>`_ (NREL, 2024) -- how the bulk power system actually works: generation, transmission, ISOs/RTOs, day-ahead vs real-time markets, ancillary services. Real-world grounding for the modeled abstractions.

Validation benchmarks
---------------------
PREP-SHOT ships three independent benchmarks that compare the
model's output against externally-published reference numbers.
Each benchmark stands alone, with its own input data, notebook
walking through the validation, and pytest regression:

* `PJM 5-bus <PJM5.html>`_ -- Hogan / MATPOWER ``case5``: 5
  buses, 5 generators, single-hour DC OPF.  PREP-SHOT reproduces
  MATPOWER's ``runopf`` total cost (``$17,479.89``) to the dollar
  and the dispatch to 0.01 MW.
* `IEEE RTS-79 <RTS79.html>`_ -- 24 buses, 32 generators, full
  hourly load profile (8 736 hours).  Annual energy by carrier
  matches the merit-order benchmark; peak-hour dispatch matches
  the textbook pattern (hydro 300, nuclear 800, coal 1 274,
  oil 476 MW).
* `IEEE RTS-96 <RTS96.html>`_ -- 3-area extension of RTS-79
  (73 buses, 96 gens, 5 inter-area ties).  Validates the multi-
  area DC OPF: each area's dispatch is exactly 3 x RTS-79.
* `Cambodia <Cambodia.html>`_ -- must-take port of the Cambodia
  case from PowNet (Chowdhury et al. 2020): 18 thermals + 6
  hydros + 3 imports, 8 760 hours.  PREP-SHOT thermal+import
  total matches PowNet's published 3.90 TWh within 0.3 %.
* `Laos <Laos.html>`_ -- companion hydro-export case (5
  thermals + 30 hydros + 4 imports).  Validates the structural
  pattern of a hydro-dominated system (hydro share ~80 %).
* `Germany <Germany.html>`_ -- PyPSA's single-day Germany
  example (Brown et al. 2018; SciGRID open-data network with
  1 423 generators across 585 buses).  PREP-SHOT lands on EUR
  4.72 M for the 24-hour cost-minimising dispatch, inside
  PyPSA's published EUR 4-5 M range.

Offline documentation
----------------------
To browse the documentation offline, download a `zipped HTML copy <https://prep-shot.readthedocs.io/_/downloads/en/stable/htmlzip/>`_ from Read the Docs (also accessible via the version-switcher at the bottom-left of every page).

.. toctree::
   :hidden:
   :caption: Getting Started
   :maxdepth: 2

   Overview <self>
   Installation
   Quickstart
   Thailand
   SoutheastAsia
   ThailandPCM

.. toctree::
   :hidden:
   :caption: Validation Benchmarks
   :maxdepth: 2

   PJM5
   RTS79
   RTS96
   Cambodia
   Laos
   Germany

.. toctree::
   :hidden:
   :caption: User Guide
   :maxdepth: 2

   Model_input_output
   Mathematical_notations
   Glossary
   how_to/index

.. toctree::
   :hidden:
   :caption: Reference
   :maxdepth: 2

   api/prepshot
   Stability
   Changelog

.. toctree::
   :hidden:
   :caption: Community
   :maxdepth: 2

   Forum
   Contribution
   Citations
   References

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
