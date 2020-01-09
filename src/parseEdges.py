#
#   Copyright 2019--2020 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import Set as _set

# Given a directory, search for the 'Edges' file, and return a list of pairs 
# corresponding to the edges of the blow-up tree.
def _parse_edges(direc, version=1):
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
            edges.append([int(a), int(b)])
            
    # Per Anne's change (18-12-2019), there is another level to consider.
    if version != 1:
        from os import listdir
        other_files = filter(lambda x: "Edges_" in x, listdir(direc))
        vertices = map(lambda x: int(x[6:]), other_files)
        for i in range(len(edges)):
            if edges[i][1] in vertices:
                edges[i] = [edges[i][0], [edges[i][1], 1]]
        for v in vertices:
            with open(edge_file + "_" + str(v)) as NEF:
                new_edges_raw = NEF.read()
            new_edges_sep = new_edges_raw.replace(";", "").replace("}", "").split("\n")
            for e in new_edges_sep:
                if "--" in e:
                    c, d = e.split("--")
                    edges.append([[v, int(c)], [v, int(d)]])
    return map(lambda e: tuple(e), edges)

# Assume we get the output from _parse_edges: a list of tuples of ints or lists.
def _get_vertex_labels(edges):
    S = _set([e[1] for e in edges])
    return list(_set([1]).union(S))

# Assume we get the output from _parse_edges: a list of tuples of ints or lists.
def _get_total_charts(edges):
    return len(_get_vertex_labels(edges))

# Assume we get the output from _parse_edges and the number of vertices.
def _get_leaves(edges):
    verts = _get_vertex_labels(edges)
    n = len(verts)
    is_leaf = [1 for _ in verts]
    for e in edges:
        is_leaf[verts.index(e[0])] = 0
    return tuple([verts[k] for k in range(n) if is_leaf[k]])
