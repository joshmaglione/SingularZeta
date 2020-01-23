#
#   Copyright 2019--2020 Joshua Maglione 
#
#   Distributed under MIT License
#

from globalVars import _DEFAULT_INDENT as _indent
from globalVars import _DEFAULT_p as _p
from globalVars import _DEFAULT_USER_INPUT as _input
from globalVars import _DEFAULT_VERBOSE as _verbose
from sage.all import AffineSpace as _affine
from sage.all import QQ as _QQ
from sage.all import Set as _set
from sage.all import var as _var
from sage.all import PolynomialRing as _polyring
from rationalPoints import _rational_points, _get_smaller_poly_ring

# Parses the list of vertices. Changes from {0, 1}-tuple to a set.
def _parse_vertices(vert_list):
    def build_subset(t):
        count = 0
        subset = []
        for i in t:
            if i == 1:
                subset.append(count)
            count += 1
        return _set(subset)

    new_verts = [map(build_subset, level) for level in vert_list]
    # Want to include the empty intersection when no focus.
    if new_verts[0] == []:
        new_verts[0] = [_set()]
    
    # Now we flatten the vertices since the size of the set determines the level
    return reduce(lambda x, y: x + y, new_verts, [])


# Parses the divisor list from Singular after passing through our expression 
# parser.
def _parse_divisors(div_list, varbs=None):
    if varbs == None:
        divs = [d.polynomial(_QQ) for d in div_list]
    else:
        P = _polyring(_QQ, varbs)
        divs = [P(d) for d in div_list]
    return divs


# Parses the set of edges from Singular. The vert_list should be the pre-parsed 
# vertices.
def _parse_edges(edge_list, vert_list, empty=True):
    vert_flat = reduce(lambda x, y: x + y, vert_list, [])
    if empty:
        vert_flat = [_set()] + vert_flat
    new_edges = []

    # Replace the edges with a list of subsets of the form {v1, v2}
    for E in edge_list:
        level = E[0]
        v1 = vert_list[level-2][E[2]-1]
        v2 = vert_list[level-1][E[1]-1]
        edge = [vert_flat.index(v1), vert_flat.index(v2)]
        new_edges.append(edge)
    if empty:
        if len(vert_list) <= 1:
            return [_set()]
        for v in vert_list[1]:
            new_edges.append([0, vert_flat.index(v)])

    return map(lambda x: _set(x), new_edges)

# Parses the list of components from Singular.
def _parse_components(comps):
    return reduce(lambda x, y: x + y, map(list, comps), [])


# Given the list of divisors and a vertex from the intersection lattice, return 
# the system of polynomials that define the corresponding ideal.
def _get_defining_ideal(divs, v):
    if len(v) == 0:
        return [0]
    polys = []
    for k in v:
        polys.append(divs[k])
    return polys


def _inc_exc(n, verts, edges, counts):
    level = {n}
    total = counts[n][0] + _var(_p)*0
    next_level = _set()
    sign = -1
    while len(level) > 0:
        for k in level:
            # First get all the edges containing vertex k
            edge_set = filter(lambda x: k in x, edges)
            # Now we put all the vertices together yielding all the neighbors
            neighbors = reduce(lambda x, y: x + y, edge_set, _set())
            # Grab the neighbors whose numbers are strictly larger
            next_neigh = filter(lambda x: x > k, neighbors)
            next_level = next_level + _set(next_neigh)
        # We add up the counts for the next neighbors
        part_tot = reduce(lambda x, y: x + y, [counts[i][0] for i in next_level], 0)
        total += sign*part_tot
        # We get ready to recurse.
        sign *= -1
        level = next_level
        next_level = _set([])
    if total == 0:
        return 0
    return total.simplify().factor()


class IntLattice():

    def __init__(self, comps, divs, edges, verts, ppts=None):
        self.bad_primes = None
        self.chart = None
        self.components = comps
        self.divisors = divs
        self.edges = edges
        self.p_points = ppts
        self.vertices = verts

        # Hidden
        self._vertexToPoints = None


    def __repr__(self):
        Nverts = len(self.vertices)
        Nedges = len(self.edges)
        return "An intersection lattice with %s vertices and %s edges." % (Nverts, Nedges)


    # Determine the p-rational points of the varieties associated to the 
    # intersection lattice. 
    def pRationalPoints(self, user_input=_input, recompute=False, verbose=_verbose):
        # Some initial checks
        if (not recompute) and (self.p_points != None):
            return self.p_points
        if self.chart == None:
            raise AttributeError('Expected a chart associated to intersection lattice.')

        if _verbose >= 2:
            print "Counting the F_p-rational points of Chart %s." % (self.chart._id)

        # Get the underlying polynomial ring (over the variables with 
        # non-normal crossings)
        P, divs, ambient = _get_smaller_poly_ring(self.divisors,  self.chart.coefficients, ambient=self.chart.ambientFactor)

        # Now we get the number of p-rational points. 
        rat_pts = []
        for i in range(len(self.vertices)):
            lab = str(self.chart._id) + '_' + str(i)
            polys = _get_defining_ideal(divs, self.vertices[i])
            if _verbose >= 2:
                print _indent + "Counting points on vertex %s." % (self.vertices[i])
            system = polys
            if not 0 in ambient:
                if polys == [0]:
                    system = ambient
                else:
                    system += ambient
            rat_pt_dat = _rational_points(P, system, user_input=user_input, label=lab)
            rat_pts.append(rat_pt_dat) # Want it to be flattened

        self.p_points = rat_pts

        # Build a function from the set of vertices to the intersection counts.
        n = len(self.vertices)
        int_count = [_inc_exc(k, self.vertices, self.edges, rat_pts) for k in range(n)]
        self._vertexToPoints = int_count
        return rat_pts


# There are a lot of redundancies in the intersection lattices. We remove them.
def _remove_redundancies(comps, divs, edges, verts, focus=None, verbose=_verbose):
    div_num = len(divs)
    # First we define functions to do the work for us.
    # The first function checks if the polynomial d is a monomial.
    is_mono = lambda d: not ("+" in str(d) or "-" in str(d))

    # Check if the polynomials f and g have any variables in common. 
    def common_var(f, g):
        f_vars = map(str, list(f.variables()))
        g_vars = map(str, list(g.variables()))
        for x in f_vars:
            if x in g_vars:
                return True
        return False

    # A wrapper for common_var. Given an index of one of the divisors, we check 
    # that particular divisor against all the other divisors. 
    check_div = lambda D, i: map(lambda x: common_var(x, D[i]), D[:i] + D[i+1:])

    # We do not want to get rid of any divisors that are in the focus.
    def not_foc(i):
        if focus != None and not divs[i] in focus:
            return True

    # We check that D is monomial and that all the variables in D are disjoint 
    # from all the variables in all other divisors. 
    can_remove = lambda i: is_mono(divs[i]) and not any(check_div(divs, i)) and not_foc(i)

    # Run through all the divisors, checking if we can remove any
    to_remove = map(can_remove, range(div_num))

    # We set all the labels that we will remove to -1, while cleaning the divs
    clean_divs = []
    mark = [-1]*div_num
    for i in range(div_num):
        if not to_remove[i]:
            mark[i] = len(clean_divs)
            clean_divs.append(divs[i])

    # Maps a vertex {a, b, ...} to {mark[a], mark[b], ...}
    marked_verts = map(lambda v: _set(map(lambda i: mark[i], v)), verts)

    # Decides if -1 is in the vertex, and if so, returns True
    verts_to_remove = map(lambda x: -1 in x, marked_verts)

    vert_comp = zip(marked_verts, comps)
    # Clean vertices and comps by removing all subsets with -1
    cleaned_vert_comp = filter(lambda x: not -1 in x[0], vert_comp)
    clean_verts, clean_comps = tuple(zip(*cleaned_vert_comp))

    # Given an edge that should not be removed, we relabel it.
    def relabel_edge(e):
        e_vert = map(lambda x: verts[x], e)
        e_new_vert = map(lambda v: _set(map(lambda i: mark[i], v)), e_vert)
        f = _set(map(lambda x: clean_verts.index(x), e_new_vert))
        return f

    # Function to mark the edges. If it should be removed, then the subset {-1} 
    # is returned; otherwise the edge is relabeled with the new vertices.
    def edge_marker(e):
        if any(verts_to_remove[v] for v in e):
            return {-1}
        else:
            return relabel_edge(e)

    marked_edges = map(edge_marker, edges)
    clean_edges = filter(lambda x: len(x) != 1, marked_edges)

    return IntLattice(clean_comps, clean_divs, clean_edges, clean_verts)


# In the latest version, we need to include the focus in the intersection 
# lattice. 
def _include_focus(comps, divs, edges, verts, focus=None):
    if focus == None or focus == (0,):
        return IntLattice(comps, divs, edges, verts)
    else:
        # don't want repeats
        new_foci_divs = filter(lambda f: not f in divs, focus) 
        make_poly = lambda f: f.polynomial(_QQ) # Sage issues...
        newdivs = divs + list(map(make_poly, new_foci_divs))
        S = _set(range(len(divs), len(newdivs)))
        union = lambda X: X.union(S)
        newverts = map(union, verts)
        return IntLattice(comps, newdivs, edges, newverts)


# A wrapper for IntLattice for charts. It will digest certain data differently.
def _parse_lattice_data(comps, divs, edges, verts, focus=None, sanity=True,  ver=2, variables=None):
    has_empty = lambda X: bool(_set() in X)
    # Parse the data individually
    newComps = _parse_components(comps)
    newDivs = _parse_divisors(divs, varbs=variables)
    newVerts = _parse_vertices(verts)
    newEdges = _parse_edges(edges, verts, empty=has_empty(newVerts))

    if sanity:
        for i in range(len(newVerts)):
            u = newVerts[i]
            for j in range(i+1, len(newVerts)):
                v = newVerts[j]
                if len(u) + 1 == len(v):
                    # Check that the two statements are logically equivalent.
                    assert bool(_set([i, j]) in newEdges) == bool(u.issubset(v))
        if _verbose >= 2:
            print "Passed sanity check 1."

    if ver <= 1:
        I = _remove_redundancies(newComps, newDivs, newEdges, newVerts, focus=focus)

        if sanity:
            embedding = lambda f: newDivs.index(f)
            for i in range(len(I.vertices)):
                u = I.vertices[i]
                old_u = _set(map(lambda x: embedding(I.divisors[x]), list(u)))
                # Check that there is a corresponding vertex.
                assert old_u in newVerts
                for j in range(i+1, len(I.vertices)):
                    v = I.vertices[j]
                    if len(u) + 1 == len(v):
                        # Check two statements are logically equivalent.
                        assert bool(_set([i, j]) in I.edges) == bool(u.issubset(v))
            if _verbose >= 2:
                print "Passed sanity check 2."
    else:
        I = _include_focus(newComps, newDivs, newEdges, newVerts, focus=focus)

    return I