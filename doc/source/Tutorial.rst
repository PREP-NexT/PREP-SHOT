Tutorial
====================================

Run your first PREP-SHOT model
------------------------------------

Let us learn by example.

Throughout this tutorial, we'll walk you through running a toy example about electricity capacity expansion.

We'll assume you have PREP-SHOT installed already.

Background
++++++++++++++++++++

This is a simplified example based on data primarily obtained from the U.S. Energy Information Administration (`EIA <https://www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/regional/REG-NW>`_), U.S. Army Corps of Engineers (`USACE <https://www.nwd-wc.usace.army.mil/dd/common/dataquery/www/>`_) and U.S. National Renewable Energy Laboratory (`NREL <https://atb.nrel.gov/electricity/2022/data>`_). Our analysis focuses on a cascade hydropower system consisting of 15 hydropower stations, with the specific typology relationship described below. We assume the presence of three balancing authorities (BA1, BA2, and BA3) and establish jurisdictional connections between reservoirs and balancing authorities as follows. Apart from hydropower, we assume that no other existing technologies or transmission lines are in place. Our analysis includes four candidate technologies: Coal-fired plants, Wind power plants, Solar power plants, and Energy storage plants. The objective is to devise an electric mix pathway from 2020 to 2030 that enables the achievement of zero-carbon emissions. To solve this problem quickly, we select a 48-hour representative period.

.. figure:: ./_static/typology.jpg
   :width: 50 %
   :alt: typology


Prepare the Input Data
+++++++++++++++++++++++
👉 technology_portfolio.xlsx

Existing total installed capacity across all zones is stored in `technology_portfolio.xlsx` as follows and the unit is ``MW``.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vS2kUJOLfZ7Y93ausQUFvIpA7NUSOTOSaRB97CCVn70uLKFzhA029C-Uh273kML6Q/pubhtml?gid=637332031&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 distance.xlsx

Distance of different pair of zones is stored in `distance.xlsx` as follows and the unit is ``km``, which is used to calculate the transmission investment cost.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTTEELrCKyXq0qXy2CsHcl5lM-ZA0ujw9uO8WTq6zadFQq-kepSLwI0_sMZmXEtPA/pubhtml?gid=293039800&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 discount_factor.xlsx

discount factor for each year is stored in `discount_factor.xlsx` as follows and the unit is ``1``, which is used to calculate the present value of cost.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRF8O3KMZ88lVjO_uHdpHRH1VdsfvHSAr1du74VJDwMMXsWiVVZov6WOpv-Ty3zHA/pubhtml?gid=2003587890&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 transline.xlsx

Existing installed capacity of transmission lines across all zones is stored in `transline.xlsx` as follows and the unit is ``MW``.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSArhwW8dUb1fM0Fhc9r_Q5GLYvmKFfvZc9NOrNxjAVHvdA3uSzEw3VwKVnnIkQ7Q/pubhtml?gid=1961690293&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 transline_efficiency.xlsx

Efficiency of transmission lines across all zones is stored in `transline_efficiency.xlsx` as follows and the unit is ``1``, which is used to calculate the transmission loss.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQchaAZ1r5XxRPygj5rpFOtrW-sex4dqIBvyAdEIiqWa6ls7VFjoxdWtwpHDWvx9w/pubhtml?gid=1498515383&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>

👉 technology_fix_cost.xlsx

Fixed operation and maintaince cost of different technologies is stored in `technology_fix_cost.xlsx` as follows and the unit is ``$/MW``, which is used to calculate the system cost.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vShzG4zwROyn0JGx9O9nOgbBxiKUDeORFyiYhzSSluWGJlyLl7XHBnoxEBhGI_ymg/pubhtml?gid=551587702&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 technology_variable_cost.xlsx

Variable operation and maintaince cost of different technologies is stored in `technology_variable_cost.xlsx` as follows and the unit is ``$/MWh``, which is used to calculate the system cost.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vT7IRzyCzhmJvylBvNX2ROrUKHAypPUYsJKCZQuJd727utBXMdT7LlWSoWZUJvx_A/pubhtml?gid=1567056778&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 technology_investment_cost.xlsx

Investment cost of different technologies is stored in `technology_investment_cost.xlsx` as follows and the unit is ``$/MW/km``, which is used to calculate the system cost.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSQTJfo_TAlwyCidnrDBaYMgayChEp00eXBQ4C8WFz1VPyzLQPVnEv-ZQBoyhYmdw/pubhtml?gid=681712845&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 carbon_content.xlsx 

Carbon content of different technologies is stored in `carbon_content.xlsx` as follows and the unit is ``tCO2/MWh``, which is used to calculate the system cost.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTFK_vG7-cDcu-flf3_nyN8Mofq2_5Fs1l7Z_1RZjCs4iRgSMwqfyaFTOb4RV-f8g/pubhtml?gid=1731802572&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>
   

👉 fuel_price.xlsx

Fuel price of different technologies is stored in `fuel_price.xlsx` as follows and the unit is ``$/MWh``, which is used to calculate the system cost.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTpTYT29azVDuHV015ChJXvrbBuWKoh9hNXZd9bTmA__Vt2_MdqW6wurKKO6r0Upw/pubhtml?gid=434666485&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 efficiency_in.xlsx

Discharging efficiency of storage technologies is stored in `efficiency_in.xlsx` as follows and the unit is ``1``, which is used to calculate the discharging and charging loss of energy storage.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQ_P7Lr6f2PrV-thn92JQc6DLWZNjMweW6oQP63qP5Bnw7_T3-ORiIb_6SW1JNL5w/pubhtml?gid=591443577&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 efficiency_out.xlsx

Charging efficiency of storage technologies is stored in `efficiency_out.xlsx` as follows and the unit is ``1``, which is used to calculate the discharging and charging loss of energy storage.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQlTy32iH0282jLMMiUIDqNDOYuH6ggwl0JuLYfuH_fCT-ziTQrj7XXlLNM0KL6uQ/pubhtml?gid=1682709855&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 energy_power_ratio.xlsx

Energy to power ratio of storage technologies is stored in `energy_power_ratio.xlsx` as follows and the unit is ``h``, which is used to measure duration of energy storage.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRXJlbJzHBUtCFARgDOwaxONEZOrRubjqgJaN1SlMnAm6lEDiuObgs16i_oXGxJmg/pubhtml?gid=1539898206&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 lifetime.xlsx

Lifetime of different technologies is stored in `lifetime.xlsx` as follows and the unit is ``year``, which is used to calculate the retirement of power plant.

.. raw:: html

    <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRsSw180wGwZZ4TAlIGGdKSAxaVvfGWn0QYsZvbtsyoigzxq2qJy8fwgZiT5qqluw/pubhtml?gid=1801866364&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 capacity_factor.xlsx

Capacity factor of different non-dispatchable technologies is stored in `capacity_factor.xlsx` as follows and the unit is ``1``, which is used to calculate the power output.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQSQe58l9nI-lX_MDMpEoDpay2wiizJ8wE4Dnnbr-ZQQslpEGdkTjZzOXgfjCz-kQ/pubhtml?gid=1863708464&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>
   
👉 demand.xlsx

Demand of different balancing authorities is stored in `demand.xlsx` as follows and the unit is ``MW``, which is used to calculate the power balance.
    
.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSulJsf8eSjFFA5CvBKACCi9U9zHn3VQgZwNQc-KZad0nJBh3t4zh_yZ2THU2Qpvw/pubhtml?gid=1251865419&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 ramp_up.xlsx

Ramp up rate of different technologies is stored in `ramp_up.xlsx` as follows and the unit is ``1/MW``, which is used to limit the fluctuation of power output.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRi4_pwVNLN5jtrB214U-qGsF-sL84L0MAW3Nc1Pe7ppjDrhNBTAb3PcqTAVSlCCA/pubhtml?gid=821500405&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 ramp_down.xlsx

Ramp down rate of different technologies is stored in `ramp_down.xlsx` as follows and the unit is ``1/MW``, which is used to limit the fluctuation of power output.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQehJwj1E29-rc9j-BD-urco4I_a9Wa7PeVbkVJR3WNdSWxk-Ex8-uC0dOR4zMEPQ/pubhtml?gid=440050753&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 carbon.xlsx

Carbon emission limit of different balancing authorities is stored in `carbon.xlsx` as follows and the unit is ``tCO2``, which is used to modelling the policy of the carbon emission reduction.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRIcZuO_wLzfcE1K_d9am-kWZnTw7eJfhU1oTgRGP3-JrpaFifW71bh1dCmNINv0g/pubhtml?gid=1661835844&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 transline_investment_cost.xlsx

Investment cost of transmission lines is stored in `transline_investment_cost.xlsx` as follows and the unit is ``$/MW/km``, which is used to calculate the system cost.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSeQz6TJah3mqCdUWdVhlJSQgmp19diqspWAszYlUY4ScoTHpBVLguBYTRakhU0lQ/pubhtml?gid=1998510036&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 technology_upper_bound.xlsx

Upper bound of installed capacity of different technologies is stored in `technology_upper_bound.xlsx` as follows and the unit is ``MW``, which is used to modelling the potential of technologies constrainted by land, fuel, and water.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSQx2SJiUGKsS5R4gyoycv9cGRo7Y9r-iwO-p6EYFqs5NABdrGx4-wiGsXE3sQ7XQ/pubhtml?gid=445947763&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 new_technology_upper_bound.xlsx

Upper bound of new built installed capacity of different technologies for each investment year is stored in `new_technology_upper_bound.xlsx` as follows and the unit is ``MW``, which is used to modelling the limits of technologies constrainted by finance and policy.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSMKiKTwzsht2cuNVX2CvRd3fVXv3zvrB-KyxZ3ECBj9CAkhX4A2Y_tcJCExjr80g/pubhtml?gid=384486929&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 new_technology_lower_bound.xlsx

Lower bound of new built installed capacity of different technologies for each investment year is stored in `new_technology_lower_bound.xlsx` as follows and the unit is ``MW``, which is used to modelling the limits of technologies constrainted by policy.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRhpZ1hfiFfRNtHToZqOpWagL0DtcYDgIaRMQDbNnr2F8FvHUK0q_ubRHgfOB5YRw/pubhtml?gid=498393379&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 init_storage_level.xlsx

Initial storage level of different storage technologies is stored in `init_storage_level.xlsx` as follows and the unit is ``1/MWh``, which is used to modelling the initial storage level of energy storage.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTqaC1jhD_x3iakcaOYCuVNW6Nm0HG_jWtdf1O-GYo7vFBNgc4-rMBUeHWwrnSKbg/pubhtml?gid=1350220091&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 transline_fix_cost.xlsx

Fixed operation and maintaince cost of transmission lines is stored in `transline_fix_cost.xlsx` as follows and the unit is ``$/MW``, which is used to calculate the system cost.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vShzG4zwROyn0JGx9O9nOgbBxiKUDeORFyiYhzSSluWGJlyLl7XHBnoxEBhGI_ymg/pubhtml?gid=551587702&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 transline_variable_cost.xlsx

Variable operation and maintaince cost of transmission lines is stored in `transline_variable_cost.xlsx` as follows and the unit is ``$/MWh``, which is used to calculate the system cost.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTtiuRyVGqmtybQQ_pb-ZXupDwUJuYlL7I0nvVLYlpynXq5Qr8xV74kNaQodYJiEA/pubhtml?gid=1541781510&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 transmission_line_lifetime.xlsx

Lifetime of transmission lines is stored in `transmission_line_lifetime.xlsx` as follows and the unit is ``year``, which is used to calculate the retirement of transmission lines.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQNxDsc0-y0_BySbc3FkNO6Jpc8tpcSMb96q9vqd2Xl77mja8RgFjQni_iWZ5ueUg/pubhtml?gid=1625392481&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 zv.xlsx

The piecewise breakpoint of forebay elevation and volume for different reservoirs is stored in `zv.xlsx` as follows and the unit is ``m`` and ``10^8 m3``. These values are utilized in the calculation of the forebay elevation based on the volume of the reservoirs.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSeAXsm3DtgiBF4W9QpleJWbxIUqAp9_fC_NBgOcOZ90SkuP-vhfB4loZTojLWVFA/pubhtml?gid=1855010818&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 zq.xlsx

The piecewise breakpoint of tailrace elevation and total discharge for different reservoirs is stored in `zq.xlsx` as follows and the unit is ``m`` and ``m^3/s``. These values are utilized in the calculation of the tailrace elevation based on the total discharge of the reservoirs.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTX5LSrVReyc-FqapxrjhUk8kD5JmX3aPoO1ky9BE8voRY6X3hdrsNzauxxeopR2Q/pubhtml?gid=86211327&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 type.xlsx

The catelogy of different technologies is stored in `type.xlsx` as follows. These values are utilized to specify modelling ways of different technologies.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vSekya_uCo8p54lrTAjmdqKJKtWFN3uz0_aQAcFGrrRHpC3NhZdxljaXpr71phoyQ/pubhtml?gid=749312388&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>

👉 age.xlsx

The age of existing different technologies is stored in `age.xlsx` as follows and the unit is ``MW``. These values are utilized to model the retirement of existing power plants.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vS1JngyPcauiYkoNrn9cOt2KQIloJ967YsCzJ7MqePQ7fblRzF0p3JsDsSk10Fkjw/pubhtml?gid=1774762525&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 storage_upbound.xlsx

The upper bound of volume of hydropower reservoirs is stored in `storage_upbound.xlsx` as follows and the unit is ``10^8 m3``. These values are utilized to model the operation rule of hydropower reservoirs.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTAcZy6hv9uPSo_RPhcVTwce2kGlwdambx1mkmTypXmQBDHlaZiRMqtakM8UYKT8w/pubhtml?gid=1986677103&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 storage_lowbound.xlsx

The lower bound of volume of hydropower reservoirs is stored in `storage_lowbound.xlsx` as follows and the unit is ``10^8 m3``. These values are utilized to model the operation rule of hydropower reservoirs.


.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vT_XjZ7CAQWdnMmJm816XvcsZERZUnsFsi1rfIEQwaCDHKytRNgcuIcmZeaF4eKDg/pubhtml?gid=137205345&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>

👉 storage_init.xlsx

The initial volume of hydropower reservoirs is stored in `storage_init.xlsx` as follows and the unit is ``10^8 m3``.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRZ-tmaK-54TGaHyJt-m3LJu77OcgzVyUK3xnZO7WlBlqcWhOotBmBGMI2jiJEp1g/pubhtml?gid=57931371&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>

👉 storage_end.xlsx

The final volume of hydropower reservoirs is stored in `storage_end.xlsx` as follows and the unit is ``10^8 m3``.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTCfsEtm4w58MxCBOW3SiB2Vpg3KU2epUl-JFLyX255Hw2Hh7pcWD0rlbj4csz2DQ/pubhtml?gid=79770751&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>

👉 hydropower.xlsx

The predifined hydropower output of all reservoirs is stored in `hydropower.xlsx` as follows and the unit is ``MW``. These values are utilized to model the simplified hydropower operation.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRPi61ApJNAI1L_7_WwnSOXKFYwNqHC6DoWMXNjZPltwZB2I1RPnOWuR-gH3yLPwg/pubhtml?gid=2031818477&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>

👉 inflow.xlsx

The inflow of all reservoirs is stored in `inflow.xlsx` as follows and the unit is ``m^3/s``. These values are utilized to model the simplified hydropower operation.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRFIz6bsPQjIrz3rCB_aIfYZSCa8_JWpeg9WpRCaC_2GwHGJki8FkLX4Joz4cMMMA/pubhtml?gid=769608322&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>

👉 connect.xlsx

The water delay time of connection between reservoirs is stored in `connect.xlsx` as follows. These values are utilized to model the cascade hydrolic connection.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6TvqsvSXg6wWigUojaipNKbgHdGQxUB5NXvLwnl8pcKh1_RgGJiv4i7Ivx0sfYg/pubhtml?gid=1371452224&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


👉 static.xlsx

The static data of all reservoirs is stored in `static.xlsx` as follows.

.. raw:: html

   <iframe src="https://docs.google.com/spreadsheets/d/e/2PACX-1vQR4irCy_B43FUEwkCBHLklt8Za4IyG7ye8srWeM2Z7m8UrbRe3hhv6QGwHToGD1w/pubhtml?gid=1743293144&amp;single=true&amp;widget=true&amp;headers=false" width="100%" height="200px"></iframe>


