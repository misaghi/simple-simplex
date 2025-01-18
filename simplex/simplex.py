from sympy import Expr, Mul, Symbol
from math import inf
from .pivot import pivot
from .findLeavingVariable import findLeavingVariable
from .findEnteringVariable import findEnteringVariable


def simplex(objective: Expr, constraints: list[Expr]):
    """This function implements the second phase of the Two Phase Method.

    Args:
        objective (Expr): The objective of previous phases
        constraints (list[Expr]): The list of the constraints
    """
    objective_symbols = list(objective.free_symbols)

    for symbol in objective_symbols:  # Rewrite the objective with the non basic variables
        for constraint in constraints:
            slack_var, rhs = constraint.args
            if slack_var == symbol:
                objective = objective.subs(symbol, rhs)
                break

    iteration = 1
    print(f'The dictionary at the start of the iteration {
        iteration} of the 2nd phase is:')
    print('Objective:', objective)
    print('s.t.:', *constraints, sep='\n')
    print()

    blacklist = set()
    while True:
        objective_symbols = list(objective.args[1].args)
        xe = findEnteringVariable(objective, blacklist)
        # All the objective variable coefficients are negative, and there are no unbounded variables.
        # This means we are finished.
        if not xe and len(blacklist) == 0:
            print('Answer:', objective_symbols[0] if (type(
                objective_symbols[0]) != Symbol and type(objective_symbols[0]) != Mul) else 0)
            print(f'The final dictionary was calculated at the iteration {
                iteration} of the 2nd phase:')
            print('Objective:', objective)
            print('s.t.:', *constraints, sep='\n')
            print()
            return

        # There are no candidates to be the entering variables other than unbounded ones.
        elif not xe and len(blacklist) != 0:
            print('LP is unbounded!')
            return

        index, xl = findLeavingVariable(constraints, xe)

        # This means none of the constraints can define a bound.
        # The corresponding variable will be added to the blacklist
        if not xl:
            blacklist.add(xe)
            continue
        else:  # The blacklist may be empty or not. It doesn't matter; we've found a suitable constraint for pivoting
            blacklist = set()

        print(f'({xe}) is chosen as entering  & ({
              xl}) is chosen as leaving.', end='\n\n')
        constraints[index] = pivot(
            constraints[index], xe, xl)

        for i in range(len(constraints)):
            if i == index:
                continue
            constraints[i] = constraints[i].subs(
                xe, constraints[index].args[1])

        objective = objective.subs(
            xe, constraints[index].args[1])

        print(f'The dictionary at the end of the iteration {
            iteration} of the 2nd phase is:')
        print('Objective:', objective)
        print('s.t.:', *constraints, sep='\n')
        print()
        iteration += 1
