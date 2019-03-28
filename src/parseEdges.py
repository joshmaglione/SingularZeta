#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#


# Given a directory, search for the 'Edges' file, and return a list of pairs 
# corresponding to the edges of the blow-up tree.
def parse_edges(direc):
    if direc[-1] != "/": 
        edge_file = direc + "/Edges"
    else:
        edge_file = direc + "Edges"
    return edge_file