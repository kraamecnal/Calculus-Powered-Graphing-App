from scipy.differentiate import derivative
from sympy import sympify, diff, lambdify
from sympy.abc import x
from core.formatting import format_expression

def differentiate(function_str, x_value=None, evaluate=False, order=1):
    """
    Compute the derivative of a function.
    
    Args:
        function_str: String representation of the function
        x_value: Point at which to evaluate (if evaluate=True)
        evaluate: Whether to return numeric value or symbolic expression
        order: Order of the derivative (1, 2, 3, ...). Default is 1.
    
    Returns:
        If evaluate=False: Pretty string of the symbolic derivative
        If evaluate=True: Numeric value of the derivative at x_value
    """
    sympified = sympify(function_str)
    
    # Compute the n-th derivative symbolically
    derivative_expr = sympified
    for _ in range(order):
        derivative_expr = diff(derivative_expr)

    if not evaluate:
        return format_expression(derivative_expr)  # returns the n-th derivative
    
    df_callable = lambdify(x, derivative_expr, "numpy")
    result = derivative(df_callable, x_value) 
    return result.df    # returns value substituted from n-th derivative


def get_derivative_function(function_str, order=1):
    """
    Returns a callable function for the n-th derivative.
    
    Args:
        function_str: String representation of the function
        order: Order of the derivative (1, 2, 3, ...). Default is 1.
    
    Returns:
        A callable function that computes the n-th derivative at any x value
    """
    sympified = sympify(function_str)
    
    # Compute the n-th derivative symbolically
    derivative_expr = sympified
    for _ in range(order):
        derivative_expr = diff(derivative_expr)
    
    return lambdify(x, derivative_expr, "numpy")