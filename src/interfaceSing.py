#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import singular as _SING
from sage.all import randint as _RAND
from globalVars import _is_int, _CHART_LIB, _chart_num
from ringClass import Ring as _ring
from parseSingularBasics import _parse_printout

# Randomly generates an unused variable name in Singular.
def _get_safe_var():
    unsafe = True
    while unsafe:
        rand_chars = (chr(_RAND(97, 122)) for i in range(_RAND(4, 16)))
        cat_chars = lambda x, y: x + y
        r_var = reduce(cat_chars, rand_chars, "")
        # We will get an error if the is *not* defined.
        try:
            _ = _SING.eval(r_var + ";")
        except:
            unsafe = False
    return r_var


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

    # We need to find a safe variable name for our Singular run.
    r_var = _get_safe_var()

    # Singular code to run.
    str_load_lib = 'LIB "' + pdir + _CHART_LIB + '";'
    str_load_char = 'def %s = load_Chart(%s, "%s");' % (r_var, num, direc)
    str_set_ring = 'setring %s;' % (r_var)

    # Print statements for the user. Maybe we'll turn these off soon?
    print "Loading Singular library: \n    %s" % (pdir + _CHART_LIB)
    print "Loading Chart: \n    %s" % (direc + _chart_num(num))
    print "\nRunning the following Singular code:"
    print "> " + str_load_lib
    print "> " + str_load_char
    print "> " + str_set_ring

    # In Sage, the Singular run is continous, so we can make multiple calls to  
    # the same variables for example. 
    # Currently, no error checking here. 
    _SING.lib(pdir + _CHART_LIB)
    _ = _SING.eval(str_load_char + "\n" + str_set_ring)

    # First we get the basics: coeff ring and vars.
    sing_ring_printout = _SING.eval(r_var + ";")
    coeff, varbs = _parse_printout(sing_ring_printout)

    # Now we construct our ring to keep all of this data in one place.
    R = _ring(coeff, varbs)

    # Clean up the Singular run
    _ = _SING.eval("kill %s;" % (r_var))

    return R