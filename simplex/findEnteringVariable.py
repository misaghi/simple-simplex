from sympy import Expr, Mul, Symbol
from math import inf
from sympy.core.function import _coeff_isneg


def findEnteringVariable(objective: Expr, blacklist: set):
    """This function returns the entering variable if there are any.

    Args:
        objective (Expr): The objective
        blacklist (set): The blacklisted variables. This is the list of variables which are unbounded.

    Returns:
        Symobl | None: xe if there are any or none.
    """
    objective_symbols = list(objective.args[1].args)
    maximum = -inf
    xe = None
    for sym in objective_symbols:  # Choose the most positive as entering
        # if sym's coeff is positive and is not a number
        if not _coeff_isneg(sym) and (type(sym) == Mul or type(sym) == Symbol):
            try:
                if maximum < sym.args[0] and sym.args[1] not in blacklist:
                    xe = sym.args[1]
                    maximum = sym.args[0]
            except IndexError:
                if maximum < 1 and sym not in blacklist:
                    xe = sym
                    maximum = 1

    return xe
