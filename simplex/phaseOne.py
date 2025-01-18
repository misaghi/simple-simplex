from sympy import Expr, Symbol, Mul
from sympy.core.function import _coeff_isneg
from math import inf
from .createSlackForm import createSlackForm
from .pivot import pivot
from .findLeavingVariable import findLeavingVariable
from .findEnteringVariable import findEnteringVariable


def phaseOne(objective: Expr, constraints: list[Expr]):
    """The first phase of the Two Phase Method
    It checks for the feasibility of the LP using the auxiliary LP.

    Args:
        objective (Expr): _description_
        constraints (list[Expr]): _description_

    Returns:
        The list of new constraints
    """
    slack_objective, slack_constraints = createSlackForm(
        Symbol('x0'), constraints, phase_one=True)

    iteration = 1
    blacklist = set()
    while True:
        if iteration == 1:  # The first iteration in which x0 must be chosen and entering variable
            print(f'The dictionary at the start of the iteration {
                iteration} of the 1st phase is:')
            print('Objective:', slack_objective)
            print('s.t.:', *slack_constraints, sep='\n')
            print()

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

            print(f'({xe}) is chosen as entering  & ({
                  xl}) is chosen as leaving.', end='\n\n')

            slack_constraints[index] = pivot(  # Do the pivoting
                slack_constraints[index], xe, xl)

            # The process of substituting xl with xe
            for i in range(len(slack_constraints)):
                if i == index:
                    continue
                slack_constraints[i] = slack_constraints[i].subs(
                    xe, slack_constraints[index].args[1])

            slack_objective = slack_objective.subs(  # In the objective too!
                xe, slack_constraints[index].args[1])

        else:
            objective_symbols = list(slack_objective.args[1].args)
            if len(objective_symbols) == 2 and objective_symbols[0] == -1 and objective_symbols[1].name == 'x0':
                # There is only -x0 in the objective. z=0 and LP is feasible.
                # Substitue x0 with 0
                return [constraint.subs(objective_symbols[1], 0) for constraint in slack_constraints]

            xe = findEnteringVariable(slack_objective, blacklist)

            # All the basics' coefficients are negative; no could be selected.
            if not xe and len(blacklist) < len(objective_symbols):
                print('LP is not feasible!')
                return  # LP is infeasible
            elif not xe and len(blacklist) == len(objective_symbols):
                print('LP is unbounded!')
                return

            index, xl = findLeavingVariable(slack_constraints, xe)

            if not xl:
                blacklist.add(xe)
                continue
            else:
                blacklist = set()

            print(f'({xe}) is chosen as entering  & ({
                  xl}) is chosen as leaving.', end='\n\n')
            slack_constraints[index] = pivot(
                slack_constraints[index], xe, xl)

            for i in range(len(slack_constraints)):
                if i == index:
                    continue
                slack_constraints[i] = slack_constraints[i].subs(
                    xe, slack_constraints[index].args[1])

            slack_objective = slack_objective.subs(
                xe, slack_constraints[index].args[1])

        print(f'The dictionary at the end of the iteration {
              iteration} of the 1st phase is:')
        print('Objective:', slack_objective)
        print('s.t.:', *slack_constraints, sep='\n')
        print()
        iteration += 1
