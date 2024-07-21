#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains utility functions for the model.
"""
from typing import Union, Tuple, List
from itertools import product

from scipy import interpolate
import pandas as pd
import numpy as np

def check_positive(*values : Union[int, float]) -> None:
    """Ensure all values are greater than 0.
    
    Parameters
    ----------
    values : Union[int, float]
        Values to be checked.

    Raises
    ------
    ValueError
        If any value is less than or equal to 0.
    """
    for value in values:
        if value <= 0:
            raise ValueError("All arguments must be greater than 0.")

def calc_inv_cost_factor(
    dep_period : int,
    interest_rate : float,
    year_built : int,
    discount_rate : int,
    year_min : int,
    year_max : int
) -> float:
    """Compute the investment cost factor. When the depreciation period is
    greater than the planning horizon, the investment cost factor is calculated
    by only considering the period within the planning horizon.

    Parameters
    ----------
    dep_period : int
        Depreciation period, in years, i.e., lifetime of the infrastructure.
    interest_rate : float
        Interest rate.
    year_built : int
        Year of investment.
    discount_rate : float
        Discount rate.
    year_min : int
        Minimum year, i.e., the first year of the planning horizon.
    year_max : int
        Maximum year, i.e., the last year of the planning horizon.

    Returns
    -------
    float
        Investment cost factor.

    Raises
    ------
    ValueError
        If year_max <= year_min, year_max < year_built, or 
        year_built < year_min.

    Examples
    --------
    Given a depreciation period of 20 years, interest rate of 0.05, year of
    investment in 2025, discount rate of 0.05, planning horizon from 2020 to
    2050, compute the investment cost factor:
    >>> calc_inv_cost_factor(20, 0.05, 2025, 0.05, 2020, 2050)
    0.783526
    
    If the depreciation perios is 100 years, compute the investment cost factor
    for the same scenario:
    
    >>> calc_inv_cost_factor(100, 0.05, 2025, 0.05, 2020, 2050)
    0.567482

    """
    check_positive(dep_period, interest_rate, year_built, year_min, year_max)
    if (year_max <= year_min) or (year_max < year_built)                      \
        or (year_built < year_min):
        raise ValueError("Invalid year values.")

    years_since_min = year_built - year_min
    years_to_max = year_max - year_built + 1
    return (interest_rate / (1 - (1 + interest_rate) ** (-dep_period))
             * (1 - (1 + discount_rate) ** (-min(dep_period, years_to_max)))
             / (discount_rate * (1 + discount_rate) ** years_since_min))

def calc_cost_factor(
    discount_rate : float,
    modeled_year : int,
    year_min : int,
    next_modeled_year : int
) -> float:
    """Compute the variable and fixed cost factor while considering the 
    multi-stage planning horizon.

    Parameters
    ----------
    discount_rate : float
        The discount rate to apply.
    modeled_year : int
        The year in which the cost occurs.
    year_min : int
        The first year of the planning horizon. All costs are discounted to 
        this year.
    next_modeled_year : int
        The subsequent modeled year. The cost incurred bewteen modeled_year
        and modeled_year and next_modeled_year is calculated.

    Returns
    -------
    float
        The computed cost factor.

    Raises
    ------
    ValueError
        if next_modeled_year < modeled_year.
        
    Examples
    --------
    Given annual cost incurred in 2025, next_modeled_year = 2030, and starting
    year = 2020, compute present value in 2020 of the cost incurred in 
    2025-2029:
    >>> calc_cost_factor(0.05, 2025, 2020, 2030)
    3.561871

    """
    check_positive(discount_rate, modeled_year, year_min, next_modeled_year)
    if next_modeled_year <= modeled_year:
        raise ValueError(
            "Next modeled year must be greater than or" 
            + "equal to the current modeled year."
        )

    years_since_min = modeled_year - year_min
    years_to_next = next_modeled_year - modeled_year
    return (1 - (1 + discount_rate) ** (-years_to_next))                      \
        / (discount_rate * (1 + discount_rate) ** (years_since_min - 1))

def interpolate_z_by_q_or_s(
    name : str,
    qs : Union[np.ndarray, float],
    zqv : pd.DataFrame
) -> float:
    """Interpolate forebay water level (Z) by reservoir storage (S) or tailrace
    water level (Z) by the reservoir outflow (Q).

    Parameters
    ----------
    name : str 
        Code of the hydropower station.
    qs : Union[np.ndarray, float]
        Reservoir storage or outflow values. 
    zqv : pandas.DataFrame
        DataFrame of ZQ or ZV values.

    Returns
    -------
    Union[np.ndarray, float]
        Interpolated values.
    """
    zqv_station = zqv[(zqv.name == int(name)) | (zqv.name == str(name))]
    x = zqv_station.Q if 'Q' in zqv_station.columns else zqv_station.V
    f_zqv = interpolate.interp1d(x, zqv_station.Z, fill_value='extrapolate')
    return f_zqv(qs)

def cartesian_product(
    *args : List[Union[int, str]]
) -> List[Tuple[Union[int, str]]]:
    """Generate Cartesian product of input iterables.

    Parameters
    ----------
    args : List[Union[int, str]]
        Iterables to be combined.

    Returns
    -------
    List[Tuple[Union[int, str]]]
        List of tuples representing the Cartesian product.

    Examples
    --------
    Combine two lists [1, 2] and [7, 8]:

    >>> cartesian_product([1, 2], [7, 8])
    [(1, 7), (1, 8), (2, 7), (2, 8)]

    """
    return list(product(*args))
