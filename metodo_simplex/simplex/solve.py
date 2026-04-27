from .algoritmo.simplex_solver import SimplexSolver
from .algoritmo.two_phases_solver import TwoPhaseSolver
from .types import ConstraintType
from .problem import LinearProgram

def requires_two_phase(lp: LinearProgram) -> bool:
    return any(
        c in (ConstraintType.GE, ConstraintType.EQ)
        for c in lp.constraints
    )

def solve(problem: LinearProgram, trace: bool = False):
    if requires_two_phase(problem):
        return TwoPhaseSolver(trace).solve(problem)
    
    return SimplexSolver(trace).solve(problem)