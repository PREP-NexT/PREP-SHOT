from os import path

from .utils import (fixcost_factor, invcost_factor, read_break_point,
                    read_four_dims,read_five_dims, read_hydro_static, read_lag_time,
                    read_one_dims, read_three_dims,read_four_dims_three_index_one_col,
                    read_three_dims_one_idx_two_col, read_two_dims,
                    varcost_factor)


def load_data(filepath, filename, para=None):
    """
    Args:
        filepath (_type_): _description_
        para (_type_): _description_

    Returns:
        _type_: _description_
    """
    if para == None:
        para = dict()

    para["technology_portfolio"] = read_two_dims(
        path.join(filepath, filename["technology_portfolio"]))
    para["distance"] = read_two_dims(path.join(filepath, filename["distance"]))
    para["transline"] = read_two_dims(path.join(filepath, filename["transline"]))
    para["transline_efficiency"] = read_two_dims(
        path.join(filepath, filename["transline_efficiency"]))
    para["discount_factor"] = read_one_dims(
        path.join(filepath, filename["discount_factor"]))
    para["technology_fix_cost"] = read_two_dims(
        path.join(filepath, filename["technology_fix_cost"]))
    para["technology_variable_cost"] = read_two_dims(
        path.join(filepath, filename["technology_variable_cost"]))
    para["technology_investment_cost"] = read_two_dims(
        path.join(filepath, filename["technology_investment_cost"]))
    para["carbon_content"] = read_two_dims(
        path.join(filepath, filename["carbon_content"]))
    para["fuel_price"] = read_two_dims(path.join(filepath, filename["fuel_price"]))
    para["efficiency_in"] = read_two_dims(
        path.join(filepath, filename["efficiency_in"]))
    para["efficiency_out"] = read_two_dims(
        path.join(filepath, filename["efficiency_out"]))
    para["energy_power_ratio"] = read_one_dims(
        path.join(filepath, filename["energy_power_ratio"]))
    para["lifetime"] = read_two_dims(path.join(filepath, filename["lifetime"]))
    para["capacity_factor"] = read_five_dims(
        path.join(filepath, filename["capacity_factor"]))
    para["demand"] = read_four_dims_three_index_one_col(path.join(filepath, filename["demand"]))
    para["ramp_up"] = read_one_dims(path.join(filepath, filename["ramp_up"]))
    para["ramp_down"] = read_one_dims(path.join(filepath, filename["ramp_down"]))
    para["carbon"] = read_one_dims(path.join(filepath, filename["carbon"]))
    para["transline_investment_cost"] = read_two_dims(
        path.join(filepath, filename["transline_investment_cost"]))
    para["technology_upper_bound"] = read_two_dims(
        path.join(filepath, filename["technology_upper_bound"]))
    para["new_technology_upper_bound"] = read_two_dims(
        path.join(filepath, filename["new_technology_upper_bound"]))
    para["new_technology_lower_bound"] = read_two_dims(
        path.join(filepath, filename["new_technology_lower_bound"]))
    para["init_storage_level"] = read_two_dims(
        path.join(filepath, filename["init_storage_level"]))
    para["transline_fix_cost"] = read_two_dims(
        path.join(filepath, filename["transline_fix_cost"]))
    para["transline_variable_cost"] = read_two_dims(
        path.join(filepath, filename["transline_variable_cost"]))
    para["transmission_line_lifetime"] = read_two_dims(
        path.join(filepath, filename["transmission_line_lifetime"]))
    para["zv"] = read_break_point(path.join(filepath, filename["zv"]))
    para["zq"] = read_break_point(path.join(filepath, filename["zq"]))
    para["type"] = read_one_dims(path.join(filepath, filename["type"]))
    para["age"] = read_three_dims_one_idx_two_col(
        path.join(filepath, filename["age"]))
    para["storage_upbound"] = read_three_dims(
        path.join(filepath, filename["storage_upbound"]))
    para["storage_downbound"] = read_three_dims(
        path.join(filepath, filename["storage_downbound"]))
    para["storage_init"] = read_two_dims(
        path.join(filepath, filename["storage_init"]))
    para["storage_end"] = read_two_dims(
        path.join(filepath, filename["storage_end"]))
    para["hydropower"] = read_five_dims(path.join(filepath, filename["hydropower"]))
    para["inflow"] = read_four_dims_three_index_one_col(path.join(filepath, filename["inflow"]))
    para["connect"] = read_lag_time(path.join(filepath, filename["connect"]))
    para["static"] = read_hydro_static(path.join(filepath, filename["static"]))

    # Ascending order
    para["year"] = sorted(list(para["discount_factor"].keys()))
    para["stcd"] = list(set([i[1] for i in para["static"].keys()]))
    para["hour"] = sorted(
        list(set([i[3] for i in list(para["demand"].keys())])))
    para["month"] = sorted(
        list(set([i[2] for i in list(para["demand"].keys())])))
    para["zone"] = list(set([i[0] for i in list(para["demand"].keys())]))
    para["tech"] = list(para["type"].keys())

    df_invcost_factor = dict()
    df_fixcost_factor = dict()
    df_varcost_factor = dict()
    trans_invcost_factor = dict()
    y_min = min(para["year"])
    y_max = max(para["year"])

    # used to calculate cost
    for te in para["tech"]:
        for y in para["year"]:
            discount_rate = para["discount_factor"][y]
            next_modeled_year = y+1 if y == y_max else para["year"][
                para["year"].index(y) + 1]
            trans_invcost_factor[y] = invcost_factor(max(para["transmission_line_lifetime"].values(
            )), interest_rate=discount_rate, discount_rate=discount_rate, year_built=y,  year_min=y_min, year_max=y_max)
            df_invcost_factor[te, y] = invcost_factor(
                para["lifetime"][te, y], interest_rate=discount_rate, discount_rate=discount_rate, year_built=y,  year_min=y_min, year_max=y_max)
            df_fixcost_factor[y] = varcost_factor(discount_rate=discount_rate, modeled_year=y,
                                                  year_min=y_min, next_modeled_year=next_modeled_year)
            df_varcost_factor[y] = fixcost_factor(discount_rate=discount_rate, modeled_year=y,
                                                  year_min=y_min, next_modeled_year=next_modeled_year)

    para["inv_factor"] = df_invcost_factor
    para["fix_factor"] = df_fixcost_factor
    para["var_factor"] = df_varcost_factor
    para["trans_inv_factor"] = trans_invcost_factor

    return para
