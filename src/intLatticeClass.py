#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

def _parse_vertices(vert_list):
    return vert_list




class IntLattice():

    def __init__(self, comps, divs, edges, verts):
        self.components = comps
        self.divisors = divs
        self.edges = edges
        self.vertices = verts

    def __repr__(self):
        return "An intersection lattice."



def _parse_lattice_data(comps, divs, edges, verts):
    # Parse the data individually
    newComps = comps
    newDivs = divs
    newEdges = edges
    newVerts = verts

    return IntLattice(newComps, newDivs, newEdges, newVerts)