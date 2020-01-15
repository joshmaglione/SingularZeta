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

_verbose = False

# The following is a function written by Tobias Rossmann for counting the 
# F_q-rational points on varieties given by a sequence F. 
def _count_pts(F, torus=False):
    # Given a bunch of ordinary polynomials F, try to symbolically
    # count the number of GF(q) points of V(F).
    assert F

    # Pre-conditioning added my Josh.
    mult = lambda x, y: x*y
    F_poly = reduce(mult, F, 1)
    P = _poly_ring(_QQ, len(F_poly.variables()), F_poly.variables())
    F = map(lambda f: P(f), F)

    from itertools import product
    
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


# Given the ambient space and a system of polynomials, we return a lookup key 
# and the variables in (the ambient space, the defining ideal, and the system).
# 
# Structure of the look up key:
# KEY = (a, b, c, d)
#   a: the dimension of the ambient space, A
#   b: the number of variables in the defining ideal (the factor ideal) of A
#   c: the number of polynomials in the system, S
#   d: the number of variables in the system, S
def _build_key(d, Q, S):
    mult = lambda x, y: x*y

    # Get the relevant data from the ambient space.
    if Q != tuple([0]):
        varbs_Q = reduce(mult, Q, 1).variables()
        k_Q = len(varbs_Q)
    else:
        varbs_Q = ()
        k_Q = 0

    # We determine the number of variables in the system
    varbs_S = reduce(mult, S, 1).variables()
    k_S = len(varbs_S)

    # Key must be a tuple
    return tuple([d, k_Q, len(S), k_S]), [varbs_Q, varbs_S]


# Given the ambient space, the polynomial system and a variable, return the 
# degree vector of the variable in the defining ideal and the system.
def _get_deg_vec(Q, S, x):
    def deg(f):
        if f != 0:
            return f.degree(x)
        else:
            return 0
    return tuple(map(deg, list(Q) + S))


# Given the data from the variety, we convert it to a list of values that we 
# can effectively compare.
def _build_data(Q, S, varbs, verbose=_verbose):
    if verbose >= 2:
        print "Converting data:"
        print _indent + "Ambient factor ideal: %s" % (Q)
        print _indent + "Polynomial system: %s" % (S)
        print _indent + "Variables: %s" % (varbs)

    # Get our data
    n = len(varbs)
    deg_vecs = [_get_deg_vec(Q, S, x) for x in varbs]
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
    Q_new = map(embed, Q)
    S_new = map(embed, S)
    dv_new = [deg_vecs[i - 1] for i in perm]
    return [dv_new, Q_new, S_new]


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
        print _indent + "Found %s similar systems" % (len(rel_dat))

    # TODO: Improve this!
    return False, 0


# Given an ambient space and a polynomial system, return a pair: a boolean 
# stating whether we have seen this data before and either the key or the 
# count. The second entry depends on the first (not good typing sorry!). 
def _check_saved_table(P, S, ambient, verbose=_verbose):
    key_AS, sys_varbs = _build_key(len(P.gens()), ambient, S)
    known_keys = _lookup.keys()

    # check to see if we have even used this key before
    if not key_AS in known_keys:
        if verbose >= 2:
            print "No similar system is saved in database."
        _lookup[key_AS] = []
        return False, key_AS

    # at this point we know we can do a lookup safely
    table = _lookup[key_AS]
    data = _build_data(ambient, S, list(P.gens()))

    # decide if our system has been saved in our table
    if verbose >= 2:
        print "Checking database to find a similar system."
    
    check, count = _decide_equiv(data, table)

    if check: 
        output = tuple([True, count])
        if verbose >= 2:
            print "We found a match!"
    else:
        output = tuple([False, key_AS])
        if verbose >= 2:
            print "We didn't find anything."
    
    return output
    

def _save_to_lookup(P, S, ambient, key, count, verbose=_verbose):
    most_data = _build_data(ambient, S, list(P.gens()))
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
def _get_smaller_poly_ring(S, ambient, R):
    if 0 in ambient:
        ambient_fact = [1]
    else:
        ambient_fact = list(ambient)
    while 0 in S:
        k = S.index(0)
        S = S[:k] + S[k+1:]
    hyper = reduce(lambda x, y: x*y, S + ambient_fact)
    varbs = hyper.variables()
    P = _poly_ring(R, len(varbs), varbs)
    embed = lambda f: P(f)
    S_new = map(embed, S)
    ambient_new = map(embed, ambient)
    return P, S_new, ambient_new

# Given an ambient space A and a system of polynomials, attempt to either count 
# the number of p-rational points on the corresponding variety or return data 
# for a human to compute. 
def _rational_points(P, S, ambient,
    user_input=_user_input, 
    label=''):

    import Zeta as Z
    d = len(P.gens())
    p = _var(_p)

    # We might need to treat the ambient polynomials differently...
    if S == [0] and not 0 in ambient:
        S = list(ambient)
    elif not 0 in ambient:
        S += list(ambient)

    # If S is trivial and ambient is trivial, then return the trivial count.
    if S == [0]: 
        return tuple([p**d, (P, S, ambient)])

    # Remove possible repeats
    S = list(_set(S))

    # Split the system into linears and non-linears. 
    is_linear = lambda x: x.degree() == 1
    lin_polys = filter(is_linear, S)
    nonlin_polys = filter(lambda x: not is_linear(x), S)

    if len(nonlin_polys) == 0: # common enough to warrant
        # Linear system
        N = p**(d - len(S))
    else:
        # Nonlinear system
        
        # We substitute the linear terms in because this is can easily be done, 
        # and then we call our function again: with only nonlinear polynomials.
        if len(lin_polys) > 0:
            const_term = lambda f: f.subs({f.variables()[0] : 0})
            sub_dict = {f.variables()[0] : -1*const_term(f) for f in lin_polys}
            new_sys = map(lambda x: x.subs(sub_dict), nonlin_polys)
            P_new, smaller_sys, ambient_update = _get_smaller_poly_ring(new_sys, ambient, P.base_ring())
            N = _rational_points(P_new, smaller_sys, 
                user_input=user_input, 
                label=label,
                ambient=ambient_update)[0]
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
                    print "Searching through a table of order %s" % (len(_lookup))
                check, data = _check_saved_table(P, S, ambient)
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
                            print "Asking Tobias about \n%s" % (S)
                        N = _count_pts(S)
                        if _verbose >= 2:
                            print "Done"
                        Z.common.symbolic = z_symb_curr
                    except _CountException: 
                        # Now we ask the user or skip
                        if user_input:
                            N = _ask_user(P, S, label)
                            _save_to_lookup(P, S, ambient, data, N)
                        else:
                            N = _var('C' + label.replace(".", "_"))
    
    return tuple([N, (P, S)])