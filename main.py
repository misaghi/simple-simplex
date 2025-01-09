from simplex.readInput import readInput
from simplex.normalize import normalize
from simplex.checkBaseFeasibleSolution import checkBaseFeasibleSolution
from simplex.createSlackForm import createSlackForm
from simplex.simplex import simplex
from simplex.phaseOne import phaseOne
import pathlib


def main():
    path = pathlib.Path(__file__).parent / 'inputs'
    dir = path.walk().__next__()
    for file in dir[2]:
        print(f'_______________________Solving {file}_______________________')
        input_path = path / file
        problem_type, objective, constraints = readInput(input_path)
        normalized_objective, normalized_constraints = normalize(
            problem_type, objective, constraints)
        if checkBaseFeasibleSolution(normalized_constraints):
            slack_objective, slack_constraints = createSlackForm(
                normalized_objective, normalized_constraints)
            simplex(slack_objective, slack_constraints)
        else:
            phase_one_constraints = phaseOne(
                normalized_objective, normalized_constraints)
            if phase_one_constraints:
                simplex(normalized_objective, phase_one_constraints)


if __name__ == '__main__':
    main()
