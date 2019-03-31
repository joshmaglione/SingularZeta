#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from parseSingularExpr import _expr_to_terms
from sage.all import expand as _expand
from sage.all import factor as _factor

# Given a string representing a fully expanded polynomial, decides if it 
# represents a monomial or not.
def _is_monomial(poly):
    terms = _expr_to_terms(poly)
    if len(terms) > 1:
        return False
    return True

# Given a string representing a factored polynomial, return the root of each of 
# its factors. For example, 'x*y' would return {'x': [0], 'y' : [0]} while 'x*
# (y-1)*(y+1)' would return {'x': [0], 'y': [-1, 1]}.
def _find_roots(poly):
    factors = poly.split("*")


class Chart():

    def __init__(self, R, X,
        biratMap = None,
        cent = None,
        cone = None,
        exDivs = None,
        jacDet = None,
        lastMap = None,
        path = None): 

        self.coefficients = R
        self.variables = X
        self.birationalMap = biratMap
        self.cent = cent
        self.cone = cone
        self.exDivisors = exDivs
        self.jacDet = jacDet
        self.lastMap = lastMap
        self.path = path


    def __repr__(self):
        cat_strings = lambda x, y: x + " " + str(y)

        str_coeffs = "coefficients: %s\n" % self.coefficients
        str_num_vars = "number of vars: %s\n" % len(self.variables)
        str_b1_ord = "    block 1: ordering dp\n"
        str_names = "      names:" + reduce(cat_strings, self.variables, "")
        str_b2_ord = "\n    block 2: ordering C"
        
        return str_coeffs + str_num_vars + str_b1_ord + str_names + str_b2_ord


    # Decides if the cone data is monomial.
    def IsMonomial(self):
        polys_str = [[str(_expand(t)) for t in f] for f in self.cone]
        polys = reduce(lambda x, y: x + y, polys_str, [])
        return all(map(_is_monomial, polys))


    # Decides if the cone data is quasi-monomial, i.e. under an affine 
    # traslation the cone data is equivalent to monomial cone data.
    def IsQuasiMonomial(self):
        # Not the most efficient, but this shouldn't be expensive.
        if self.IsMonomial():
            return True, [[0] for X in self.variables]

        # Not monomial, so find out where the data is not monomial.
        polys_str = [[str(_factor(t)) for t in f] for f in self.cone]
        polys = reduce(lambda x, y: x + y, polys_str, [])
        translation = [[] for X in self.variables]
        for f in polys:
            if not _is_monomial(f):

        return polys