#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from globalVars import _DEFAULT_INDENT as _indent
from globalVars import _DEFAULT_p as _p
from globalVars import _DEFAULT_USER_INPUT as _user_input
from globalVars import _DEFAULT_VERBOSE as _verbose
from globalVars import _Lookup_Table as _lookup
from sage.all import var as _var
from sage.all import AffineSpace as _affine_space
from sage.all import PolynomialRing as _poly_ring
from sage.all import Subsets as _subsets
from sage.all import GF as _GF
from sage.all import SR as _SR
from sage.all import QQ as _QQ
from sage.all import Word as _word
from sage.all import Set as _set
from parseSingularExpr import _parse_user_input
from Zeta.torus import CountException as _CountException


# The following is a function written by Tobias Rossmann for counting the 
# F_q-rational points on varieties given by a sequence F. 
def _count_pts(F, q=None, torus=False):
    # Given a bunch of ordinary polynomials F, try to symbolically
    # count the number of GF(q) points of V(F).
    assert F

    # Pre-conditioning added by Josh.
    mult = lambda x, y: x*y
    F_poly = reduce(mult, F, 1)
    P = _poly_ring(_QQ, len(F_poly.variables()), F_poly.variables())
    F = map(lambda f: P(f), F)

    from itertools import product
    if q:
        R = F[0].parent()
        n = R.ngens()
        K = _poly_ring(_GF(q),n, R.gens())
        G = [K(f) for f in F]
        res = 0
        for x in product(_GF(q),repeat=n):
            if torus and not product(x):
                continue
            if all(g(x) == 0 for g in G):
                res += 1
        return res
    q = _var(_p)
    R = F[0].parent()
    n = R.ngens()

    from Zeta.torus import SubvarietyOfTorus

    if torus:
        return SubvarietyOfTorus([F]).count().subs({_var('q') : q})
    
    total = _SR(0)
    for S in _subsets(R.gens()):
        D = {str(x): R(0) if x in S else x for x in R.gens()}
        G = [f(**D) for f in F]
        V = SubvarietyOfTorus(G)
        cnt = V.count().subs({_var('q') : q})/(q-1)**len(S)
        total += cnt
    return total.factor() if total else total

# Given a polynomial ring P and a system S, attempt to guess the polynomial 
# equation for the number of F_p-rational points. 
def _guess_polynomial(P, S):
    from sage.all import Matrix, Primes
    d = len(P.gens())
    # Find the cut off
    C = reduce(lambda x, y: x + y, map(lambda f: f.coefficients(), S), [])
    max_coeff = max(map(abs, C))
    E = reduce(lambda x, y: x + y, map(lambda f: f.exponents(), S), [])
    max_exp = max(map(lambda x: max(x), E))
    m = max(max_coeff, max_exp)
    primes = []
    for p in Primes():
        if len(primes) >= d + 3:
            break
        if p > m:
            primes.append(p)
    A_flat = map(lambda p: [p**k for k in range(d + 3)], primes)
    A = Matrix(_QQ, A_flat)
    b_flat = map(lambda p: [_count_pts(S, q=p)], primes)
    b = Matrix(_QQ, b_flat)
    X = A.solve_right(b)
    p = _var('X')
    data = zip(X.list(), [p**k for k in range(d + 3)])
    guess = reduce(lambda x, y: x + y[0]*y[1], data, 0)
    print guess
    if guess.degree(p) > d:
        return False, 0
    else:
        return True, guess

# Given the integer corresponding to the dimension of the underlying affine 
# space and a system of polynomials, we return a lookup key and the variables 
# in the system.
# 
# Structure of the look up key:
# KEY = (a, b, c, d)
#   a: the dimension of the affine space,
#   c: the number of polynomials in the system S,
#   d: the number of variables in the system S,
def _build_key(d, S):
    mult = lambda x, y: x*y

    # We determine the number of variables in the system
    varbs_S = reduce(mult, S, 1).variables()
    k_S = len(varbs_S)

    # Key must be a tuple
    return tuple([d, len(S), k_S]), [varbs_S]


# Given the polynomial system and a variable, return the 
# degree vector of the variable in the defining ideal and the system.
def _get_deg_vec(S, x):
    def deg(f):
        if f != 0:
            return f.degree(x)
        else:
            return 0
    return tuple(map(deg, S))


# Given the data from the variety, we convert it to a list of values that we 
# can effectively compare.
def _build_data(S, varbs, verbose=_verbose):
    # if verbose >= 2:
    #     print "Converting data:"
    #     print _indent + "Polynomial system: %s" % (S)
    #     print _indent + "Variables: %s" % (varbs)

    # Get our data
    n = len(varbs)
    deg_vecs = [_get_deg_vec(S, x) for x in varbs]
    # Sort the data based on internal ordering
    perm = _word(deg_vecs).standard_permutation().inverse()

    # Build the change of variables dictionary
    var_change = {varbs[perm[i]-1] : _var("X" + str(i)) for i in range(n)}
    # Build the change of variables function
    def embed(f): 
        if f != 0:
            f.subs({x : var_change[x] for x in f.variables()})
        else:
            return 0

    # Get the new data
    S_new = map(embed, S)
    dv_new = [deg_vecs[i - 1] for i in perm]
    return [dv_new, S_new]


# Given the polynomial system data and a table, we decide if there is a match. 
# If there is no match, we return (False, 0); if there is a match, we return 
# (True, count), where count is the number of p-rational points saved in the 
# table. 
def _decide_equiv(data, table, verbose=_verbose):
    deg_vec = data[0]
    eq_deg_vec = lambda x: x[0] == deg_vec
    rel_dat = filter(eq_deg_vec, table)
    if len(rel_dat) == 0:
        return False, 0

    if verbose >= 2:
        print _indent*2 + "Found %s similar systems" % (len(rel_dat))

    # TODO: Improve this!
    return False, 0


# Given a polynomial ring and a system of polynomials, return a pair: a boolean 
# stating whether we have seen this data before and either the key or the 
# count. The second entry depends on the first (not good typing sorry!). 
def _check_saved_table(P, S, verbose=_verbose):
    key_AS, _ = _build_key(len(P.gens()), S)
    known_keys = _lookup.keys()

    # check to see if we have even used this key before
    if not key_AS in known_keys:
        if verbose >= 2:
            print _indent*2 + "No similar system is saved in database."
        _lookup[key_AS] = []
        return False, key_AS

    # at this point we know we can do a lookup safely
    table = _lookup[key_AS]
    data = _build_data(S, list(P.gens()))

    # decide if our system has been saved in our table
    if verbose >= 2:
        print _indent*2 + "Checking database to find a similar system."
    
    check, count = _decide_equiv(data, table)

    if check: 
        output = tuple([True, count])
        if verbose >= 2:
            print _indent*2 + "We found a match!"
    else:
        output = tuple([False, key_AS])
        if verbose >= 2:
            print _indent*2 + "We didn't find anything."
    
    return output
    

def _save_to_lookup(P, S, key, count, verbose=_verbose):
    most_data = _build_data(S, list(P.gens()))
    data = most_data + [count]

    assert key in _lookup.keys()
    table = _lookup[key]
    table.append(data)
    _lookup[key] = table

    if verbose >= 2:
        print "Saved input to database."
        print _lookup


# Given a system of polynomials, check to see if the support of the polynomials 
# are disjoint.
def _split_support(S):
    varbs = [f.variables() for f in S]
    i = 0
    while i < len(varbs):
        for j in range(i + 1, len(varbs)):
            I = {str(x) for x in varbs[i]}
            J = {str(y) for y in varbs[j]}
            if len(I.intersection(J)) != 0:
                return False
        i += 1
    return True


# Given a system of polynomials, check to see if all polynomials:
#   1. are binomial, 
#   2. have nonzero constant coefficient, and
#   3. have a variable of degree 1.
def _binom_system(S):
    not_binom = lambda x: x.number_of_terms() != 2
    zero_const = lambda x: x.constant_coefficient() == 0

    if any(map(not_binom, S)):
        return False
    if any(map(zero_const, S)):
        return False

    def deg_one_var(f):
        varbs = f.variables()
        for x in varbs:
            if f.degree(x) == 1:
                return True
        return False

    if not all(map(deg_one_var, S)):
        return False
    return True


# Given the variety and a label, ask the user to count the p-rational points on 
# the variety. 
def _ask_user(Aff, S, label):
    print '\nCount the number of points on:\n%s defined by:' % (Aff)
    for f in S:
        print _indent + '%s' % (f)
    need_input = True
    not_poly = {_var('n'), _var('N')}
    while need_input:
        print 'If not a polynomial in p, write N.'
        exp_str = input('How many? Use %s if needed.\n' % (_p))
        if exp_str in not_poly:
            need_input = False
            C = _var('C' + label.replace(".", "_"))
        else:
            try:
                need_input = False
                C = _parse_user_input(exp_str)
            except:
                print 'Unknown expression.'
                need_input = True
    return C

# Get the underlying polynomial ring (over the variables with non-normal 
# crossings)
def _get_smaller_poly_ring(S, R, ambient=None):
    if ambient != None and not 0 in ambient:
        ambient_new = ambient
    else:
        ambient_new = []
    while 0 in S:
        k = S.index(0)
        S = S[:k] + S[k+1:]
    hyper = reduce(lambda x, y: x*y, S + ambient_new)
    varbs = hyper.variables()
    P = _poly_ring(R, len(varbs), varbs)
    embed = lambda f: P(f)
    S_new = map(embed, S)
    if ambient != None:
        ambient = map(embed, ambient)
    return P, S_new, ambient

def _simplify_with_linears(P, linears, nonlinears):
    from sage.all import Matrix
    column_labels = reduce(lambda x, y: x*y, linears, 1).variables()
    # turn linear polynomial into coefficient vector with constant at end.
    def coeff_vec(f):
        monos = f.monomials()
        coeffs = f.coefficients()
        def replace(x): 
            if x in monos:
                return coeffs[monos.index(x)]
            else:
                return 0
        v = list(column_labels)
        return map(replace, v) + [f.constant_coefficient()]
    row_vecs = map(coeff_vec, linears)
    A = Matrix(_QQ, len(linears), len(column_labels) + 1, row_vecs)
    B = A.rref()
    # Convert the nonzero rows to a substitution function.
    def sub_func(v):
        piv = v.support()[0]
        fold_with_mult = lambda x, y: x + y[0]*y[1]
        im = -reduce(fold_with_mult, zip(v[piv + 1:], column_labels[piv + 1:]),
            v[-1])
        return {column_labels[piv] : im}
    nonzero_row = lambda r: r.support() != []
    funcs = map(sub_func, filter(nonzero_row, B.rows()))
    # Doesn't seem to be a good python 2 way to merge dictionaries easily.
    def merge_dicts(d1, d2):
        d = d1.copy()
        d.update(d2)
        return d
    sub_dict = reduce(merge_dicts, funcs, dict())
    substitution = lambda x: x.subs(sub_dict)
    nonzero_polys = lambda f: f != 0
    new_sys = filter(nonzero_polys, map(substitution, nonlinears))
    if new_sys == []:
        key_to_poly = lambda x: x - sub_dict[x]
        simplified_lins = list(map(key_to_poly, sub_dict.keys()))
        return _get_smaller_poly_ring(simplified_lins, P.base_ring())
    else:
        return _get_smaller_poly_ring(new_sys, P.base_ring())

# Given a polynomial ring P and a system of polynomials, attempt to either 
# count the number of p-rational points on the corresponding variety or return 
# data for a human to compute. 
def _rational_points(P, S,
    user_input=_user_input, 
    label=''):

    import Zeta as Z
    d = len(P.gens())
    p = _var(_p)
    T = S
    P_new = P

    # If S is trivial, then return the trivial count.
    if S == [0]: 
        data = {
            "original_ring": P, 
            "original_system": S, 
            "simplified_ring": P_new,
            "simplified_system": T
        }
        return tuple([p**d, data])

    # Remove possible repeats
    S = list(_set(S))

    # Get number of free vars
    free = d - len(reduce(lambda x, y: x*y, S, 1).variables())

    # Split the system into linears and non-linears. 
    is_linear = lambda x: x.degree() == 1
    lin_polys = filter(is_linear, S)
    nonlin_polys = filter(lambda x: not is_linear(x), S)

    if len(nonlin_polys) == 0: # common enough to warrant
        # Linear system
        # First we delete repeated information.
        P_lin, T, _ = _simplify_with_linears(P, lin_polys, nonlin_polys)
        N = p**(len(P_lin.gens()) - len(T))
    else:
        # Nonlinear system
        
        # We substitute the linear terms in because this is can easily be done, 
        # and then we call our function again: with only nonlinear polynomials.
        if len(lin_polys) > 0:
            P_new, smaller_sys, _ = _simplify_with_linears(P, lin_polys, 
                nonlin_polys)
            N, new_data = _rational_points(P_new, smaller_sys,
                user_input=user_input, 
                label=label)
            T = new_data["simplified_system"]
            P_new = new_data["simplified_ring"]
        else:
            # First we check if there's a possibility that we can solve this
            # I can only think of a nice binomial system where the 
            # support of the nonlinear binomials are disjoint.
            feasible = lambda x: _split_support(x) and _binom_system(x)
            if feasible(nonlin_polys):
                get_num_vars = lambda x, y: x + len(y.variables())
                num_vars = reduce(get_num_vars, nonlin_polys, 0)
                N = (p - 1)**(num_vars - len(nonlin_polys))
                N *= p**(d - num_vars)
            else:
                # First we look up our table
                if _verbose >= 2:
                    print _indent*2 + "Searching through a table of order %s" % (len(_lookup))
                check, data = _check_saved_table(P, S)
                if check: 
                    N = data
                else:
                    # It is not contained in our table, so we continue
                    try:
                        # Now we apply Rossmann's toric counting function
                        # We turn off symbolic counting
                        z_symb_curr = Z.common.symbolic
                        Z.common.symbolic = False
                        if _verbose >= 2:
                            print _indent*2 + "Asking Tobias about \n%s%s" % (_indent*3, S)
                        N = _count_pts(S)
                        if _verbose >= 2:
                            print _indent*2 + "Done"
                        Z.common.symbolic = z_symb_curr
                    except _CountException: 
                        # Now we ask the user or skip
                        if user_input:
                            N = _ask_user(P, S, label)
                            _save_to_lookup(P, S, data, N)
                        else:
                            N = _var('C' + label.replace(".", "_"))

    data = {
        "original_ring": P, 
        "original_system": S, 
        "simplified_ring": P_new,
        "simplified_system": T
    }
    return tuple([p**free*N, data])