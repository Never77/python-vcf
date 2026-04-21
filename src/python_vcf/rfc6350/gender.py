from enum import Enum


class GenderType(str, Enum):
    M = "M"  # Male
    F = "F"  # Female
    O = "O"  # Other  # noqa: E741
    N = "N"  # None/Not applicable
    U = "U"  # Unknown
