#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from globalVars import _DEFAULT_INDENT as _indent
from globalVars import _DEFAULT_p as _p
from globalVars import _DEFAULT_t as _t
from globalVars import _DEFAULT_VERBOSE as _verbose
from sage.all import Matrix as _matrix
from sage.all import var as _var
from sage.all import Permutations as _perms
from sage.all import Polyhedron as _polyhedron
from sage.all import PolynomialRing as _polyring
from sage.all import QQ as _QQ
from Zeta.smurf import SMURF as _Zeta_smurf

# There is a problem with nonpositive vectors in the Polyhedron code, so we 
# clean up our cone data.
def _clean_cone_data(varbs, cone):
    clean_varbs = list(varbs)
    clean_cone = cone
    i = 0
    j = 0
    p = _var(_p)

    # First we check the left hand side
    while i < len(clean_cone):
        if clean_cone[i][0] == 1:
            clean_cone = clean_cone[:i] + clean_cone[i + 1:]
        else: 
            i += 1
    
    # Now we handle the right hand side
    while j < len(clean_cone):
        if clean_cone[j][1] == 1:
            f = clean_cone[j][0]
            if p in f.variables():
                return [], [], True
            for x in f.variables():
                if x in clean_varbs:
                    clean_varbs.remove(x)
            clean_cone = clean_cone[:j] + clean_cone[j + 1:]
        else:
            j += 1
    
    return clean_varbs, clean_cone, False


# Given cone data and variables, return the corresponding matrix
def _cone_mat(varbs, cone):
    a = len(varbs)
    b = len(cone)
    p = _var(_p)
    cone_conditions = [[0 for i in range(a + 1)] for j in range(a + b)]

    # Get the rows corresponding to nonnegative integers
    for i in range(len(varbs)):
        cone_conditions[i][i + 1] = 1

    # For some reason f.degree(x) returns a symbolic expression... UGHHH
    def my_deg(f, x): 
        return _QQ.coerce(int(str(f.degree(x))))

    # Get the rows from the actual cone data
    for i in range(b):
        lhs = cone[i][0]
        rhs = cone[i][1]
        if lhs != 1:
            cone_conditions[a + i][0] -= my_deg(lhs, p)
            for j in range(len(varbs)):
                cone_conditions[a + i][j + 1] -= my_deg(lhs, varbs[j])
            if rhs != 1:
                cone_conditions[a + i][0] += my_deg(rhs, p)
                for j in range(len(varbs)):
                    cone_conditions[a + i][j + 1] += my_deg(rhs, varbs[j])

    to_tup = lambda x: tuple(x)
    return list(map(to_tup, cone_conditions))

# If we cannot subsitute all variables at once, sub in as much as we can first 
# before factoring and simplifying.
# Here we generate a number of random permutations for subsituting. This should 
# be seen as trying a number of random substitutions and seeing which one is 
# both legal and has the fewest number of variables. At the end, we simplify 
# the one with the few number of variables. 
def _get_sub(Z, subs):
    if _verbose >= 2:
        print "Had problems with substituting. Searching for alternatives."
    keys = subs.keys()
    n = len(keys)
    rand_perms = [list(_perms(n).random_element()) for _ in range(n)]
    shuffle = lambda S, k: [S[rand_perms[k][i]-1] for i in range(n)]
    shuff_keys = [shuffle(keys, k) for k in range(n)]
    vals = [-1 for _ in range(n)]
    funcs = [0 for _ in range(n)]
    for i in range(n):
        for j in range(1, n):
            if vals[i] == -1:
                partial_subs = {shuff_keys[i][k] : subs[shuff_keys[i][k]] 
                    for k in range(j)}
                try:
                    f = Z.subs(partial_subs)
                except ValueError:
                    vals[i] = i
                    if j > 0:
                        partial_subs = {shuff_keys[i][k] : subs[shuff_keys[i][k]] for k in range(j-1)}
                        f = Z.subs(partial_subs)
                    else:
                        f = Z
                    funcs[i] = f

    def count_vars(f):
        try:
            return len(f.variables())
        except AttributeError:
            return len(Z.variables()) + 1
    num_vars = map(lambda f: count_vars(f), funcs)
    m = min(num_vars)
    k = num_vars.index(m)
    remaining = {shuff_keys[k][j] : subs[shuff_keys[k][j]] for j in range(vals[k])}

    if _verbose >= 2:
        print "Most optimal option found has %s variables, down from %s." % (m, len(Z.variables()))

    return (funcs[k].simplify().factor()).subs(remaining).simplify().factor()


# Given a monomial chart and its integrand, return its generating function. The 
# output is from Zeta.
def _mono_chart_to_gen_func(C, I, verbose=_verbose):
    # Clean up the variables and cone data
    c_varbs, c_cone, trivial = _clean_cone_data(C.variables, C.cone)

    if trivial:
        if verbose >= 1:
            print "Trivial set to integrate over."
        return 0

    if verbose >= 1:
        print "Started with the following data."
        print "%sVariables: %s" % (_indent, list(C.variables))
        print "%sCone data: %s\n" % (_indent, C.cone)
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
    try:
        zed = zed.subs(var_change).simplify().factor()
    except ValueError:
        zed = _get_sub(zed, var_change)
    return zed
