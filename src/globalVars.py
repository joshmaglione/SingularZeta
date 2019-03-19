#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.rings.integer import Integer as _int

_CHART_LIB = "Chart_loading.lib"
_is_int = lambda x: isinstance(x, int) or isinstance(x, _int)
_chart_num = lambda x: "Chart" + str(x) + ".ssi"