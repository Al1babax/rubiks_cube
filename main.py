from rubiks_cube import Cube
from solver import Solver
from solver_c import SolverC
import time
import cube_module

def time_it(func):
    """Decorator to measure the runtime of a function."""

    def wrapper(*args, **kwargs):
        start = time.perf_counter()  # Start timing
        result = func(*args, **kwargs)  # Call the wrapped function
        end = time.perf_counter()  # End timing
        print(f"Runtime of {func.__name__}: {end - start:.6f} seconds\n")
        return result  # Return the result of the wrapped function

    return wrapper


def solve_in_py(speed_test=False):
    rubiks_cube = Cube(3, debug=True)
    rubiks_cube.random_shuffle(1000)

    if not speed_test:
        rubiks_cube.show()

    solver = Solver(rubiks_cube)
    solver.solve()

    if speed_test is False:
        rubiks_cube.show()


def solve_in_c(speed_test=False):
    rubiks_cube = cube_module.Cube()
    rubiks_cube.random_shuffle(1000)

    if not speed_test:
        rubiks_cube.show()

    solver = SolverC(rubiks_cube)
    solver.solve()

    if speed_test is False:
        rubiks_cube.show()


def py_speed_test(amount):
    print("Running python speed test: ")
    for i in range(amount):
        if i % 50 == 0:
            print(f"Running {i} --> {i + 50}")

        solve_in_py(speed_test=True)

    print("Done")


def c_speed_test(amount):
    print("Running c speed test: ")
    for i in range(amount):
        if i % 50 == 0:
            print(f"Running {i} --> {i + 50}")

        solve_in_c(speed_test=True)

    print("Done")


@time_it
def main_c(run_speed_test=False, amount=100):
    if run_speed_test:
        c_speed_test(amount)
    else:
        solve_in_c()


@time_it
def main(run_speed_test=False, amount=100):
    if run_speed_test:
        py_speed_test(amount)
    else:
        solve_in_py()


if __name__ == '__main__':
    # TO RUN MAIN_C YOU NEED CUSTOM MODULE
    speed_test_iterations = 1000
    speed_test = False

    main(speed_test, speed_test_iterations)
    main_c(speed_test, speed_test_iterations)
