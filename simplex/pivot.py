from sympy import Expr, Symbol, Eq, Mul, Add


def pivot(expression: Expr, xe: Symbol, xl: Symbol):
    """This function does only one thing: Given an expression, it rewrites it with new xe.

    Args:
        expression (Expr): The constraint
        xe (Symbol): The variable to be entered
        xl (Symbol): The leaving variable (It wasn't used though)

    Returns:
        Expr: The pivoted expression
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
