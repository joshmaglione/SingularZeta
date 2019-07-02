#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from globalVars import _DEFAULT_INDENT as _indent
from globalVars import _DEFAULT_p as _p
from globalVars import _DEFAULT_USER_INPUT as _input
from globalVars import _DEFAULT_VERBOSE as _verbose
from integrandClass import Integrand as _integrand
from integrandClass import _integral_printout
from interfaceSingular import LoadChart as _load
from parseEdges import _parse_edges, _get_total_charts, _get_leaves
from sage.all import var as _var
from sage.all import factor as _factor
from sage.all import ZZ as _ZZ

# Given a list of variables and a boolean, build the root integrand.
# Note: this is only for the root of the atlas. 
def _build_integrand(varbs, LT):
    n = len(varbs)
    s = _ZZ.coerce(1 + 8*n) # In Sage 'int' does not have a sqrt method...
    if (s.sqrt())**2 != s:
        raise AssertionError("Number of variables is not an expected.")
    rows = (int(s.sqrt()) - 1)//2
    choose = lambda x: (x + 1)*(x + 2)//2
    integrand = []
    if not LT:
        varbs = varbs[::-1]
    for k in range(rows):
        exponent = k - rows
        factor = [varbs[choose(k) - 1], [exponent, 1]]
        integrand.append(factor)
    if not LT:
        integrand = integrand[::-1]
    p = _var(_p)
    return _integrand(integrand, factor=[[1 - p**(-1), [-rows, 0]]])
    

class Atlas():

    # Currently, we have LT until more information is given concerning the 
    # variables. 
    def __init__(self, direc, LT=True, verbose=_verbose):
        if verbose:
            print("Loading atlas from %s" % (direc))
            print("="*79)

        # First we "clean up" the direc string.
        if direc[-1] != "/":
            direc = direc + "/"
        self.directory = direc

        # Get the edges as a list of tuples of integers
        self.edges = _parse_edges(direc)

        # Get the integer
        self.number_of_charts = _get_total_charts(self.edges)

        # Get the leaves as a tuple of integers corresponding to the vertex 
        # number
        self.leaves = _get_leaves(self.edges, self.number_of_charts)

        # Load Chart 1 as the starting chart. 
        # BUG with the following command due to jacDet not being defined.
        # self.root = _load(1, direc)
        # self.root = _load(2, direc) # PLACEHOLDER (this may cause bugs)

        # # Get the starting integrand.
        # self.integrand = _get_integrand(self.root.variables, LT)

        # Load in all the leaves
        self.charts = tuple([_load(i, direc) for i in self.leaves])

        # TODO: Once the jacDet bug is fixed, uncomment the lines above.
        self.root = _load(1, direc, get_lat=False) # Cannot run Singular anymore

        if verbose:
            print("Successfully loaded atlas.")
            print("="*79)

        self.integrand = _build_integrand(self.root.variables, LT)
        for C in self.charts:
            C.atlas = self

        if verbose:
            print(self)
            _integral_printout(self.root, integrand=self.integrand)


    def __repr__(self):
        ring = self.charts[0].coefficients
        dim = len(self.charts[0].variables)
        # TODO: Eventually when the bug from ambient spaces is fixed, turn into 
        # lambda function.
        def chart_to_verts(x): 
            try:
                return len(x.intLat.vertices)
            except: 
                return 0
        add_up = lambda x, y: x + y 
        Nverts = reduce(add_up, map(chart_to_verts, self.charts))
        first = "An atlas over %s in %s dimensions.\n" % (ring, dim)
        direct = "%sDirectory: %s\n" % (_indent, self.directory)
        charts = "%sNumber of charts: %s\n" % (_indent, self.number_of_charts)
        leaves = "%sNumber of leaves: %s\n" % (_indent, len(self.leaves))
        integrals = "%sNumber of integrals: %s" % (_indent, Nverts)
        return first + direct + charts + leaves + integrals


    # Returns the integral on the entire lattice
    def ZetaIntegral(self, user_input=_input, verbose=_verbose):
        add_up_ints = lambda x, y: x + y.ZetaIntegral()
        # Currently we do not have the intersection lattice of a chart with an 
        # ambient space different from the standard affine space.
        AVOID_BUG = lambda x: x.intLat != None
        return reduce(add_up_ints, filter(AVOID_BUG, self.charts), 0)

