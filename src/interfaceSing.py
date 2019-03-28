#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import singular as _SING
from sage.all import randint as _RAND
from globalVars import _is_int, _CHART_LIB, _chart_num
from ringClass import Ring as _ring
from parseSingularBasics import _parse_printout, _parse_list

# Randomly generates an unused variable name in Singular.
def _get_safe_var():
    unsafe = True
    while unsafe:
        rand_chars = (chr(_RAND(97, 122)) for i in range(_RAND(4, 16)))
        cat_chars = lambda x, y: x + y
        r_var = reduce(cat_chars, rand_chars, "")
        # We will get an error if the variable is *not* defined.
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
    print "> " + str_set_ring + "\n"

    # A wrapper for our _parse_list function
    _parse_list_wrapped = lambda x: tuple([_parse_list(y) for y in x])
    def _exDivs_wrap(size):
        divs = []
        for i in range(size):
            entry = "print(BO[4][%s]);" % (i+1)
            data = _SING.eval(entry).replace(",", "").split("\n")
            divs += [_parse_list_wrapped(data)]
        return tuple(divs)

    # In Sage, the Singular run is continous, so we can make multiple calls to  
    # the same variables for example. 
    # Currently, no error checking here. 
    _ = _SING.lib(pdir + _CHART_LIB)
    _ = _SING.eval(str_load_char + "\n" + str_set_ring)

    # First we get the basics: coeff ring and vars.
    print "Determining the basics of the Singular data."
    sing_ring_printout = _SING.eval(r_var + ";")
    coeff, varbs = _parse_printout(sing_ring_printout)

    # Get the birational map data
    print "Obtaining the birational map."
    sing_birat_str = _SING.eval("print(BO[5]);").replace(",", "").split("\n")
    birat = _parse_list_wrapped(sing_birat_str)

    # Get the center of the blow-up
    print "Obtaining the center of the blow-up."
    sing_cent_str = _SING.eval("print(cent);").replace(",", "").split("\n")
    cent = _parse_list_wrapped(sing_cent_str)

    # Get the cone data
    print "Obtaining the cone data."
    sing_cone_printout = _SING.eval("Cone;").split("\n")
    cone = _parse_list(sing_cone_printout) # Do not want the wrapped version

    # Get the exceptional divisors
    print "Obtaining the exceptional divisor data."
    num_exc_divs = int(_SING.eval("size(BO[4]);"))
    exDivs = _exDivs_wrap(num_exc_divs)

    # Get the Jacobian determinant
    print "Obtaining the Jacobian."
    try:
        sing_jacobian_str = _SING.eval("jacDet;")
        jacDet = _parse_list(sing_jacobian_str) # Do not want wrapped version
    except:
        jacDet = 1
    
    # Get the last map
    print "Obtaining the last map data."
    try:
        sing_lm_str = _SING.eval("print(lastMap);").replace(",", "").split("\n")
        lastmap = _parse_list_wrapped(sing_lm_str)
    except:
        lastmap = None

    # Get the path
    # Waiting on a Hannover visit to learn how to read this!

    # Now we construct our ring to keep all of this data in one place.
    R = _ring(coeff, varbs, \
        biratMap=birat, 
        cent=cent, 
        cone=cone,
        exDivs=exDivs,
        jacDet=jacDet,
        lastMap=lastmap)

    # Clean up the Singular run
    _ = _SING.eval("kill %s;" % (r_var))

    return R