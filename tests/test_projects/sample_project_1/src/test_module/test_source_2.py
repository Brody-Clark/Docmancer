import math
from typing import List, Union


def factorial(n: int) -> int:

    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


class Calculator:

    def __init__(self, initial_value: float = 0.0):
        self.value = initial_value

    @staticmethod
    def subtract_static(x: float, y: float) -> float:

        return x - y
