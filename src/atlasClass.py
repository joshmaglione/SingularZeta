#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from parseEdges import _parse_edges, _get_total_charts, _get_leaves
from interfaceSing import LoadChart as _load

class Atlas():

    def __init__(self, direc):
        self.directory = direc
        self.edges = _parse_edges(direc)
        self.number_of_charts = _get_total_charts(self.edges)
        self.leaves = _get_leaves(self.edges, self.number_of_charts)
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

