#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import QQ as _QQ
from sage.all import Set as _set
from rationalPoints import _rational_points

# Parses the list of vertices. Changes from {0, 1}-tuple to a set.
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


# Parses the divisor list from singular after passing through our expression 
# parser.
def _parse_divisors(div_list):
    divs = [d.polynomial(_QQ) for d in div_list]
    return divs


# Given the list of divisors and a vertex from the intersection lattice, return 
# the system of polynomials that define the corresponding ideal.
def _get_defining_ideal(divs, v):
    if len(v) == 0:
        return [0]
    polys = []
    for k in v:
        polys.append(divs[k-1])
    return polys


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

    def RationalPoints(self, user_input=False, recompute=False):
        if (not recompute) and (self.p_points != None):
            return self.p_points
        if self.chart == None:
            raise AttributeError('Expected a chart associated to intersection lattice.')
        A = self.chart.AmbientSpace()
        rat_pts = []
        for i in range(len(self.vertices)):
            row = []
            for j in range(len(self.vertices[i])):
                lab = str(self.chart._id) + '_' + str(i) + '_' + str(j)
                polys = _get_defining_ideal(self.divisors, self.vertices[i][j])
                rat_pt_dat = _rational_points(A, polys, user_input=user_input, label=lab)
                row.append(rat_pt_dat)
            rat_pts.append(row)
        self.p_points = rat_pts
        return rat_pts


# A wrapper for IntLattice for charts. It will digest certain data differently.
def _parse_lattice_data(comps, divs, edges, verts):
    # Parse the data individually
    newComps = comps
    newDivs = _parse_divisors(divs)
    newEdges = edges
    newVerts = _parse_vertices(verts)

    return IntLattice(newComps, newDivs, newEdges, newVerts)