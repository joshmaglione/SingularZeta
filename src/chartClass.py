#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from parseSingularExpr import _expr_to_terms
from sage.all import expand as _expand

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


    def IsMonomial(self):
        polys_str = [[str(_expand(t)) for t in f] for f in self.cone]
        polys = reduce(lambda x, y: x + y, polys_str, [])
        for f in polys:
            terms = _expr_to_terms(f)
            if len(terms) > 1:
                return False
        return True