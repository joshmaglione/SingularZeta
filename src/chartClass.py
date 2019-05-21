#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from integrandClass import MapIntegrand as _get_integrand
from parseSingularExpr import _expr_to_terms
from sage.all import expand as _expand
from sage.all import factor as _factor
from sage.all import Ideal as _ideal
from sage.all import PolynomialRing as _polyring
from sage.all import Set as _set
from sage.all import var as _var
from util import _my_odom


# Given a list of variables and an integer n, return an n-tuple of new, safe 
# variables.
def _safe_variables(varbs, n):
    i = 1
    letter = 'z'
    varbs_str = {str(x) for x in varbs}
    new_varbs = []
    for k in range(n):
        if not letter + str(i) in varbs_str:
            new_varbs.append(_var(letter + str(i)))
        i += 1
    return tuple(new_varbs)


# Given an expression expr, units, non_units, and replacements repl, simplify 
# the expression to be monomial in the latest variables.
def _simplify_expr(expr, units, non_units, repl):
    p = _var('p')
    f = expr.factor_list()
    # Run through all the factors of expr
    for i in range(len(f)):
        print f
        d = f[i][0]
        if d in units:
            # If the factor is a unit, replace it with 1
            f[i] = tuple([1, f[i][1]])
        else:
            # If the factor is not a unit, replace it with p*z
            if d in non_units:
                j = non_units.index(d)
                f[i] = tuple([p*repl[j], f[i][1]])
            else:
                # Maybe it's OK that the variable does not get replaced...
                print "The factor %s is not in %s nor %s" % (d, units, non_units)
                # raise AssertionError("When doing a variable substitution, expected a factor to be in the set of units or non-units. Is the intersection lattice compatible with the chart?")
    # We might need to return a polynomial instead of a factorized polynomial.
    return f

# Given the chart, units, non_units, and the replacement variables, construct a 
# new chart from C with the given data.
def _simplify(C, units, non_units, repl):
    # To be used to by 'map'
    _simp_map = lambda x: _simplify_expr(x, units, non_units, repl)

    # First we update the birational map.
    birat = tuple(map(_simp_map, C.birationalMap))

    # We update the cone.
    cone = [tuple(map(_simp_map, ineq)) for ineq in C.cone]

    # Finally we update the Jacobian.
    jacobian = _simp_map(C.jacDet)

    # Now we determine which variables are gone and which remain. 
    new_varbs_list = []
    app_to_list = lambda x: new_varbs.extend(list(x.variables()))
    _ = map(app_to_list, birat)
    _ = [tuple(map(_simp_map, ineq)) for ineq in cone]
    _ = app_to_list(jacobian)
    new_varb_set = {x for x in new_varbs_list}
    new_varbs = tuple([x for x in new_varb_set])

    sub_C = _chart(C.coefficient, new_varbs, 
        atlas = C.atlas,
        biratMap = birat,
        cent = C.cent,
        cone = cone,
        exDivs = C.exDivs,
        factor = C.factor,
        focus = C.focus,
        jacDet = jacobian, 
        lastMap = C.lastMap,
        parent = C,
        path = C.path)
    return sub_C


# Given a chart C and a vertex v, construct the (monomial) subchart of C with 
# respect to v. This comes from the intersection lattice of C. 
def _construct_subchart(C, v): 
    # Get the data
    A = C.AmbientSpace()
    divs = [A.coerce(d) for d in C.intLat.divisors]
    n = len(divs)

    # Even though these are supposed to be sets, there's something about them 
    # that makes them not act like sets. You can only use difference and union 
    # to add or subtract elements...
    units = [divs[k - 1] for k in _set(range(1, n+1)).difference(v)]
    non_units = [divs[k - 1] for k in v]

    # Determine the variables in the divs.
    varbs = {x for d in divs for x in d.variables()}
    a = min(n, len(varbs))

    # Will replace non_unit[k] with new_varb[k].
    new_varbs = _safe_variables(C.variables, a)

    # Replace non_unit[k] with p*repl[k]
    repl = [new_varbs[i] for i in range(len(non_units))]

    # Build the subchart
    sub_C = _simplify(C, units, non_units, repl)

    # We modify the subchart just slightly. 
    # We give it an id from C
    vert_to_str = lambda x, y: str(x) + y
    sub_C._id = int(str(C._id) + reduce(vert_to_str, v, ''))
    # We multiply by a factor of p
    rem = a - len(new_varbs)

    return sub_C



class Chart():

    def __init__(self, R, X,
        atlas = None,
        biratMap = None,
        cent = None,
        cone = None,
        exDivs = None,
        factor = None,
        focus = None,
        identity = None,
        intLat = None,
        jacDet = None,
        lastMap = None,
        parent = None,
        path = None): 

        self._id = identity
        self._parent = parent
        self._subcharts = None

        self.coefficients = R
        self.variables = X
        self.atlas = atlas
        self.birationalMap = biratMap
        self.cent = cent
        self.cone = cone
        self.exDivisors = exDivs
        self.factor = factor
        self.focus = focus
        self.intLat = intLat
        self.jacDet = jacDet
        self.lastMap = lastMap
        self.path = path

        if intLat != None:
            self.intLat.chart = self


    def __repr__(self):
        cat_strings = lambda x, y: x + " " + str(y)
        # Build strings
        str_coeffs = "coefficients: %s\n" % self.coefficients
        str_num_vars = "number of vars: %s\n" % len(self.variables)
        str_b1_ord = "    block 1: ordering dp\n"
        str_names = "      names:" + reduce(cat_strings, self.variables, "")
        str_b2_ord = "\n    block 2: ordering C"
        # Put everything together
        return str_coeffs + str_num_vars + str_b1_ord + str_names + str_b2_ord


    # Decides if the cone data is monomial.
    def IsMonomial(self):
        flatten = lambda x: x[0]*x[1]
        def _is_monomial(x):
            s = str(flatten(x))
            if "+" in s or "-" in s[1:]:
                return False
            return True
        return all(map(_is_monomial, self.cone))


    # Returns the ambient space as a (quotient) polynomial ring.
    def AmbientSpace(self):
        R = _polyring(self.coefficients, self.variables)
        if self.factor == 0:
            return R
        I = _ideal(R, self.factor)
        S = R.quotient(I)
        return S

    # Constructs the subcharts based on the intersection lattice.
    def Subcharts(self, recompute=False):
        if not recompute and self._subcharts != None:
            return self._subcharts
        verts = [v for level in self.intLat.vertices for v in level]
        charts = tuple([_construct_subchart(self, v) for v in verts])
        self._subcharts = charts
        return charts
        
