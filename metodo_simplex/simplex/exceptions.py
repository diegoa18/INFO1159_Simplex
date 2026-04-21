from __future__ import annotations

# exception -> LPerror -> los demas


class LPError(Exception):
    pass


class InvalidLPError(LPError):
    pass


class UnboundedError(LPError):
    pass


class InfeasibleError(LPError):  # infactible
    pass


class StabilityError(LPError):  # estabilidad, como: algo > MAX_ITERATIONS, eso
    pass


class TableauError(LPError):
    pass


class PivotError(LPError):  # para errores en el pivoteo
    pass
