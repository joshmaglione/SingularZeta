#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from globalVars import _DEFAULT_USER_INPUT as _user_input
from globalVars import _Lookup_Table as _lookup
from sage.all import var as _var
from sage.all import AffineSpace as _affine_space
from sage.all import QQ as _QQ
from parseSingularExpr import _parse_user_input

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


# Given a polynomial system, check the table to see if we already know the 
# count. 
def _check_saved_table(S):
    # TODO: Add a lookup! 

    

# Given an ambient space A and a system of polynomials, attempt to either count 
# the number of p-rational points on the corresponding variety or return data 
# for a human to compute. 
def _rational_points(A, S, user_input=_user_input, label=''):
    Aff = _affine_space(len(A.gens()), _QQ, A.gens())
    d = Aff.dimension()
    variety = Aff.subscheme(S)
    p = _var('p')
    is_linear = lambda x: x.degree() == 1

    # Split the system into linears and non-linears. 
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
            if user_input:
                print 'Count the number of points on:\n' + str(variety)
                need_input = True
                while need_input:
                    exp_str = input('How many? Use p if needed.\n')
                    try:
                        N = _parse_user_input(exp_str)
                        need_input = False
                    except:
                        print 'Unknown expression.'
            else:
                N = _var('C' + label)
    
    return tuple([N, variety])