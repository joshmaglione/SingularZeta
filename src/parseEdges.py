#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import Set as _set

# Given a directory, search for the 'Edges' file, and return a list of pairs 
# corresponding to the edges of the blow-up tree.
def _parse_edges(direc):
    if direc[-1] != "/": 
        edge_file = direc + "/Edges"
    else:
        edge_file = direc + "Edges"
    with open(edge_file) as EF:
        edges_raw = EF.read()
    edges_separated = edges_raw.replace(";", "").replace("}", "").split("\n")
    edges = []
    for e in edges_separated:
        if e != "" and "--" in e:
            a, b = e.split("--")
            edges.append(tuple([int(a), int(b)]))
    return edges

# Assume we get the output from _parse_edges: a list of tuples of ints.
def _get_total_charts(edges):
    vertices = _set(e[1] for e in edges)
    # The initial vertex is a source, so we add 1
    return len(vertices) + 1

# Assume we get the output from _parse_edges and the number of vertices.
def _get_leaves(edges, n):
    is_leaf = [1 for i in range(n)]
    for e in edges:
        is_leaf[e[0] - 1] = 0
    return tuple([k + 1 for k in range(n) if is_leaf[k]])