#
#   Copyright 2019--2020 Joshua Maglione 
#
#   Distributed under MIT License
#

from globalVars import _is_int
from globalVars import _DEFAULT_p as _p
from globalVars import _DEFAULT_t as _t
from globalVars import _DEFAULT_INDENT as _indent
from parseSingularExpr import _term_to_factors, _str_to_vars
from sage.all import factor as _factor
from sage.all import var as _var

# A function to printout the integral needed to solve, given a chart.
def _integral_printout(chart, integrand=None):
    if integrand == None:
        integrand = chart.Integrand()
    print("The corresponding integral:\n%s" % (integrand))
    print("where S is the set of all %s satisfying:" % (list(chart.variables)))
    to_ineq = lambda x: "%s%s | %s\n" % (_indent, x[0], x[1])
    print(reduce(lambda x, y: x + y, map(to_ineq, chart.cone), ""))


# Given two tuples of variables, return the map from one tuple to the other.
def _get_birat_map(vars1, vars2):
    strings = [str(x) for x in vars1]
    bi_dict = {strings[k] : vars2[k] for k in range(len(vars2))}
    return lambda x: bi_dict[str(x)]


# Given a list of terms, as string, check if any are negative, and if so, 
# remove it.
def _remove_negative(list_of_terms):
    new_terms = []
    for term in list_of_terms:
        if term[0] == "-":
            new_terms.append(term[1:])
        else:
            new_terms.append(term)
    return new_terms
    

# Given a list of (old) variables, a birational map, an (old) integrand, and a 
# jacobian, return the updated integrand with the birational map and jacobian.
def _get_integrand(varbs, biratMap, integrand, jacDet, integralFactor):
    # Build the actual birational map
    birat_map = _get_birat_map(varbs, biratMap)
    init_integrand = integrand
    map_it = lambda x: [birat_map(x[0]), x[1]]

    # Map the initial integrand to the current with the birational map
    int_mapped = map(map_it, init_integrand) 

    # Multiply by the Jacobian
    if str(jacDet) != "1":
        int_jac = [[jacDet, (1, 0)]]
    else:
        int_jac = []

    factor = integrand.factor + [[integralFactor, [1, 0]]]

    return Integrand(int_mapped + int_jac, factor=factor)


# Given an atlas and a chart, modify the integrand for the chart according to 
# the data. This is a wrapper, using the atlas and chart classes, for 
# _get_integrand
def MapIntegrand(atlas, chart):
    if chart.atlas == None:
        raise ValueError("Expected the chart to come from an atlas.")
    if atlas.directory != chart.atlas.directory:
        raise ValueError("Expected the chart to be contained in the given atlas.")
    return _get_integrand(atlas.root.variables, chart.birationalMap, 
        atlas.integrand, chart.jacDet, chart._integralFactor)


# Given a list of factors corresponding to the integrand, return a list of the 
# same form but factored and simplified.
def _clean_integrand(integrand):
    # First we make sure everything is factored as much as possible.
    cleaned_int = []
    for int_fact in integrand:
        # Cannot use 'factor_list' for integers, so we treat them separately
        if _is_int(int_fact[0]):
            if not int_fact[0] in {-1, 1}:
                cleaned_int.append(int_fact)
        else:
            fact_list = int_fact[0].factor_list()
            for f in fact_list:
                vec = int_fact[1]
                scl_vec = [f[1]*u for u in vec]
                cleaned_int.append([f[0], scl_vec])

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
        

# Given a list corresponding to an integrand, return the tuple of p-powers 
# (after evaluting the p-adic absolute value) and the int_list without the 
# p-powers.
def _remove_p_powers(int_list):
    is_p = lambda x: str(x[0]) == _p
    not_p = lambda x: not is_p(x)
    p_part = list(filter(is_p, int_list))
    if len(p_part) != 0:
        p_part = [[p_part[0][0], [-a for a in p_part[0][1]]]]
    else:
        p_part = [[_var(_p), [0, 0]]]
    return p_part, list(filter(not_p, int_list))
    


# Integrand class. 
# There is one major attribute: 'list'.
# This should be given as a list of lists of the form [f(X), (a, b)], where f(X)
# is a polynomial in the variables X and (a, b) is a tuple of integers. This 
# will correspond to the factor |f(X)|^{b*s + a} in the integral.
class Integrand():

    def __init__(self, data_list, factor=[]):
        # First we make sure to clean the data up
        data = _clean_integrand(data_list)
        # Now we split off the p-powers
        p_powers, cleaned_list = _remove_p_powers(data)
        
        self.list = cleaned_list
        self.terms = [T[0] for T in self.list]
        self.factor = _clean_integrand(factor + p_powers)

        # 'Hidden' attribute
        self._term_dict = {str(T[0]): T[1] for T in self.list} 


    def __repr__(self):
        # Our integral sign
        int_sign = lambda x, y: '%s   _\n%s  | `\n%s ._|  ' % (' '*x, ' '*x, y)
        # Mapping functions
        def fact_to_str(fact):
            s = _var('s')
            out = "|%s|^(%s)*" % (fact[0], fact[1][1]*s + fact[1][0])
            return out
        def out_to_str(fact):
            s = _var('s')
            expr = str(fact[0])
            if '-' in expr or '+' in expr or '*' in expr or '/' in expr:
                out = "(%s)^(%s)*" % (fact[0], fact[1][1]*s + fact[1][0])
            else:
                out = "%s^(%s)*" % (fact[0], fact[1][1]*s + fact[1][0])
            return out 
        # String for the integrand    
        integrand =  reduce(lambda x, y: x + fact_to_str(y), self.list, "")
        # String for the factor
        out_factor =  reduce(lambda x, y: x + out_to_str(y), self.factor, "")
        n = len(out_factor)
        # String for the differential and integrating set
        ending = " dX\n%s   S\n" % (' '*n)
        return int_sign(n, out_factor[:-1]) + integrand[:-1] + ending


    def __iter__(self):
        for x in self.list:
            yield x
    

    # Returns the factor as a function of p: the part outside the integral.
    def pFactor(self):
        # Given a list x = [expr, (a, b)], return (expr)^a*(expr)^(bs).
        # We call the first factor the "real" factor and the second factor the 
        # "complex" factor. No, it's not particularly accurate.
        def convert_to_expr(x): 
            real_factor = x[0]**(x[1][0])
            if x[1][1] != 0:
                if x[0] != _var(_p):
                    raise AssertionError("Integrand is not as expected. Contains a factor of the form %s." % (x[0]**(x[1][1]*_var('s'))))
                else:
                    complex_factor = _var(_t)**(-x[1][1])
            else:
                complex_factor = 1
            return real_factor * complex_factor
        mult = lambda x, y: x*y
        return reduce(mult, map(convert_to_expr, self.factor), 1)