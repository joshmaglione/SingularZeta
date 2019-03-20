#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

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
    # This will quickly get us a coarse splitting up.
    some_terms = exp.split("+")
    terms = []
    # Now we run through all the terms from above looking for negative terms 
    # that we missed.
    for term in some_terms:
        while "-" in term[1:]:
            ind = term.index("-")
            if ind > 0:
                terms += [term[:ind]]
            # Keep the negative, so start at ind.
            terms = term[ind:] 
        if len(term) > 0:
            terms += [term]
    return tuple(terms)