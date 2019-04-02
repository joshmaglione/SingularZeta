#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from parseSingularExpr import _expr_to_terms
from sage.all import expand as _expand
from sage.all import factor as _factor
from sage.all import Set as _set


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

        def _is_monomial(poly):
            terms = _expr_to_terms(poly)
            if len(terms) > 1:
                return False
            return True
        
        return all(map(_is_monomial, polys))


    # Decides if the cone data is quasi-monomial, i.e. under an affine 
    # traslation the cone data is equivalent to monomial cone data.
    def IsQuasiMonomial(self): # My made up name.
        flatten_list = lambda x, y: x + list(y)
        polys_cone = reduce(flatten_list, self.cone, []) 
        factor = lambda x: [f[0] for f in x.factor_list()]
        factored_cone = reduce(flatten_list, map(factor, polys_cone), [])

        # Safe for coefficients in the output of .factor_list().
        def get_vars(f):
            try: 
                varbs = f.variables()
            except AttributeError:
                varbs = ()
            return varbs

        # First check: each factor has at most 1 variable.
        for f in factored_cone:
            if len(get_vars(f)) > 1:
                return False

        roots_cone = {str(X) : [] for X in self.variables}
        constants = []
        for f in factored_cone:
            if len(get_vars(f)) == 0:
                constants.append(f)
            else:
                x = f.variables()[0]
                assert f.degree(x) == 1, "Assumed the factors would be linear."
                root_f = f.roots()[0][0]
                roots_cone[str(x)].append(root_f)
        
        # We clean up the data
        is_nonunit = lambda x: (x != 1) and (x != -1)
        consts = _set(filter(is_nonunit, constants))
        roots_set = {str(X) : _set(roots_cone[str(X)]) for X in self.variables}

        return True, roots_set, consts