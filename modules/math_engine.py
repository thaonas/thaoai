import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

def evaluer_expression(message):
    try:
        expr = parse_expr(message.replace(" ", ""))
        resultat = sp.N(expr)
        return f"Résultat : {resultat}"
    except:
        return None