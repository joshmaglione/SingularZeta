#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from parseSingularExpr import _term_to_factors, _str_to_vars
from sage.all import factor as _factor

# Given two tuples of variables, return the map from one tuple to the other.
def _get_birat_map(vars1, vars2):
    strings = [str(x) for x in vars1]
    bi_dict = {strings[k] : vars2[k] for k in range(len(vars2))}
    return lambda x: bi_dict[str(x)]

# Given a list of terms, as string, check if any are negative (i.e. start with 
# a minus sign), and if so, remove it.
def _remove_negative(list_of_terms):
    new_terms = []
    for term in list_of_terms:
        if term[0] == "-":
            new_terms.append(term[1:])
        else:
            new_terms.append(term)
    return new_terms

# Given a list of factors corresponding to the integrand, return a list of the 
# same form but factored and simplified.
def _clean_integrand(integrand):
    # First we make sure everything is factored as much as possible.
    cleaned_int = []
    for fact in integrand:
        exp_str = str(_factor(fact[0])) # unfortunate naming...
        if "*" in exp_str:
            exp_str_fact = _remove_negative(exp_str.split("*"))
            for t in exp_str_fact:
                # For the moment, I am assuming all factors are monomial. 
                assert not ("-" in t or "+" in t), "Assumed terms are monomial!"
                X, expon = _term_to_factors(t)[0]
                varb = _str_to_vars([X, 1])
                cleaned_int.append([varb, (expon*fact[1][0], expon*fact[1][1])])
        else:
            cleaned_int.append(fact)

    # Now we group together like variables. 
    simplif_int = cleaned_int
    index = 0
    while index < len(simplif_int):
        X = str(simplif_int[index][0])
        index2 = index + 1
        # Search for other variables equal to X
        while index2 < len(simplif_int):
            Y = str(simplif_int[index2][0])
            # If we find one, add up their exponent vectors
            if X == Y:
                a, b = simplif_int[index][1]
                c, d = simplif_int[index2][1]
                simplif_int[index][1] = (a + c, b + d)
                del simplif_int[index2]
            else: 
                index2 += 1
        index += 1

    return simplif_int
        


# Given an atlas and a chart, modify the integrand for the chart according to 
# the data. 
def MapIntegrand(atlas, chart):
    birat_map = _get_birat_map(atlas.root.variables, chart.birationalMap)
    init_integrand = atlas.integrand
    map_it = lambda x: [birat_map(x[0]), x[1]]
    int_mapped = map(map_it, init_integrand) 
    return tuple(_clean_integrand(int_mapped))