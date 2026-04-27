from dataclasses import dataclass

@dataclass(frozen=True)
class Solution:
    optimal_value: float
    variables: tuple[float, ...]  # vector solucion
    is_optimal: bool
    iterations: int