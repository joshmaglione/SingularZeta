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
from sage.all import AffineSpace as _Aff
from sage.all import GF as _GF
from sage.all import Matrix as _matrix
from sage.all import Polyhedron as _polyhedron
from sage.all import PolynomialRing as _polyring
from sage.all import Primes as _Primes
from sage.all import QQ as _QQ
from sage.all import symbolic_expression as _symb_expr
from sage.all import var as _var
from sage.all import ZZ as _ZZ
from Zeta.smurf import SMURF as _Zeta_smurf


################################################################################
#   An integral test
################################################################################

def _trivial_cone(C, I, verbose=_verbose):
    # Clean up the variables and cone data
    c_varbs, c_cone, trivial = _clean_cone_data(C.variables, [(1, 1)])

    if trivial:
        if verbose >= 1:
            print "Trivial set to integrate over."
        return 0

    if verbose >= 1:
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

    if verbose >= 2:
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
    
    if verbose >= 1:
        print "Applying the following change of variables:"
        if n > 1: 
            for i in range(n):
                print "%s%s -> %s" % (_indent, c_varbs[i], var_change[_var('Z' + str(i))])
        else:
            print "%s%s -> %s" % (_indent, c_varbs[0], var_change[_var('Z')])

    zed = I.pFactor() * (1 - p**(-1))**n * S.evaluate()

    if verbose >= 1:
        print "Multiplying by:"
        print "%s%s" % (_indent, I.pFactor() * (1 - p**(-1))**n)

    if zed == 0:
        return 0
    zed = zed.subs(var_change).simplify().factor()
    return zed



def _zeta_solve(C, verbose=_verbose, integ=True, cone=True):
    if verbose >= 1: 
        print "="*79
        print "Solving the integral for Chart %s." % (C._id)

    # First decide if the chart is monomial
    if C.IsMonomial():
        subcharts = [C]
    else:
        if _verbose >= 2:
            print "Constructing monomial subcharts."
        # First we get the monomial subcharts
        subcharts = C.Subcharts(verbose=verbose)

    if verbose >= 1:
        print "Constructing integral."

    if integ:
        # Removes the integrand plus the factor (1 - p^-1)^k
        temp_integrand = _integrand([[1, (1, 0)]])
    else:
        temp_integrand = C.atlas.integrand

    # Now we determine the integrands for each subchart
    build_int = lambda X: _get_integrand(C.atlas.root.variables, X.birationalMap, temp_integrand, X.jacDet, X._integralFactor)
    integrands = map(build_int, subcharts)

    if verbose >= 1:
        print("Solving %s integrals." % (len(integrands)))

    chrt_int = zip(subcharts, integrands)
    gen_funcs = []
    for t in chrt_int:
        if verbose >= 1:
            print "-"*79
            print "Solving the integral for Subchart %s." % (t[0]._id)
            _integral_printout(t[0])
        if cone:
            gen_funcs.append(_trivial_cone(t[0], t[1]))
        else:
            gen_funcs.append(_mono_chart_to_gen_func(t[0], t[1]))

    add_up = lambda x, y: x + y

    return reduce(add_up, gen_funcs, 0)


def IntegralTests(A, chart_filter=None, cone_condition=True, integrand=True):
    add_up_ints = lambda x, y: x + _zeta_solve(y, cone=cone_condition, integ=integrand)
    # Currently we do not have the intersection lattice of a chart with an 
    # ambient space different from the standard affine space.
    AVOID_BUG = lambda x: x.intLat != None
    if chart_filter == None:
        wrap = lambda x: True
    else:
        if not isinstance(chart_filter, type(lambda x: x)):
            raise TypeError("Expected chart_filter to be a function compatible with filter.")
        wrap = chart_filter
    relevant_charts = filter(wrap, filter(AVOID_BUG, A.charts))
    return reduce(add_up_ints, relevant_charts, 0)

################################################################################
################################################################################


################################################################################
#   A p-rational point test
################################################################################

def _count_p(tup, p):
    target = _symb_expr(tup[0])
    S = tup[1]
    K = _GF(p)
    S_K = S.change_ring(K)
    target_p = target.subs({_var(_p) : p})
    return len(S_K.rational_points()) == target_p

def _vertex_p(target, vertex, divisor, p):
    divisors = map(lambda f: _symb_expr(f), divisor)
    varbs = reduce(lambda x, y: x*y, divisors, 1).variables()
    A = _Aff(len(varbs), _GF(p), varbs)
    sys_on = [divisors[k] for k in vertex]
    sys_off = [divisors[k] for k in range(len(divisor)) if not k in vertex]
    # We need to use tuple to remove extra info that sage carries.
    get_points = lambda S: set(map(lambda pt : tuple(pt), A.subscheme(S).rational_points()))
    points_off = reduce(lambda x,y: y.union(x), map(get_points, sys_off), set())
    points_on = get_points(sys_on)
    relevant_points = points_on.difference(points_off)
    target_p = _symb_expr(target).subs({_var(_p) : p})
    return target_p == len(relevant_points)


def pRationalPointChartTest(C, primes_excluded=[2], bound=20, verbose=_verbose):
    I = C.intLat
    p = _ZZ.coerce(2)

    if verbose >= 1:
        print "Checking the number of F_p-points on the listed varieties are correct."
        if C.atlas != None:
            print "%sChart: %s," % (_indent, C._id)
            print "%sAtlas: %s," % (_indent, C.atlas.directory)
        print "%sExcluding primes: %s," % (_indent, primes_excluded)
        print "%sBound: %s," % (_indent, bound)
        print "%sNumber of varieties: %s" % (_indent, len(I.vertices))

    while p < bound:
        if not p in primes_excluded:
            for tup in I.pRationalPoints():
                if not _count_p(tup, p):
                    if verbose >= 1:
                        print "The following entry is incorrect for p = %s:\n%s" % (p, tup)
                    raise AssertionError("Failed the test. If there is a bad prime, consider excluding it.")
            for k in range(len(I.vertices)):
                target = I._vertexToPoints[k]
                vertex = I.vertices[k]
                if not _vertex_p(target, vertex, I.divisors, p):
                    if verbose >= 1:
                        print "The following vertex has incorrect point count for p = %s:\n%s%s" % (p, _indent, vertex)
                    raise AssertionError("Failed the test. If there is a bad prime, consider excluding it.")
        p = _Primes().next(p)

    return True

def pRationalPointTest(A, primes_excluded=[2], bound=20, verbose=_verbose):
    return all(map(lambda C: pRationalPointChartTest(C, 
        primes_excluded=primes_excluded,
        bound=bound,
        verbose=verbose),
        A.charts))