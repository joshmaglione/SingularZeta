#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import var as _var
from sage.all import AffineSpace as _affine_space
from sage.all import QQ as _QQ
from parseSingularExpr import _parse_user_input

# Given an ambient space A and a system of polynomials, attempt to either count 
# the number of p-rational points on the corresponding variety or return data 
# for a human to compute. 
def _rational_points(A, S, user_input=False, label=''):
    Aff = _affine_space(len(A.gens()), _QQ, A.gens())
    d = Aff.dimension()
    variety = Aff.subscheme(S)
    p = _var('p')
    is_linear = lambda x: x.degree() == 1

    if all(map(is_linear, S)): # common enough to warrant
        # linear system
        N = p**(d - len(S))
    else:
        # nonlinear system
        if user_input:
            print 'Count the number of points on:\n' + str(variety)
            need_input = True
            while need_input:
                exp_str = input('How many? Use p if needed.\n')
                try:
                    N = _parse_user_input(exp_str)
                    need_input = False
                except:
                    print 'Unknown symbol.'
        else:
            N = _var('C' + label)
    
    return tuple([N, variety])