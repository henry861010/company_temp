import math

def f_eq(a: float, b: float, tolerance: float = 0.0001):
    return abs(a - b) <= tolerance

def f_ne(a: float, b: float, tolerance: float = 0.0001):
    return abs(a - b) > tolerance

def f_gt(a: float, b: float, tolerance: float = 0.0001):
    return abs(a - b) > tolerance or a > b

def f_ge(a: float, b: float, tolerance: float = 0.0001):
    return abs(a - b) <= tolerance or a > b

def f_lt(a: float, b: float, tolerance: float = 0.0001):
    return abs(a - b) > tolerance or a < b

def f_le(a: float, b: float, tolerance: float = 0.0001):
    return abs(a - b) <= tolerance or a < b

def f_isInt(a: float, tolerance: float = 0.0001):
    return isinstance(a, (int, float)) and math.isclose(a, round(a), abs_tol=tolerance)