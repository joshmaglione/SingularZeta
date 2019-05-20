#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from integrandClass import MapIntegrand as _get_integrand
from parseSingularExpr import _expr_to_terms
from polynomialManipulation import _construct_subchart
from sage.all import expand as _expand
from sage.all import factor as _factor
from sage.all import Ideal as _ideal
from sage.all import PolynomialRing as _polyring
from sage.all import Set as _set
from sage.all import var as _var
from util import _my_odom


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
        self.subcharts = None

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
        if not recompute and self.subcharts != None:
            return self.subcharts
        verts = [v for level in range(self.intLat.vertices) for v in level]
        charts = tuple([_construct_subchart(self, v) for v in verts])
        self.subcharts = charts
        return charts
        
