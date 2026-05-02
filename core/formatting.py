import re


def format_expression(expr) -> str:
    """Convert a SymPy expression into a cleaner plain-text form.

    This keeps powers as ^ and removes explicit multiplication signs.
    Example: 2*x**2 + x - 10 -> 2x^2+x-10
    """
    text = str(expr)
    text = text.replace("**", "^")
    text = text.replace("*", "")
    text = re.sub(r"\s+", "", text)
    return text
