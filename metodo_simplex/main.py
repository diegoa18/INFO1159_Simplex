from __future__ import annotations

from simplex import InfeasibleError, UnboundedError, solve
from simplex.input_parser import build_problem_from_input


def main() -> None:
    problem = build_problem_from_input()

    # RESOLUCION
    try:
        solution = solve(problem, trace=True)
        print("SOLUCION OPTIMA")
        print("-" * 60)

        print(f"valor optimo: {solution.optimal_value:.6f}")

        for i, val in enumerate(solution.variables, start=1):
            print(f"x{i} = {val:.6f}")

        print(f"iteraciones: {solution.iterations}")

    except UnboundedError as e:
        print("cueck")
        print(e)

    except InfeasibleError as e:
        print("es infactible")
        print(e)


if __name__ == "__main__":
    main()
