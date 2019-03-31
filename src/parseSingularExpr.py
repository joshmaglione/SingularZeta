#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import var as _var
from sage.all import ZZ as _ZZ

def _get_row_num(factors):
    row = 0 
    for fact in factors:
        if "gen(" in fact[0]:
            row = int(fact[0].replace("gen(", "").replace(")", ""))
    return row        


# Given a Singular term as a string (probably from _expr_to_terms), return the 
# tuple of pairs of type (str, int). Each entry corresponds to a factor of the 
# tuple, and the integer its corresponding power.
def _term_to_factors(term):
    some_factors = term.split("*")
    factors = []
    for fact in some_factors:
        if "^" in fact:
            fact_sp = fact.split("^")
            fact_tup = (fact_sp[0], int(fact_sp[1]))
            factors += [fact_tup]
        else:
            factors += [(fact, 1)]
    return tuple(factors)


# Given a Singular expression as a string, returns the tuple of strings 
# corresponding to the terms of the expression given.
# This assumes the expression is completely expanded, so each term is a monomial
def _expr_to_terms(exp):
    # Treat negative terms as -1 * the term.
    # This will quickly get us a coarse splitting up.
    some_terms = exp.replace("-", "+-1*").split("+")
    terms = []
    # Now we run through all the terms from above looking for negative terms 
    # that we missed.
    for term in some_terms:
        if len(term) > 0:
            terms += [term]
    return tuple(terms)


# Given a string of variables, we remove the chars in "()_".
def _format_var(str_vars):
    return str_vars.replace("(", "").replace(")", "").replace("_", "")


# Assumes it takes as input a pair (str, int) and it returns str^int. If the 
# string is a constant, then a constant is returned. Otherwise, string is taken 
# to be a variable. 
def _str_to_vars(factor):
    exponent = factor[1]
    s = factor[0]
    try:
        constant = _ZZ.coerce(int(s))
        return constant**exponent
    except ValueError: # if factor is not an int, we receive ValErr.
        if not "gen(" in s:
            varb = _var(_format_var(s))
            return varb**exponent
    return 1


def _expr_to_tup(exp):
    # Separate the expression into terms, then each term into factors. 
    terms = _expr_to_terms(exp)
    fact_terms = [_term_to_factors(term) for term in terms]

    # This isn't the most efficient algorithm, but hopefully it's clear.
    # We parse the data into sage values and variables. 
    _mult = lambda x, y: x*y
    n = max(_get_row_num(fact) for fact in fact_terms)
    # It is possible that n == 0, in such a case, we have a single polynomial.
    if n == 0:
        t = 0
    else:
        t = [0 for i in range(n)]

    for fact in fact_terms:
        vars_and_consts = [_str_to_vars(f) for f in fact] # important: keep list
        sage_fact = reduce(_mult, vars_and_consts, 1)
        if n == 0:
            t += sage_fact
        else:
            t[_get_row_num(fact) - 1] += sage_fact
        
    if n == 0:
        return t
    else:
        return tuple(t)


# Given a product of polynomials, return something...
def _get_factors(term):
    return term # Comeback!