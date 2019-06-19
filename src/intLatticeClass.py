#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from globalVars import _DEFAULT_USER_INPUT as _input
from globalVars import _DEFAULT_VERBOSE as _verbose
from sage.all import QQ as _QQ
from sage.all import Set as _set
from rationalPoints import _rational_points

# Parses the list of vertices. Changes from {0, 1}-tuple to a set.
def _parse_vertices(vert_list):
    def build_subset(t):
        n = len(t)
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
        new_verts[0] = [{}]
    
    # Now we flatten the vertices since the size of the set determines the level
    return reduce(lambda x, y: x + y, new_verts, [])


# Parses the divisor list from Singular after passing through our expression 
# parser.
def _parse_divisors(div_list):
    divs = [d.polynomial(_QQ) for d in div_list]
    return divs


# Parses the set of edges from Singular. The vert_list should be the pre-parsed 
# vertices.
def _parse_edges(edge_list, vert_list, empty=True):
    vert_flat = reduce(lambda x, y: x + y, vert_list, [])
    if empty:
        vert_flat = [{}] + vert_flat
    new_edges = []

    # Replace the edges with a list of subsets of the form {v1, v2}
    for E in edge_list:
        level = E[0]
        v1 = vert_list[level-2][E[2]-1]
        v2 = vert_list[level-1][E[1]-1]
        edge = {vert_flat.index(v1), vert_flat.index(v2)}
        new_edges.append(edge)
    if empty:
        for v in vert_list[1]:
            new_edges.append({0, vert_flat.index(v)})

    return new_edges

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
        self.vertexToPoints = None


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

        # Construct the ambient space
        A = self.chart.AmbientSpace()

        # Now we get the number of p-rational points. 
        rat_pts = []
        for i in range(len(self.vertices)):
            row = []
            for j in range(len(self.vertices[i])):
                lab = str(self.chart._id) + '_' + str(i) + '_' + str(j)
                polys = _get_defining_ideal(self.divisors, self.vertices[i][j])
                rat_pt_dat = _rational_points(A, polys, user_input=user_input, 
                    label=lab)
                row.append(rat_pt_dat)
            rat_pts.extend(row) # Want it to be flattened
        self.p_points = rat_pts

        # Build a function from the set of vertices to the intersection counts.
        return rat_pts



# There are a lot of redundancies in the intersection lattices. We remove them.
def _remove_redundancies(comps, divs, edges, verts, focus=None):
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




# A wrapper for IntLattice for charts. It will digest certain data differently.
def _parse_lattice_data(comps, divs, edges, verts, focus=None):
    # Parse the data individually
    newComps = _parse_components(comps)
    newDivs = _parse_divisors(divs)
    newVerts = _parse_vertices(verts)
    contains_emptyset = lambda L: {} in L
    newEdges = _parse_edges(edges, verts, empty=contains_emptyset(newVerts))
    
    return _remove_redundancies(newComps, newDivs, newEdges, newVerts, focus=focus)