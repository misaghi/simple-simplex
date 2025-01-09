from sympy import Mul, Symbol, Expr, Ge, Le, Add, sympify, Eq
from .getAllVariables import getAllVariables


def normalize(problem_type: str, objective: Expr, constraints: list[Expr]):
    """
    1. Checks if the problem type is maximization or not
    2. Checks for '=' constraints and replace it with '<=' and '>='
    3. Checks for 'Xi >= 0' constraints and add X'i and X"i if it is needed
    4. Replaces >= with <= where it is necessary

    Args:
        problem_type (str): The problem type: minimize or maximize
        objective (Expr): The objective
        constraints (list[Expr]): The list of constraints

    Returns:
        The normalized objective and constraints
    """
    # Checking the first condition
    if problem_type.lower() == 'minimize':
        objective = Mul(objective, -1)
        problem_type = 'maximize'

    # Checking the second condition
    phase_2_constraints = list()
    for constraint in constraints:
        if type(constraint) == Eq:
            phase_2_constraints.append(Ge(Add(*constraint.args), 0))
            phase_2_constraints.append(Le(Add(*constraint.args), 0))
        else:
            phase_2_constraints.append(constraint)

    # Checking the third condition
    variables = getAllVariables(objective, phase_2_constraints)
    phase_3_constraints = phase_2_constraints[:]
    for variable in variables:
        for constraint in phase_3_constraints:
            constraint_args = constraint.args
            greater_than_flag = False  # Checks if Xi >= 0 presents or not
            if len(constraint_args) == 2 and constraint_args[0] == variable and constraint_args[1] == 0:
                greater_than_flag = True
                break

        if not greater_than_flag:
            variable_name = variable.name
            xp = Symbol(variable_name[:1] + "'" + variable_name[1:])
            xpp = Symbol(variable_name[:1] + "\"" + variable_name[1:])
            phase_3_constraints.append(Ge(xpp, 0))
            phase_3_constraints.append(Ge(xp, 0))
            for i in range(len(phase_3_constraints)):
                phase_3_constraints[i] = phase_3_constraints[i].subs(
                    variable, xp - xpp)  # Replace xi with x'i and x"i in each constraint

            # Replace xi with x'i and x"i in objective
            objective = objective.subs(variable, xp - xpp)

    # Checking the forth condition
    phase_4_constraints = list()
    for i in range(len(phase_3_constraints)):
        lhs, rhs = phase_3_constraints[i].args
        if type(phase_3_constraints[i]) == Ge:
            if type(rhs) != Mul and type(rhs) != Symbol and rhs == 0 and len(lhs.args) <= 1:
                pass
            else:  # Adds sth like Xi - rhs <= 0 to the 4th step's dictionary
                phase_4_constraints.append(Le(
                    Mul(sympify(Add(*list(lhs.args), Mul(rhs, -1))), -1), 0))
        else:  # Adds sth like Xi - rhs <= 0 to the 4th step's dictionary
            phase_4_constraints.append(Le(
                sympify(Add(*list(lhs.args), Mul(rhs, -1))), 0))

    return objective, phase_4_constraints
