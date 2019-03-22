#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import var as _var

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


def _str_to_vars(factor):
    try:
        f = int(factor)
    except ValueError: # if factor is not an int, we receive ValErr.
        if not "gen(" in factor:
            return _var(factor.replace("(", "").replace(")", ""))
    return 1



def _expr_to_tup(exp):
    # Separate the expression into terms, then each term into factors. 
    terms = _expr_to_terms(exp)
    fact_terms = [_term_to_factors(term) for term in terms]

    # This isn't the most efficient algorithm, but hopefully it's clear.
    # We parse the data into sage values and variables. 
    mult = lambda x, y: x*y
    n = max(_get_row_num(fact) for fact in fact_terms)
    t = [0 for i in range(n)]
    for fact in fact_terms:
        sage_fact = reduce(mult, (_str_to_vars(f) for f in fact), 1)
        t[_get_row_num(fact) - 1] += sage_fact
    return tuple(t)
