import pyoptinterface as poi
import numpy as np


class AddFinanceConstraints:
    """Class for financial calculations and constraints.
    """
    def __init__(self, model : object) -> None:
        """Initialize the class.

        Parameters
        ----------
        model : object
            Model object depending on the solver.

        """
        self.model = model
        model.cost_newtech_breakdown = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.cost_newtech_breakdown
        )
        model.public_debt_newtech = poi.make_tupledict(
            model.year, model.zone, model.tech,
            rule=self.public_debt_newtech
        )
        model.public_debt_upper_bound_system_cons = poi.make_tupledict(
            model.year,
            rule=self.public_debt_upper_bound_system_rule
        )
        model.public_debt_upper_bound_zone_cons = poi.make_tupledict(
            model.year, model.zone,
            rule=self.public_debt_upper_bound_zone_rule
        )

    def public_debt_newtech(
        self, y : int, z : str, te : str
    ) -> poi.ConstraintIndex:
        """Public debt investment calculation for each zone and technology.

        Parameters
        ----------
        y : int
            Planned year.
        z : str
            Zone.
        te : str
            Technology.

        Returns
        -------
        poi.ConstraintIndex
            A constraint of the model.
        """
        model = self.model
        return model.cost_newtech_breakdown[y, z, te] * model.params['public_debt_ratio'][te]

    def public_debt_upper_bound_system_rule(
        self, y : int
    ) -> poi.ConstraintIndex:
        """Public debt upper bound constraint for each zone and technology.

        Parameters
        ----------
        y : int
            Planned year.

        Returns
        -------
        poi.ConstraintIndex
            A constraint of the model.
        """
        model = self.model
        upper_bound = model.params['public_debt_upper_bound_system'][y]
        if upper_bound != np.Inf:
            lhs = poi.ExprBuilder(0)
            lhs += poi.quicksum(
                model.public_debt_newtech.select(y, '*', '*')
            )
            lhs -= upper_bound
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        return None

    def public_debt_upper_bound_zone_rule(
        self, y : int, z : str
    ) -> poi.ConstraintIndex:
        """Public debt upper bound constraint for each zone and technology.

        Parameters
        ----------
        y : int
            Planned year.
        z : str
            Zone.

        Returns
        -------
        poi.ConstraintIndex
            A constraint of the model.
        """
        model = self.model
        upper_bound = model.params['public_debt_upper_bound_zone'][z, y]
        if upper_bound != np.Inf:
            lhs = poi.ExprBuilder(0)
            lhs += poi.quicksum(
                model.public_debt_newtech.select(y, z, '*')
            )
            lhs -= upper_bound
            return model.add_linear_constraint(lhs, poi.Leq, 0)
        return None

    def cost_newtech_breakdown(
        self, y : int, z : str, te : str
    ) -> poi.ExprBuilder:
        """New technology investment cost breakdown.

        Parameters
        ----------
        y : int
            Year.
        z : str
            Zone.
        te : str
            Technology.

        Returns
        -------
        poi.ExprBuilder
            Investment cost of new technologies at a given year, zone and 
            technology.
        """
        model = self.model
        tic = model.params['technology_investment_cost'][te, y]
        ivf = model.params['inv_factor'][te, y, z]
        return tic * model.cap_newtech[y, z, te] * ivf