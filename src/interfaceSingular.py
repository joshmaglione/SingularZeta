#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import singular as _SING
from sage.all import randint as _RAND
from sage.all import factor as _factor
from globalVars import _is_int, _CHART_LIB, _INT_LAT_LIB, _chart_num
from globalVars import _DEFAULT_INDENT as _indent
from globalVars import _DEFAULT_VERBOSE as _verbose
from chartClass import Chart as _chart
from parseSingularBasics import _parse_printout, _parse_list
from intLatticeClass import _parse_lattice_data

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


def LoadChart(num, direc, atlas=None, verbose=_verbose, get_lat=True):
    # We check that the input is the correct type.
    if not _is_int(num):
        raise TypeError("First argument must be an integer.")
    if not isinstance(direc, str): 
        raise TypeError("Second argument must be a string.")

    # We need to grab the parent directory.
    # If a value error is raised, then we are in the parent dir. 
    if direc[-1] == "/":
        direc = direc[:-1]
    try:
        index = direc.rindex('/')
        pdir = direc[:index+1]
    except ValueError:
        pdir = './'

    # We need to find a safe variable name for our Singular run.
    r_var = _get_safe_var()

    # Singular code to run.
    str_load_lib1 = 'LIB "' + pdir + _CHART_LIB + '";'
    str_load_lib2 = 'LIB "' + pdir + 'LIB/primdec.lib";'
    str_load_lib3 = 'LIB "' + pdir + _INT_LAT_LIB + '";'
    str_load_char = 'def %s = load_Chart(%s, "%s");' % (r_var, num, direc)
    str_set_ring = 'setring %s;' % (r_var)

    # Print statements for the user.
    if verbose:
        print "Loading Singular library: \n%s%s" % (_indent, pdir + _CHART_LIB)
        print "Loading Singular library: \n%s%s" % (_indent, pdir + 'LIB/primdec.lib')
        print "Loading Singular library: \n%s%s" % (_indent, pdir + _INT_LAT_LIB)
        print "Loading Chart: \n%s%s" % (_indent, direc + _chart_num(num))
        print "\nRunning the following Singular code:"
        for lib_str in (str_load_lib1, str_load_lib2, str_load_lib3):
            print "> " + lib_str
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

    # In Sage, the Singular run is continuous, so we can make multiple calls to 
    # the same variables for example. 
    # Currently, no error checking here. 
    _ = _SING.lib(pdir + _CHART_LIB)
    _ = _SING.lib(pdir + 'LIB/primdec.lib')
    _ = _SING.lib(pdir + _INT_LAT_LIB)
    _ = _SING.eval(str_load_char + "\n" + str_set_ring)

    # Get the basics: coeff ring and vars.
    sing_ring_printout = _SING.eval(r_var + ";")
    coeff, varbs = _parse_printout(sing_ring_printout)

    # Get the factor of the ambient space.
    sing_amb_fact = _SING.eval("print(BO[1]);").replace(",", "").split("\n")
    if sing_amb_fact[0] != "0":
        # Print info about the ambient space 
        if verbose:
            print "Ambient space not necessarily affine."
        amb_fact = _parse_list_wrapped(sing_amb_fact)
    else:
        amb_fact = 0


    # Get the birational map data
    sing_birat_str = _SING.eval("print(BO[5]);").replace(",", "").split("\n")
    birat = _parse_list_wrapped(sing_birat_str)
    birat = tuple([im.factor() for im in birat])

    # Get the center of the blow-up
    sing_cent_str = _SING.eval("print(cent);").replace(",", "").split("\n")
    cent = _parse_list_wrapped(sing_cent_str)

    # Get the cone data
    sing_cone_printout = _SING.eval("Cone;").split("\n")
    cone = _parse_list(sing_cone_printout) # Do not want the wrapped version
    # Here, we clean up the cone data a little bit. 
    # We make sure that the first term is positive and everything is factored 
    # as much as possible. 
    def pos(x):
        y = str(x)
        if y[0] == "-":
            return -x
        else:
            return x
    factor_pair = lambda x: tuple([pos(_factor(y)) for y in x])
    cone_factored = map(factor_pair, cone)

    # Get the exceptional divisors
    num_exc_divs = int(_SING.eval("size(BO[4]);"))
    exDivs = _exDivs_wrap(num_exc_divs)

    # Get the Jacobian determinant
    try:
        sing_jacobian_str = _SING.eval("jacDet;")
        jacDet = _parse_list(sing_jacobian_str).factor() # Not wrapped version
        if str(jacDet)[0] == '-': # Remove the negative if it's there
            jacDet = -jacDet
    except:
        jacDet = 1 # Currently the Jacobian is not defined for the root.
    
    # Get the last map
    try:
        sing_lm_str = _SING.eval("print(lastMap);").replace(",", "").split("\n")
        lastmap = _parse_list_wrapped(sing_lm_str)
    except:
        lastmap = None

    # Get the focus
    sing_foc_str = _SING.eval("print(focus);").replace(",", "").split("\n")
    focus = _parse_list_wrapped(sing_foc_str)

    # Get the info read for the intersection lattice
    r_var2 = _get_safe_var()
    str_load_lat = 'def %s = createInterLattice(%s, "%s");' % (r_var2, num, direc)
    str_set_lat = 'setring %s;' % (r_var2)

    # Get the intersection lattice
    if get_lat and (amb_fact == 0):
        # Print statements for the user about the intersection lattice
        if verbose:
            print "Creating the intersection lattice."
            print "Running the following Singular code:"
            print "> " + str_load_lat
            print "> " + str_set_lat
        
        # Get all the data from the int lattice individually
        _ = _SING.eval(str_load_lat)
        _ = _SING.eval(str_set_lat)
        sing_lat_vert_str = _SING.eval('retlist[1];').split("\n")
        lat_vert = _parse_list(sing_lat_vert_str, var_expr=False)
        sing_lat_comp_str = _SING.eval('retlist[2];').split("\n")
        lat_comp = _parse_list(sing_lat_comp_str, var_expr=False)
        sing_lat_edge_str = _SING.eval('retlist[3];').split("\n")
        lat_edge = _parse_list(sing_lat_edge_str, var_expr=False)
        sing_lat_divs_str = _SING.eval('print(retlist[4]);').replace(",", "").replace("_[1]=", "").split("\n")
        lat_divs = _parse_list(sing_lat_divs_str)

        # Put all the data together
        lattice = _parse_lattice_data(lat_comp, lat_divs, lat_edge, lat_vert)
        random_varbs = [r_var, r_var2]
    else: 
        lattice = None
        random_varbs = [r_var]
        # TODO: update once we can compute the intersection lattice
        if verbose and amb_fact != 0:
            print "Cannot compute intersection lattice yet due to non-trivial ambient space."

    # Clean up the Singular run
    for v in random_varbs:
        _ = _SING.eval("kill %s;" % (v))

    # Now we construct our ring to keep all of this data in one place.
    C = _chart(coeff, varbs, \
        atlas=atlas,
        biratMap=birat, 
        cent=cent, 
        cone=cone_factored,
        exDivs=exDivs,
        factor=amb_fact,
        focus=focus,
        identity=num,
        intLat=lattice,
        jacDet=jacDet,
        lastMap=lastmap)

    return C