import pathlib
from sympy import sympify, Eq


def readInput(path: pathlib.Path):
    """How to write input?
    1. Problem type(minimize or maximize) must be seperated by a ':' from the objective.
    2. Every constraint must be written in a new line.
    3. The LP's type can be in lower case or upper case. It doesn't matter.
    4. After writing the objective, there must be a "s.t." line.

    Args:
        path (pathlib.Path)

    Returns:
        The problem type, objective, and constraints
    """
    with open(path) as file:
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
