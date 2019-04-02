#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from parseSingularExpr import _expr_to_terms
from sage.all import expand as _expand
from sage.all import factor as _factor
from sage.all import Set as _set
from sage.all import var as _var
from util import _my_odom


# TODO: Not quite correct. If replace is False, then we should check carefully.
# Update the information in the chart C by applying the substitution k + q*x'
def update_chart(C, x, k, replace=False):
    # Grab the useful information from C
    coeffs = C.coefficients
    varbs = list(C.variables)
    biratMap = list(C.birationalMap)
    cone = list(C.cone)
    jacDet = C.jacDet
    assert x in varbs, "Variable is not contained in the chart."
    # Check if we are doing a full replacement or not
    if replace:
        expr = 1
        varbs = tuple(varbs[:varbs.index(x)] + varbs[varbs.index(x)+1:])
    else:
        x_new = _var(str(x) + str(k))
        q = _var('q')
        expr = k + q*x_new
        varbs[varbs.index(x)] = x_new
        varbs = tuple(varbs)
    # Now adjust accordingly
    replace_x = lambda y: y.substitute({x: expr})
    biratMap = tuple(map(replace_x, biratMap))
    cone = tuple([map(replace_x, ineq) for ineq in cone])
    jacDet = replace_x(jacDet)
    return Chart(coeffs, varbs, biratMap=biratMap, cone=cone, jacDet=jacDet)



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
        self.factor = 1


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
                return False, 0, 0

        # We cannot just use empty sets because there are too many bugs.
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

        # Clean up the data
        is_nonunit = lambda x: (x != 1) and (x != -1)
        consts = _set(filter(is_nonunit, constants))
        roots_set = {str(X) : _set(roots_cone[str(X)]) for X in self.variables}

        return True, roots_set, consts


    # Returns a tuple of charts based on further case distinctions.
    def SubCharts(self):
        check, roots, consts = self.IsQuasiMonomial()
        if not check:
            print "Chart is not quasi-monomial."
            return False
        poss_vals = {}
        for x in self.variables:
            if roots[str(x)] != _set({}):
                if not roots[str(x)]:
                    poss_vals.update({str(x) : list(roots[str(x)])})

        # Now we build all the maps to all the subcharts.
        var_map = {str(X) : X for X in self.variables}
        vals_vec = [len(poss_vals[x]) for x in poss_vals.keys()]
        # for vec in _my_odom(vals_vec):
        #     for k in len(vec):
        #         if vec[k] == vals_vec[k]:
        #             # Just replace the variable
        #         else: 
        #             # Determine the value.