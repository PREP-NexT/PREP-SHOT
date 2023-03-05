.. module:: PREP-SHOT

Welcome to PREP-SHOT's documentation!
======================================

:Author: `Liu Zhanwei <https://www.researchgate.net/profile/Zhanwei-Liu-4>`_ (Mr), <liuzhanwei@u.nus.edu> and `He Xiaogang <http://hydro.iis.u-tokyo.ac.jp/~hexg/>`_ (Dr), <hexg@nus.edu.sg>
:Organization: `National University of Singapore <https://nus.edu.sg/>`_
:Version: |release|
:Date: |today|
:Copyright:  The model code is licensed under the `GNU General Public License 3.0 <http://www.gnu.org/licenses/gpl-3.0>`_. This documentation is licensed under a `Creative Commons Attribution 4.0 International <http://creativecommons.org/licenses/by/4.0/>`_ license.

**P**\ athways for **R**\ enewable **E**\ nergy **P**\ lanning coupling **S**\ hort-term **H**\ ydropower **O**\ pera\ **T**\ ion (`PREP-SHOT <https://github.com/PREP-NexT/PREP-SHOT>`_) is a transparent, modular, and open-source energy expansion model. It can be used for the multi-scale, intertemporal cost-effective expansion of energy systems and transmission lines. Compared to other existing energy expansion models, which either treat hydropower as fixed processes (`urbs <https://urbs.readthedocs.io/en/latest/>`_) or overlook the dynamic nature of water heads (`GenX <https://genxproject.github.io/GenX/dev/>`_, `PLEXOS <https://www.energyexemplar.com/plexos>`_) or simply aggregate multiple hydropower stations into a single unit, a unique feature of PREP-SHOT is that it explicitly considers the plant-level water head dynamics (i.e., time-varying water head and storage) and the system-level network topology of all hydropower stations within a regional grid. This allows us to better capture the multi-scale dynamic feedbacks between hydropower operation and energy system expansion as well as realistically simulate the magnitude and spatial-temporal variability of hydropower output, especially in regions with a large number of cascade hydropower stations.

The PREP-SHOT mainly aims to answer the following question:

* How to plan an energy portfolio and new transmission capacity for the future (i.e. new-built, retirement) under deep uncertainty?
* Quantifying the impacts of variable hydropower on generation and capacity of future energy portfolio?


.. figure:: ./_static/overview.png
   :width: 100 %
   :alt: overview of PREP-SHOT

Contents
-----------
.. toctree::
   :maxdepth: 1

   Installation

.. toctree::
   :maxdepth: 1

   Introduction

.. toctree::
   :maxdepth: 1

   Users_guide

.. toctree::
   :maxdepth: 1

   Model_structure

.. toctree::
   :maxdepth: 1
   
   Changelog
