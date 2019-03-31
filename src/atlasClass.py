#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from parseEdges import _parse_edges, _get_total_charts, _get_leaves
from interfaceSing import LoadChart as _load
from sage.all import var as _var
from sage.all import factor as _factor

def _get_integrand(varbs, LT):
    n = len(varbs)
    X = _var('X')
    f = X**2 + X - 2*n
    roots = [T[0] for T in _factor(f).roots()]
    rows = max(roots)
    choose = lambda x: (x + 1)*(x + 2)//2
    integrand = []
    if not LT:
        varbs = varbs[::-1]
    for k in range(rows):
        exponent = k - rows
        factor = [varbs[choose(k) - 1], (exponent, 1)]
        integrand.append(factor)
    if not LT:
        integrand = integrand[::-1]
    return tuple(integrand)


class Atlas():

    # Currently, we have LT until more information is given concerning the 
    # variables. 
    def __init__(self, direc, LT=True):
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
        self.root = _load(2, direc) # PLACEHOLDER (this may cause bugs)

        # Get the starting integrand.
        self.integrand = _get_integrand(self.root.variables, LT)

        # Load in all the leaves
        self.charts = tuple([_load(i, direc) for i in self.leaves])
            

    def __repr__(self):
        ring = self.charts[0].coefficients
        dim = len(self.charts[0].variables)
        first = "An atlas over %s in %s dimensions.\n" % (ring, dim)
        direct = "    Directory: %s\n" % (self.directory)
        charts = "    Number of charts: %s\n" % (self.number_of_charts)
        leaves = "    Number of leaves: %s" % (len(self.leaves))
        return first + direct + charts + leaves


    def Integrand(self):
        def fact_to_str(factor):
            s = _var('s')
            out = "|%s|^(%s)*" % (factor[0], factor[1][1]*s + factor[1][0])
            return out
        integrand =  reduce(lambda x, y: x + fact_to_str(y), self.integrand, "")
        return integrand[:-1]
