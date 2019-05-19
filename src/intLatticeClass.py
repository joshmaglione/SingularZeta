#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import QQ as _QQ
from sage.all import Set as _set
from rationalPoints import *

def _parse_vertices(vert_list):
    def build_subset(t):
        n = len(t)
        count = 1
        subset = []
        for i in t:
            if i == 1:
                subset.append(count)
            count += 1
        return _set(subset)

    return [map(build_subset, level) for level in vert_list]


def _parse_divisors(div_list):
    divs = [d.polynomial(_QQ) for d in div_list]
    return divs


class IntLattice():

    def __init__(self, comps, divs, edges, verts, ppts=None):
        self.bad_primes = None
        self.chart = None
        self.components = comps
        self.divisors = divs
        self.edges = edges
        self.p_points = ppts
        self.vertices = verts

    def __repr__(self):
        add_up = lambda x, y: x + y 
        Nverts = reduce(add_up, map(len, self.vertices))
        Nedges = reduce(add_up, map(len, self.edges))
        return "An intersection lattice with %s vertices and %s edges." % (Nverts, Nedges)

    def RationalPoints(self):
        if p_points != None:
            return self.p_points
        if self.chart == None:
            raise AttributeError('Expected a chart associated to intersection lattice.')
        A = self.chart.AmbientSpace()


# A wrapper for IntLattice for charts. It will digest certain data differently.
def _parse_lattice_data(comps, divs, edges, verts):
    # Parse the data individually
    newComps = comps
    newDivs = _parse_divisors(divs)
    newEdges = edges
    newVerts = _parse_vertices(verts)

    return IntLattice(newComps, newDivs, newEdges, newVerts)