#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.rings.integer import Integer as _int



# Variables for user settings. These can be changed without affecting the 
# mathematics.
_DEFAULT_INDENT = " "*4         # String
_DEFAULT_LOAD_DB = True         # Boolean
_DEFAULT_USER_INPUT = False     # Boolean
_DEFAULT_VERBOSE = True         # Boolean


# Variables for Singular things
# Defined globally in case their format/ name changes.
_CHART_LIB = "Chart_loading.lib"
_INT_LAT_LIB = "intersectionLattice.lib"
_chart_num = lambda x: "Chart" + str(x) + ".ssi" 


# Variables for type checking in Sage
_is_int = lambda x: isinstance(x, int) or isinstance(x, _int)


# Variable for saving polynomial data
# The structure of the lookup key is given in 'rationalPoints.py'
_Lookup_Table = {}