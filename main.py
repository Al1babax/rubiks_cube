from rubiks_cube import Cube
from solver import Solver

def main():
    rubiks_cube = Cube(3, debug=True)
    rubiks_cube.random_shuffle(1000)
    solver = Solver(rubiks_cube)
    solver.solve()
    rubiks_cube.controls()

if __name__ == '__main__':
    main()