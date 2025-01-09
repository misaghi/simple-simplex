from sympy import Symbol, Expr, Mul, Eq, Add


def createSlackForm(objective: Expr | Symbol, constraints: list[Expr], phase_one=False):
    """Creates Slack Form from the normalized objective and constraints

    Args:
        objective (Expr | Symbol): Symbol varient is used for first phase. Other than that it is always an Expr
        constraints (list[Expr]): A list of constraints
        phase_one (bool, optional): Must be true if we are passing the auxiliary dictionary's objective and constraints. Defaults to False.

    Returns:
        _type_: slack_objective, slack_constraints
    """
    z = Symbol('z')
    slack_objective = Eq(z, Mul(objective, -1)
                         ) if phase_one else Eq(z, objective)
    slack_constraints = list()
    counter = 1
    for constraint in constraints:
        lhs, rhs = constraint.args
        var = Symbol(f'w{counter}')
        slack_constraints.append(Eq(var, Add(Add(Mul(lhs, -1), objective),
                                             rhs) if phase_one else Add(Mul(lhs, -1), rhs)))
        counter += 1

    return slack_objective, slack_constraints
