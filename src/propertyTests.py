#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from atlasClass import Atlas as _atlas
from globalVars import _DEFAULT_INDENT as _indent
from globalVars import _DEFAULT_p as _p
from globalVars import _DEFAULT_t as _t
from globalVars import _DEFAULT_VERBOSE as _verbose
from integrandClass import _get_integrand, _integral_printout
from integrandClass import Integrand as _integrand 
from interfaceZeta import _clean_cone_data, _cone_mat, _mono_chart_to_gen_func
from sage.all import Matrix as _matrix
from sage.all import Polyhedron as _polyhedron
from sage.all import PolynomialRing as _polyring
from sage.all import QQ as _QQ
from sage.all import var as _var
from Zeta.smurf import SMURF as _Zeta_smurf

def _trivial_cone(C, I, verbose=_verbose):
    # Clean up the variables and cone data
    c_varbs, c_cone, trivial = _clean_cone_data(C.variables, [(1, 1)])

    if trivial:
        if verbose:
            print "Trivial set to integrate over."
        return 0

    if verbose:
        print "Started with the following data."
        print "%sVariables: %s" % (_indent, list(C.variables))
        print "%sCone data: %s\n" % (_indent, [(1, 1)])
        print "Cleaned it up to the following."
        print "%sVariables: %s" % (_indent, c_varbs)
        print "%sCone data: %s\n" % (_indent, c_cone)

    # Get the matrix of inequalities so Polyhedron can read it
    cone_mat = _cone_mat(c_varbs, c_cone)
    P = _polyhedron(ieqs=cone_mat)
    n = len(c_varbs)
    R = _polyring(_QQ, 'Z', n)

    if verbose:
        print "Running Zeta via the polyhedron:"
        print "%s" % (_matrix(cone_mat))

    # Run Zeta
    S = _Zeta_smurf.from_polyhedron(P, R)

    # Clean up the output
    p = _var(_p)
    t = _var(_t)
    tup_to_p_t = lambda T: p**(-T[0] - 1)*t**(T[1])
    def p_val(x): 
        if str(x) in I._term_dict.keys():
            return tup_to_p_t(I._term_dict[str(x)])
        else:
            return p**(-1)
    
    # Different naming convention if it is univariate.
    if n > 1:
        var_change = {_var('Z' + str(i)) : p_val(c_varbs[i]) for i in range(n)}
    else:
        var_change = {_var('Z') : p_val(c_varbs[0])}
    
    if verbose:
        print "Applying the following change of variables:"
        if n > 1: 
            for i in range(n):
                print "%s%s -> %s" % (_indent, c_varbs[i], var_change[_var('Z' + str(i))])
        else:
            print "%s%s -> %s" % (_indent, c_varbs[0], var_change[_var('Z')])

    zed = I.pFactor() * (1 - p**(-1))**n * S.evaluate()

    if verbose:
        print "Multiplying by:"
        print "%s%s" % (_indent, I.pFactor() * (1 - p**(-1))**n)

    if zed == 0:
        return 0
    zed = zed.subs(var_change).simplify().factor()
    return zed



def _zeta_solve(C, verbose=_verbose, integ=True, cone=True):
    if verbose: 
        print "="*79
        print "Solving the integral for Chart %s." % (C._id)

    # First decide if the chart is monomial
    if C.IsMonomial():
        subcharts = [C]
    else:
        if _verbose:
            print "Constructing monomial subcharts."
        # First we get the monomial subcharts
        subcharts = C.Subcharts(verbose=verbose)

    if _verbose:
        print "Constructing integral."

    if integ:
        temp_integrand = _integrand([[1, (1, 0)]])
    else:
        temp_integrand = C.atlas.integrand

    # Now we determine the integrands for each subchart
    build_int = lambda X: _get_integrand(C.atlas.root.variables, X.birationalMap, temp_integrand, X.jacDet, X._integralFactor)
    integrands = map(build_int, subcharts)

    if _verbose:
        print("Solving %s integrals." % (len(integrands)))

    chrt_int = zip(subcharts, integrands)
    gen_funcs = []
    for t in chrt_int:
        if verbose:
            print "-"*79
            print "Solving the integral for Subchart %s." % (t[0]._id)
            _integral_printout(t[0])
        if cone:
            gen_funcs.append(_trivial_cone(t[0], t[1]))
        else:
            gen_funcs.append(_mono_chart_to_gen_func(t[0], t[1]))

    add_up = lambda x, y: x + y

    return reduce(add_up, gen_funcs, 0)

def IntegralTests(A, cone_condition=True, integrand=True):
    add_up_ints = lambda x, y: x + _zeta_solve(y, cone=cone_condition, integ=integrand)
    # Currently we do not have the intersection lattice of a chart with an 
    # ambient space different from the standard affine space.
    AVOID_BUG = lambda x: x.intLat != None
    return reduce(add_up_ints, filter(AVOID_BUG, A.charts), 0)