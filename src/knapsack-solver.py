# knapsack-solver.py

# Original author: Lorenzo Lopez
# Refactoring: Antonio Rocchia

# Dependencies: PulP
# $ pip install -r requirements.txt

import argparse
from sys import stderr, exit

from pulp import LpMaximize, LpProblem, LpVariable

class ProblemInput:

    def __init__(self, objective_coefficients: list[int], constraint_coefficients: list[int], capacity: int, extra_constraints: dict[int, tuple[str,int]]):
        self.objective_coefficients = objective_coefficients
        self.constraint_coefficients = constraint_coefficients
        self.capacity = capacity
        self.extra_constraints = extra_constraints

class ProblemSolution:

    def __init__(self, decision_variables, objective_variables):
        self.decision_variables = decision_variables
        self.objective_variables = objective_variables

def setup_argparser() -> argparse.ArgumentParser: 
    # Initialize the argument parser for the program
    parser = argparse.ArgumentParser(
        description="Algorithm for testing knapsack problems with integer decision variables.",
        epilog="Original author: Lorenzo Lopez\nRefactoring: Antonio Rocchia"
    )

    parser.add_argument("-i", "--input", help="Input file for the program", type=str)
    parser.add_argument("-o", "--output", help="Output file for the program", type=str)
    parser.add_argument("--interactive", help="Interactive mode", action="store_true")

    return parser

def askConfirm(message: str, yes_string: str = "y", no_string: str = "n", quit_string: str = "exit") -> bool:
    usr_input = input(message)
    while usr_input != yes_string and usr_input != no_string and usr_input != quit_string:
        print("Error: " + usr_input + " is not a valid input.", file=stderr)
        usr_input = input(message)

    if usr_input == yes_string:
        return True
    elif usr_input == no_string:
        return False
    else:
        exit()

def get_integer_input(message: str):
    while True:
        usr_input = input(message)
        try:
            number = int(usr_input)
            return number
        except ValueError:
            print("Error: impossible to convert '" + usr_input + "' to an integer.", file=stderr)
            if not askConfirm("Retry? (y/n) [or type 'exit' to quit the program]: "):
                exit()
            else:
                continue

def print_tabular_representation(objective_coefficients: list[int], constraint_coefficients: list[int], capacity: int, extra_constraints: dict[int, tuple[str,int]]):
    # A column to display the table header
    table_format = "{:>20} "

    for i in range(len(objective_coefficients)):
        # A new column for each coefficient
        table_format += "{:>8} "

    # A column for the constraints
    table_format += "{:>4} "
    # Column for the capacity
    table_format += "{:>8}"
    
    # First row
    print(table_format.format("", *range(len(objective_coefficients)), "", "capacity"))
    # Second riga
    print(table_format.format("Objective", *objective_coefficients, "", ""))
    # Third row
    print(table_format.format("Main constraint", *constraint_coefficients, "<=", capacity))
    # Forth row
    ## Alline extra constraints in the table
    ordered_extra_constraints: list[str] = []
    for i in range(len(objective_coefficients)):
        if i in extra_constraints:
            tipo_vincolo, valore = extra_constraints[i]
            ordered_extra_constraints.append(tipo_vincolo + " "+ str(valore))
        else:
            ordered_extra_constraints.append("")

    print(table_format.format("Extra constraints", *ordered_extra_constraints, "", ""))


        

def get_input_interactively():
    print(
    """
    ==============================================================================
    Algorithm for testing knapsack problems with integer decision variables.
    Note: It is necessary to sort the variables before using the program.
    ==============================================================================
    """
    )

    num_var: int = get_integer_input("Number of variables: ")

    objective_coefficients: list[int] = []
    for i in range(num_var):
        objective_coefficients.append(get_integer_input("Objective coefficient n° {}: ".format(i)))

    constraint_coefficients: list[int] = []
    for i in range(num_var):
        constraint_coefficients.append(get_integer_input("Constraint coefficient n° {}: ".format(i)))

    capacity: int = get_integer_input("Capacity: ")

    extra_constraints: dict[int, tuple[str, int]] = {}
    while askConfirm("Do you want to add or modify extra constraints? (y/n) [or type 'exit' to quit the program]: "):
        print_tabular_representation(objective_coefficients, constraint_coefficients, capacity, extra_constraints)

        index = get_integer_input("Choose the variable to constrain: ")

        # Check if the extra bounds has been set already, if that's the case give the chance to delete the 
        if index in extra_constraints:
            print("The extra constraint for the variable {} has already been set to {}".format(index, extra_constraints[index]))
            if not askConfirm("Do you want to modify the constraint? (y/n) [or type 'exit' to quit the program]: "):
                continue

        if index >= len(objective_coefficients) or index < 0:
            print("Error: The specified index doesn't point to an objective coefficient", file=stderr)
            continue
        else:
            input_constraint_type = input("Choose a constraint type: ['<=' or '>=']: ")
            while input_constraint_type != "<=" and input_constraint_type != ">=":
                print("Error: '" +input_constraint_type + "' is not a valid constraint type.", file=stderr)
                input_constraint_type = input("Choose a constraint type: ['<=' or '>=']: ")
        
        constraint = get_integer_input("Constraint value: ")
        extra_constraints[index] = (input_constraint_type, constraint)

    return ProblemInput(objective_coefficients, constraint_coefficients, capacity, extra_constraints)

def solveProblem(input: ProblemInput):
    problem = LpProblem("Knapsack problem", LpMaximize)
    variables = LpVariable.dicts("x", range(len(input.objective_coefficients)), lowBound=0, cat="Integer")

    for key, constraint in input.extra_constraints.items():
        constraint_type, constraint_value = constraint
        if constraint_type == "<=":
            problem += variables[key] <= constraint_value
        elif constraint_type == ">=":
            problem += variables[key] >= constraint_value

    # Genero funzione obbiettivo
    problem += sum(input.objective_coefficients[i] * variables[i] for i in range(len(input.objective_coefficients)))

    # Genero vincolo principale
    problem += sum(input.constraint_coefficients[i] * variables[i] for i in range(len(input.constraint_coefficients))) <= input.capacity

    problem.solve()

    # Estrazione risultati
    return ProblemSolution([variables[i].varValue for i in range(len(input.objective_coefficients))], problem.objective.value())

if __name__ == "__main__":
    parser = setup_argparser()
    args = parser.parse_args()

    problem_input: ProblemInput 
    if(args.interactive):
       problem_input = get_input_interactively()

    solution: ProblemSolution = solveProblem(problem_input)

    # Print dei risultati in output
    print("Valori decisionali: ", solution.decision_variables)
    print("Valore ottimo z: ", solution.objective_variables)

