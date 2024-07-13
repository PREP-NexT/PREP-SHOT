#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This module contains utility functions related to the head iteration.
"""

import datetime
import logging

import numpy as np
import pandas as pd

import pyoptinterface as poi

from prepshot.utils import interpolate_z_by_q_or_s

def initialize_waterhead(stations, year, month, hour, params):
    """Initialize water head.

    Parameters
    ----------
    stations : list
        List of stations.
    year : list
        List of years.
    month : list
        List of months.
    hour : list
        List of hours.
    params : dict
        Dictionary of parameters for the model.

    Returns
    -------
    tuple
        A tuple of two pandas.DataFrame objects, the first one is 
        the old water head, the second one is the new water head.
    """
    old_waterhead = pd.DataFrame(
        index=stations,
        columns=pd.MultiIndex.from_product(
            [year, month, hour], names=['year', 'month', 'hour']
        )
    )
    new_waterhead = old_waterhead.copy(deep=True)

    for s in stations:
        old_waterhead.loc[s, :] = [
            params['reservoir_characteristics']['head', s]
        ] * (len(hour) * len(month) * len(year))
    return old_waterhead, new_waterhead

def compute_error(old_waterhead, new_waterhead):
    """Calculate the error of the water head.

    Parameters
    ----------
    old_waterhead : pandas.DataFrame
        The water head before the solution.
    new_waterhead : pandas.DataFrame
        The water head after the solution.

    Returns
    -------
    float
        The error of the water head.
    """
    new_waterhead[new_waterhead <= 0] = 1
    error = (
        abs(new_waterhead - old_waterhead)
        / new_waterhead
    ).mean(axis='columns').mean()
    return error

def process_model_solution(
    model, stations, year, month, hour, params, old_waterhead, new_waterhead
):
    """Process the solution of the model, updating the water head data.

    Parameters
    ----------
    model : pyoptinterface._src.solver.Model
        Model to be solved.
    stations : list
        List of hydropower stations.
    year : list
        List of years.
    month : list
        List of months.
    hour : list
        List of hours.
    params : dict
        Dictionary of parameters for the model.
    old_waterhead : pandas.DataFrame
        The water head before the solution.
    new_waterhead : pandas.DataFrame
        The water head after the solution.

    Returns
    -------
    bool
        True if the model is solved, False otherwise.
    """
    idx = pd.IndexSlice
    for s, h, m, y in model.station_hour_month_year_tuples:
        efficiency = params['reservoir_characteristics']['coeff', s]
        model.set_normalized_coefficient(
            model.output_calc_cons[s, h, m, y],
            model.genflow[s, h, m, y],
            - efficiency * 1e-3 * old_waterhead.loc[s, idx[y, m, h]]
        )
    # Solve the model and check the solution status.
    model.set_model_attribute(poi.ModelAttribute.Silent, False)
    model.optimize() # add log into log file
    status = model.get_model_attribute(poi.ModelAttribute.TerminationStatus)
    if status != poi.TerminationStatusCode.OPTIMAL:
        return False
    if params['iteration_number'] <= 1:
        # If fixed head is True, do not update water head.
        new_waterhead = old_waterhead
        return True
    # Iterate over each station to update water head data.
    for stcd in stations:
        outflow = np.array([[
            [model.get_value(model.outflow[int(stcd), h, m, y]) for h in hour]
            for m in month] for y in year]
        )
        storage = np.array([[
            [model.get_value(model.storage_reservoir[int(stcd), h, m, y])
            for h in model.hour_p] for m in month] for y in year]
        )

        tail = interpolate_z_by_q_or_s(
            str(stcd), outflow,
            params['reservoir_tailrace_level_discharge_function']
        )
        storage = interpolate_z_by_q_or_s(
            str(stcd), storage, params['reservoir_forebay_level_volume_function']
        )

        # Calculate the new water head.
        fore = (storage[:, :, :hour[-1]] + storage[:, :, 1:]) / 2
        h = np.maximum(fore - tail, 0)
        new_waterhead.loc[int(stcd), :] = h.ravel()
    return True

def run_model_iteration(
    model, params, error_threshold=0.001, max_iterations=5
):
    """Run the model iteratively.

    Parameters
    ----------
    model : pyoptinterface._src.solver.Model
        Model to be solved.
    params : dict
        Dictionary of parameters for the model.
    error_threshold : float, optional
        The error threshold, by default 0.001
    max_iterations : int, optional
        The maximum number of iterations, by default 5

    Returns
    -------
    bool
        True if the model is solved, False otherwise.
    """
    logging.info(
        'Starting iteration recorded at %s.', 
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # Initialize water head.
    stations, years, months, hours =                                          \
        params['stcd'], params['year'], params['month'], params['hour']
    old_waterhead, new_waterhead = initialize_waterhead(
        stations, years, months, hours, params
    )

    # Variables for iteration.
    error = 1
    errors = []
    # Perform water head iteration.
    for iteration in range(1, max_iterations+1):
        alpha = 1 / iteration
        success = process_model_solution(
            model, stations, years, months, hours, params,
            old_waterhead, new_waterhead
        )
        if not success:
            return False

        # Calculate error.
        if  max_iterations <= 1:
            logging.warning(
                "Maximum iteration is set to 1 and " 
                + "the model will be solved with fixed head."
            )
            error = 0
        else:
            error = compute_error(old_waterhead, new_waterhead)
        errors.append(error)
        logging.info('Water head error: %.2f%%', error)
        if error < error_threshold:
            return True

        # Update old water head for next iteration.
        old_waterhead += alpha * (new_waterhead - old_waterhead)

    logging.warning(
        "Ending iteration recorded at %s."
        + "Failed to converge. Maximum iteration exceeded.",
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return True
