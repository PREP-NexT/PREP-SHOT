#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains utility functions for the model.
"""

from itertools import product

from scipy import interpolate

def check_positive(*values):
    """Ensure all values are greater than 0.
    
    Parameters
    ----------
    values : int or float
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
    dep_period, interest_rate, year_built, discount_rate, year_min, year_max
):
    """Compute the investment cost factor.

    Parameters
    ----------
    dep_period : int
        Depreciation period.
    interest_rate : float
        Interest rate.
    year_built : int
        Year of construction.
    discount_rate : float
        Discount rate.
    year_min : int
        Minimum year.
    year_max : int
        Maximum year.

    Returns
    -------
    float
        Investment cost factor.

    Raises
    ------
    ValueError
        If year_max <= year_min, year_max < year_built, or 
        year_built < year_min.
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

def calc_cost_factor(discount_rate, modeled_year, year_min, next_modeled_year):
    """Compute the cost factor.

    Parameters
    ----------
    discount_rate : float
        Discount rate.
    modeled_year : int
        Modeled year.
    year_min : int
        Minimum year.
    next_modeled_year : int
        Next year.

    Returns
    -------
    float
        Cost factor.

    Raises
    ------
    ValueError
        if next_modeled_year < modeled_year.
    """
    check_positive(discount_rate, modeled_year, year_min, next_modeled_year)
    if next_modeled_year < modeled_year:
        raise ValueError(
            "Next modeled year must be greater than or" 
            + "equal to the current modeled year."
        )

    years_since_min = modeled_year - year_min
    years_to_next = next_modeled_year - modeled_year
    return (1 - (1 + discount_rate) ** (-years_to_next))                      \
        / (discount_rate * (1 + discount_rate) ** (years_since_min - 1))

def interpolate_z_by_q_or_s(name, qs, zqv):
    """Interpolate forebay water level (Z) by reservoir storage (S) or tailrace
    water level (Z) by the reservoir outflow (Q).

    Parameters
    ----------
    name : str
        Name of the hydropower station.
    qs : numpy.ndarray
        Array of Q or S values.
    zqv : pandas.DataFrame
        DataFrame of ZQ or ZV values.

    Returns
    -------
    scipy.interpolate.interp1d
        Array of interpolated values.
    """
    zqv_temp = zqv[(zqv.name == int(name)) | (zqv.name == str(name))]
    x = zqv_temp.Q if 'Q' in zqv_temp.columns else zqv_temp.V
    f_zqv = interpolate.interp1d(x, zqv_temp.Z, fill_value='extrapolate')
    return f_zqv(qs)


def cartesian_product(*args):
    """Generate Cartesian product of input iterables.
    
    Parameters
    ----------
    args : iterable
        Input iterables.
        
    Returns
    -------
    list
        List of tuples representing the Cartesian product. 
    """
    # [1, 2], [7, 8] -> [(1, 7), (1, 8), (2, 7), (2, 8)]
    return list(product(*args))
