from sympy import Expr


def getAllVariables(objective: Expr, constraints: list[Expr]):
    """Returns all the variables in the objective and constraints

    Args:
        objective (Expr): _description_
        constraints (list[Expr]): _description_

    Returns:
        list: A list of all variables
    """
    variables = list()
    variables.extend(list(objective.free_symbols))
    for constraint in constraints:
        variables.extend(list(constraint.free_symbols))

    return list(set(variables))
