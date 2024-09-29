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
        print(f"Runtime of {func.__name__}: {end - start:.6f} seconds")
        return result  # Return the result of the wrapped function

    return wrapper

@time_it
def main_c():
    rubiks_cube = cube_module.Cube()
    rubiks_cube.random_shuffle(1000)

    solver = SolverC(rubiks_cube)
    solver.solve()
    # rubiks_cube.show()

@time_it
def main():
    rubiks_cube = Cube(3, debug=True)
    rubiks_cube.random_shuffle(1000)

    solver = Solver(rubiks_cube)
    solver.solve()
    # rubiks_cube.show()


if __name__ == '__main__':
    main()
    main_c()
