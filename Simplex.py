import pathlib
from sympy import Symbol, sympify, Mul, Expr, Ge, Le, Add, Eq
from sympy.core.function import _coeff_isneg
from math import inf


def main():
    pass


def getAllVariables(objective: Expr, constraints: list[Expr]):
    """Returns all variables in objective and constraints

    Args:
        objective (Expr): _description_
        constraints (list[Expr]): _description_

    Returns:
        _type_: _description_
    """
    variables = list()
    variables.extend(list(objective.free_symbols))
    for constraint in constraints:
        variables.extend(list(constraint.free_symbols))

    return list(set(variables))


def normalize(problem_type: str, objective: Expr, constraints: list[Expr]):
    """
    1. Check if the problem type is maximization or not
    2. Check for '=' constraints and replace it with '<=' and '>='
    3. Check for 'Xi >= 0' constraints and add X'i and X"i if it is needed
    4. Replace >= with <= where it is necessary

    Args:
        problem_type (str): _description_
        objective (Expr): _description_
        constraints (list[Expr]): _description_
    """
    # Checking the first condition
    if problem_type.lower() == 'minimize':
        objective = Mul(objective, -1)
        problem_type = 'maximize'

    # Checking the second condition
    for constraint in constraints:
        if type(constraint) == Eq:
            constraints.append(Ge(*constraint.args))
            constraints.append(Le(*constraint.args))
            constraints.remove(constraint)

    # Checking the third condition
    variables = getAllVariables(objective, constraints)
    for variable in variables:
        for constraint in constraints:
            constraint_args = constraint.args
            greater_than_flag = False
            if len(constraint_args) == 2 and constraint_args[0] == variable and constraint_args[1] == 0:
                greater_than_flag = True
                break
        if not greater_than_flag:
            # constraints.append()
            variable_name = variable.name
            xp = Symbol(variable_name[:1] + "'" + variable_name[1:])
            xpp = Symbol(variable_name[:1] + "\"" + variable_name[1:])
            constraints.append(Ge(xpp, 0))
            constraints.append(Ge(xp, 0))
            for i in range(len(constraints)):
                constraints[i] = constraints[i].subs(
                    variable, xp - xpp)  # Replace xi with x'i and x"i in each constraint

            # Replace xi with x'i and x"i in objective
            objective = objective.subs(variable, xp - xpp)

    for i in range(len(constraints)):
        lhs, rhs = constraints[i].args
        if len(lhs.args) >= 2 and type(constraints[i]) == Ge:
            constraints[i] = Le(
                Mul(sympify(Add(*list(lhs.args))), -1), Mul(rhs, -1))

    final_constraints = list()
    for constraint in constraints:
        if len(constraint.args[0].args) >= 2:
            final_constraints.append(constraint)

    return objective, final_constraints


def createSlackForm(objective: Expr | Symbol, constraints: list[Expr], phase_one=False):
    """Creates Slack Form from normalized objective and constraints

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


def checkBaseFeasibleSolution(constraints: list[Expr]):
    """The function checkes whether or not all rhs are greater or equal to 0

    Args:
        constraints (list[Expr]): _description_

    Returns:
        _type_: _description_
    """
    for constraint in constraints:
        rhs = constraint.args[1]
        if rhs < 0:
            return False
    return True


def pivot(expression: Expr, xe: Symbol, xl: Symbol):
    """This function does only one thing: Given an expression, it rewrites it with new xe

    Args:
        expression (Expr): _description_
        xe (Symbol): _description_
        xl (Symbol): _description_

    Returns:
        _type_: _description_
    """
    slack_var, rhs = expression.args
    rhs_literals = list(rhs.args)
    # Let's find the coeff of the entering
    for rhs_literal in rhs_literals[1:]:
        try:
            if rhs_literal.args[1] == xe:
                # The coefficient is greater than 1
                coeff = -rhs_literal.args[0]
                rhs_literals.remove(rhs_literal)
                break
        except IndexError:
            if rhs_literal == xe:
                coeff = -1
                rhs_literals.remove(rhs_literal)
                break  # The coefficient is 1

    return Eq(xe, Mul(Add(*rhs_literals, Mul(slack_var, -1)), 1/coeff))


def phaseOne(objective: Expr, constraints: list[Expr]):
    """Two phase implementation: Phase 1
    Check for feasibility of the LP using auxiliary LP

    Args:
        objective (Expr): _description_
        constraints (list[Expr]): _description_
    """
    slack_objective, slack_constraints = createSlackForm(
        Symbol('x0'), constraints, phase_one=True)

    # print(slack_objective)
    # print(*slack_constraints, sep='\n')
    # return

    iteration = 1
    while True:
        if iteration == 1:  # The first iteration in which x0 should be chosen and entering variable
            objective_symbols = list(slack_objective.args)
            for sym in objective_symbols:
                if _coeff_isneg(sym):
                    xe = sym.args[1]  # Choose x0 as entering

            minimum = inf
            index = 0
            # Choose the most negative variable as leaving
            for i in range(len(slack_constraints)):
                slack_var, rhs = slack_constraints[i].args
                try:
                    if minimum > rhs.args[0]:
                        minimum = rhs.args[0]
                        xl = slack_var
                        index = i
                # b is zero; therefore it gives a TypeError because it compares a number with a Symobl.
                except TypeError:
                    if minimum > 0:
                        minimum = 0
                        xl = slack_var  # Choose the most negative variable as leaving
                        index = i

            # print(slack_constraints[index])
            # return

            slack_constraints[index] = pivot(  # Do the pivoting
                slack_constraints[index], xe, xl)

            # print(slack_constraints[index])
            # return

            # The process of substituting xl with xe
            for i in range(len(slack_constraints)):
                if i == index:
                    continue
                slack_constraints[i] = slack_constraints[i].subs(
                    xe, slack_constraints[index].args[1])

            slack_objective = slack_objective.subs(  # In the objective too!
                xe, slack_constraints[index].args[1])

            # print(slack_objective)
            # print(*slack_constraints, sep='\n')
        else:
            objective_symbols = list(slack_objective.args[1].args)
            if len(objective_symbols) == 2 and objective_symbols[0] == -1 and objective_symbols[1].name == 'x0':
                # There is only -x0 in the objective. z=0 and LP is feasible.
                # Substitue x0 with 0
                return [constraint.subs(objective_symbols[1], 0) for constraint in slack_constraints]
            maximum = -inf
            xe = None
            xl = None
            # Choose the most positive as entering
            for sym in objective_symbols:
                # sym's coeff is not negative and it is not a number
                if not _coeff_isneg(sym) and (type(sym) == Mul or type(sym) == Symbol):
                    try:
                        if maximum < sym.args[0]:
                            xe = sym.args[1]
                            maximum = sym.args[0]
                    except IndexError:  # The coefficient is 1 but in the expression it is sth like Xi
                        if maximum < 1:
                            xe = sym
                            maximum = 1
            if not xe:  # All the basics' coefficients are negative; no could be selected.
                print('LP is not feasible!')
                exit()  # LP is infeasible

            minimum = inf
            index = 0
            for i in range(len(slack_constraints)):  # Find the leaving variable
                slack_var, rhs = slack_constraints[i].args
                rhs_literals = rhs.args if len(rhs.args) > 2 else [rhs]

                start_index = 1
                b_is_zero = False
                try:
                    # Is b zero? Raises "ValueError" if b is zero.
                    rhs_literals[0] > 0
                except ValueError:
                    start_index = 0
                    b_is_zero = True

                # If b is zero, we should start from 2nd item in the list
                # Finding the xl
                for rhs_literal in rhs_literals[start_index:]:
                    if rhs_literal.args[1] == xe and rhs_literal.args[0] < 0:
                        if not b_is_zero and minimum > -rhs_literals[0] / rhs_literal.args[0]:
                            minimum = -rhs_literals[0] / rhs_literal.args[0]
                            index = i
                            xl = slack_var
                            break
                        elif b_is_zero and minimum > 0:  # b is zero.
                            minimum = 0
                            index = i
                            xl = slack_var
                            break

            print(f'Chosen xe is {xe} & Chosen xl is {xl}', end='\n\n')
            slack_constraints[index] = pivot(
                slack_constraints[index], xe, xl)

            for i in range(len(slack_constraints)):
                if i == index:
                    continue
                slack_constraints[i] = slack_constraints[i].subs(
                    xe, slack_constraints[index].args[1])

            slack_objective = slack_objective.subs(
                xe, slack_constraints[index].args[1])

        print(f'Dictionary at the end of iteration {
              iteration} of the 1st phase is:')
        print('Objective:', slack_objective)
        print('s.t.:', *slack_constraints, sep='\n')
        print()
        iteration += 1


def simplex(objective: Expr, constraints: list[Expr]):
    objective_symbols = list(objective.free_symbols)

    for symbol in objective_symbols:  # Rewrite the objective with the non basic variables
        for constraint in constraints:
            slack_var, rhs = constraint.args
            if slack_var == symbol:
                objective = objective.subs(symbol, rhs)
                break

    iteration = 1
    print(f'Dictionary at the end of iteration {
        iteration} of the 2nd phase is:')
    print('Objective:', objective)
    print('s.t.:', *constraints, sep='\n')
    print()
    while True:
        objective_symbols = list(objective.args[1].args)
        maximum = -inf
        xe = None
        xl = None
        for sym in objective_symbols:  # Choose the most positive as entering
            # if sym's coeff is positive and is not a number
            if not _coeff_isneg(sym) and (type(sym) == Mul or type(sym) == Symbol):
                try:
                    if maximum < sym.args[0]:
                        xe = sym.args[1]
                        maximum = sym.args[0]
                except IndexError:
                    if maximum < 1:
                        xe = sym
                        maximum = 1
        if not xe:  # All the objective variable coefficients are negative, and we are finished!
            print('Answer:', objective_symbols[0] if (type(
                objective_symbols[0]) != Symbol and type(objective_symbols[0]) != Mul) else 0)
            print(f'Final dictionary was calculated at iteration {
                iteration} of the 2nd phase:')
            print('Objective:', objective)
            print('s.t.:', *constraints, sep='\n')
            print()
            exit()

        minimum = inf
        index = 0
        for i in range(len(constraints)):  # Find the leaving variable
            slack_var, rhs = constraints[i].args
            # Possibility of existing a constraint with only a signle variable in its rhs
            rhs_literals = rhs.args if len(rhs.args) > 2 else [rhs]

            start_index = 1
            b_is_zero = False
            try:
                rhs_literals[0] > 0  # Is b zero?
            except ValueError:
                start_index = 0
                b_is_zero = True

            for rhs_literal in rhs_literals[start_index:]:
                if rhs_literal.args[1] == xe and rhs_literal.args[0] < 0:
                    if not b_is_zero and minimum > -rhs_literals[0] / rhs_literal.args[0]:
                        minimum = -rhs_literals[0] / rhs_literal.args[0]
                        index = i
                        xl = slack_var
                        break
                    elif b_is_zero and minimum > 0:
                        minimum = 0
                        index = i
                        xl = slack_var
                        break

        if not xl:
            print('LP is unbounded!')
            exit()

        print(f'Chosen xe is {xe} & Chose xl is {xl}', end='\n\n')
        constraints[index] = pivot(
            constraints[index], xe, xl)

        for i in range(len(constraints)):
            if i == index:
                continue
            constraints[i] = constraints[i].subs(
                xe, constraints[index].args[1])

        objective = objective.subs(
            xe, constraints[index].args[1])

        print(f'Dictionary at the end of iteration {
            iteration} of the 2nd phase is:')
        print('Objective:', objective)
        print('s.t.:', *constraints, sep='\n')
        print()
        iteration += 1


def readInput():
    """How to write input?
    1. Problem type(minimize or maximize) must be seperated by a ':' from the objective.
    2. Every constraint must be written in a new line.
    3. The LP's type can be in lower case or upper case. It doesn't matter.
    4. After writing the objective, there must be a "s.t." line.

    Returns:
        _type_: _description_
    """
    with open(pathlib.Path(__file__).parent / 'input.txt') as file:
        lines = file.readlines()
        problem_type, objective = lines[0].split(':')
        objective = sympify(objective)
        problem_type = problem_type.strip()
        constraints = list()
        for line in lines[2:]:
            try:
                constraints.append(sympify(line))
            except ValueError:
                eq_index = line.find('=')
                constraints.append(
                    Eq(sympify(line[:eq_index]), sympify(line[eq_index+1:-1])))

    return problem_type, objective, constraints


def main():
    problem_type, objective, constraints = readInput()
    normalized_objective, normalized_constraints = normalize(
        problem_type, objective, constraints)
    if checkBaseFeasibleSolution(normalized_constraints):
        slack_objective, slack_constraints = createSlackForm(
            normalized_objective, normalized_constraints)
        simplex(slack_objective, slack_constraints)
    else:
        phase_one_constraints = phaseOne(
            normalized_objective, normalized_constraints)
        simplex(normalized_objective, phase_one_constraints)

        # print(normalized_objective)
        # print(*normalized_constraints, sep='\n')


if __name__ == '__main__':
    main()
