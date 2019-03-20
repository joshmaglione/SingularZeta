#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#


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


# COMEBACK HERE
def _expr_to_tup(exp):
    terms = _expr_to_terms(exp)
    fact_terms = [_term_to_factors(term) for term in terms]
    n = max(_get_row_num(fact) for fact in fact_terms)
    return n
