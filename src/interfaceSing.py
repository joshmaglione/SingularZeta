#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import singular as _SING
from globalVars import _is_int, _CHART_LIB, _chart_num
from ringClass import Ring as _ring
from parseSingular import _parse_printout


def LoadChart(num, direc):
    # We check that the input is the correct type.
    if not _is_int(num):
        raise TypeError("First argument must be an integer.")
    if not isinstance(direc, str): 
        raise TypeError("Second argument must be a string.")

    # We need to grab the parent directory.
    # If a value error is raised, then we are in the parent dir. 
    try:
        index = direc.rindex('/')
        pdir = direc[:index+1]
    except ValueError:
        pdir = './'

    # Singular code to run.
    str_load_lib = 'LIB "' + pdir + _CHART_LIB + '";'
    str_load_char = 'def S = load_Chart(' + str(num) + ',"' + direc + '");'
    str_set_ring = 'setring S;'

    # Print statements for the user. Maybe we'll turn these off soon?
    print "Loading Singular library: \n    %s" % (pdir + _CHART_LIB)
    print "Loading Chart: \n    %s" % (direc + _chart_num(num))
    print "\nRunning the following Singular code:"
    print "> " + str_load_lib
    print "> " + str_load_char
    print "> " + str_set_ring

    # In Sage, the Singular run is continous, so we can make multiple calls to  
    # the same variables for example. 
    _SING.lib(pdir + _CHART_LIB)
    _ = _SING.eval(str_load_char + "\n" + str_set_ring)

    # First we get the basics: coeff ring and vars.
    sing_ring_printout = _SING.eval("S;")
    coeff, varbs = _parse_printout(sing_ring_printout)

    # Now we construct our ring to keep all of this data in one place.
    R = _ring(coeff, varbs)

    return R