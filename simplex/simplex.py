from sympy import Expr, Mul, Symbol
from math import inf
from .pivot import pivot
from .findLeavingVariable import findLeavingVariable
from sympy.core.function import _coeff_isneg


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

        index, xl = findLeavingVariable(constraints, xe)

        if not xl:
            print('LP is unbounded!')
            exit()

        print(f'{xe} is chosen as entering  & {
              xl} is chosen as leaving.', end='\n\n')
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
