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
from sage.all import QQ as _QQ
from sage.all import Word as _word
from parseSingularExpr import _parse_user_input

# Given the ambient space and a system of polynomials, we return a lookup key 
# and the variables in (the ambient space, the defining ideal, and the system).
# 
# Structure of the look up key:
# KEY = (a, b, c, d)
#   a: the dimension of the ambient space, A
#   b: the number of variables in the defining ideal (the factor ideal) of A
#   c: the numer of polynomials in the system, S
#   d: the number of variables in the system, S
def _build_key(d, Q, S):
    mult = lambda x, y: x*y

    # Get the relevant data from the ambient space.
    if Q != []:
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
    deg = lambda f: f.degree(x)
    return tuple(map(deg, Q + S))


# Given the data from the variety, we convert it to a list of values that we 
# can effectively compare.
def _build_data(Q, S, varbs, verbose=_verbose):
    if verbose:
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
    embed = lambda f: f.subs({x : var_change[x] for x in f.variables()})

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

    if verbose:
        print _indent + "Found %s similar systems" % (len(rel_dat))

    # TODO: Improve this!
    return False, 0


# Given an ambient space and a polynomial system, return a pair: a boolean 
# stating whether we have seens this data before and either the key or the 
# count. The second entry depends on the first (not good typing sorry!). 
def _check_saved_table(A, S, verbose=_verbose):
    # We need to know if there is a defining polynomial
    try:
        I = A.defining_ideal() # Only place where an error can occur
        Q = I.gens()
        C = A.cover_ring()
    except:
        Q = []
        C = A

    key_AS, sys_varbs = _build_key(A.dimension(), Q, S)
    known_keys = _lookup.keys()

    # check to see if we have even used this key before
    if not key_AS in known_keys:
        if verbose:
            print "No similar system is saved in database."
        _lookup[key_AS] = []
        return False, key_AS

    # at this point we know we can do a lookup safely
    table = _lookup[key_AS]
    data = _build_data(Q, S, list(C.gens()))

    # decide if our system has been saved in our table
    if verbose:
        print "Checking database to find a similar system."
    
    check, count = _decide_equiv(data, table)

    if check: 
        output = tuple([True, count])
        if verbose:
            print "We found a match!"
    else:
        output = tuple([False, key_AS])
        if verbose:
            print "We didn't find anything."
    
    return output
    

def _save_to_lookup(A, S, key, count, verbose=_verbose):
    # We need to know if there is a defining polynomial
    try:
        I = A.defining_ideal() # Only place where an error can occur
        Q = I.gens()
        C = A.cover_ring()
    except:
        Q = []
        C = A
    most_data = _build_data(Q, S, list(C.gens()))
    data = most_data + [count]

    assert key in _lookup.keys()
    table = _lookup[key]
    table.append(data)
    _lookup[key] = table

    if verbose:
        print "Saved input to database."
        print _lookup


# Given a system of polynomials, check to see if the support of the polynomials 
# are disjoint.
def _check_split_support(S):
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
def _check_binom_system(S):
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
def _ask_user(variety, label):
    print '\nCount the number of points on:\n%s' % (variety)
    need_input = True
    not_poly = {_var('n'), _var('N')}
    while need_input:
        print 'If not a polynomial in p, write N.'
        exp_str = input('How many? Use %s if needed.\n' % (_p))
        if exp_str in not_poly:
            need_input = False
            C = _var('C' + label)
        else:
            try:
                need_input = False
                C = _parse_user_input(exp_str)
            except:
                print 'Unknown expression.'
                need_input = True
    return C


# Given an ambient space A and a system of polynomials, attempt to either count 
# the number of p-rational points on the corresponding variety or return data 
# for a human to compute. 
def _rational_points(A, S, user_input=_user_input, label=''):
    Aff = _affine_space(len(A.gens()), _QQ, A.gens())
    d = Aff.dimension()
    variety = Aff.subscheme(S)
    p = _var(_p)
    
    # If S is trivial, then return the trivial count.
    if S == [0]: 
        return p**d

    # Split the system into linears and non-linears. 
    is_linear = lambda x: x.degree() == 1
    lin_polys = filter(is_linear, S)
    nonlin_polys = filter(lambda x: not is_linear(x), S)

    if len(nonlin_polys) == 0: # common enough to warrant
        # Linear system
        N = p**(d - len(S))
    else:
        # Nonlinear system
        # First we check if there's a possibility that we can solve this
        # At the moment, I can only think of a nice binomial system where the 
        # support of the nonlinear binomials are disjoint.
        feasible = lambda x: _check_split_support(x) and _check_binom_system(x)
        if feasible(nonlin_polys):
            get_num_vars = lambda x, y: x + len(y.variables())
            num_vars = reduce(get_num_vars, nonlin_polys, 0)
            N = (p - 1)**(num_vars - len(nonlin_polys))
            N *= p**(d - num_vars - len(lin_polys))
        else:
            # First we look up our table
            check, data = _check_saved_table(Aff, S)
            if check: 
                N = data
            else:
                # At this stage it is not contained in our table, so we continue
                if user_input:
                    N = _ask_user(variety, label)
                    _save_to_lookup(Aff, S, data, N)
                else:
                    N = _var('C' + label)
    
    return tuple([N, variety])