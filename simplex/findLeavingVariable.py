from math import inf
from sympy import Symbol, Expr, Mul


def findLeavingVariable(constraints: list[Expr], xe: Symbol):
    """The function finds the leaving variable. It will return None if there are no leaving variables.

    Args:
        constraints (list[Expr]): The list of all constraints
        xe (Symbol): The entering variable

    Returns:
        _type_: The index of the selected constraint is to be pivoted, and xl if it finds any.
    """
    minimum = inf
    index = 0
    xl = None
    for i in range(len(constraints)):
        slack_var, rhs = constraints[i].args
        # A constraint with only one non-basic variable and no rhs
        rhs_literals = rhs.args if len(rhs.args) > 2 else [rhs]

        start_index = 0
        b_is_zero = True
        if type(rhs_literals[0]) != Symbol and type(rhs_literals[0]) != Mul:
            start_index = 1
            b_is_zero = False

        for rhs_literal in rhs_literals[start_index:]:
            try:
                coeff, literal = rhs_literal.args
            except ValueError:  # The coeff of non-basic variable is 1
                coeff = 1
                literal = rhs_literal
            if literal == xe and coeff < 0:
                if not b_is_zero and minimum > -rhs_literals[0] / coeff:
                    minimum = -rhs_literals[0] / coeff
                    index = i
                    xl = slack_var
                    break
                elif b_is_zero and minimum > 0:
                    minimum = 0
                    index = i
                    xl = slack_var
                    break

    return index, xl
