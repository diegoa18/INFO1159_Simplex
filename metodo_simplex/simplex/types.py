from __future__ import annotations

from enum import IntEnum
from typing import TypeAlias
import numpy as np
import numpy.typing as npt

class ConstraintType(IntEnum):
    LE = 1  # <=
    GE = 2  # >=
    EQ = 3  # =

class ObjectiveType(IntEnum):
    MAX = 1
    MIN = -1

EPSILON: float = 1e-10
MAX_ITERATIONS: int = 10000

Matriz: TypeAlias = npt.NDArray[np.float64]
Tupla: TypeAlias = np.ndarray[tuple[int, ...], np.dtype[np.intp]]
