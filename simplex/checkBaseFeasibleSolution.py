from sympy import Expr, Symbol, Mul


def checkBaseFeasibleSolution(constraints: list[Expr]):
    """This function checks if the basic solution is feasible or not.

    Args:
        constraints (list[Expr]): List of all constraints

    Returns:
        boolean: True if base solution is feasible. o.w. False
    """
    for constraint in constraints:
        lhs, rhs = constraint.args
        lhs_literals = lhs.args
        if type(lhs_literals[0]) != Mul and type(lhs_literals[0]) != Symbol and lhs_literals[0] > 0:
            return False
    return True
