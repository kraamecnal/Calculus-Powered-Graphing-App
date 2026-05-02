from sympy import sympify, lambdify, integrate
from sympy.abc import x
from core.formatting import format_expression
import scipy.integrate as integral
import numpy as np

def integration(function_str, lower_limit=None, upper_limit=None, evaluate=False):
    sympified = sympify(function_str)

    if not evaluate:
        return format_expression(integrate(sympified))     # returns anti-derivative (indefinite integral)
    
    integral_callable = lambdify(x, sympified, "numpy")
    result = integral.quad(integral_callable, lower_limit, upper_limit)
    return result[0]    # returns the value from the definite integral


def area_between_curves(func1_str, func2_str, lower_limit, upper_limit):
    """
    Calculate the area between two curves f1(x) and f2(x) over [a, b].
    
    Args:
        func1_str: String representation of first function
        func2_str: String representation of second function
        lower_limit: Lower bound (a)
        upper_limit: Upper bound (b)
    
    Returns:
        The absolute area between the two curves
    """
    sym1 = sympify(func1_str)
    sym2 = sympify(func2_str)
    
    # Calculate the absolute difference
    difference = sym1 - sym2
    
    # Create callable function for the absolute difference
    diff_callable = lambdify(x, difference, "numpy")
    
    # Numerical integration of the absolute difference
    def abs_diff(x_val):
        return np.abs(diff_callable(x_val))
    
    result = integral.quad(abs_diff, lower_limit, upper_limit)
    return result[0]


def get_area_between_curves_function(func1_str, func2_str):
    """
    Returns information about the area between two curves for visualization.
    
    Args:
        func1_str: String representation of first function
        func2_str: String representation of second function
    
    Returns:
        Tuple of (f1_callable, f2_callable, sym1, sym2)
    """
    sym1 = sympify(func1_str)
    sym2 = sympify(func2_str)
    
    f1_callable = lambdify(x, sym1, "numpy")
    f2_callable = lambdify(x, sym2, "numpy")
    
    return f1_callable, f2_callable, sym1, sym2