#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import var as _var
from sage.all import AffineSpace as _affine_space
from sage.all import QQ as _QQ

# Given an ambient space A and a system of polynomials, attempt to either count 
# the number of p-rational points on the corresponding variety or return data 
# for a human to compute. 
def _rational_points(A, S, label=''):
    Aff = _affine_space(len(A.gens()), _QQ, A.gens())
    d = Aff.dimension()
    variety = Aff.subscheme(S)
    p = _var('p')
    is_linear = lambda x: x.degree() == 1

    if all(map(S, is_linear)): # common enough to warrant
        # linear system
        N = p^(d - len(S))
    else:
        # nonlinear system
        N = _var('pRP' + label)
    
    return tuple([N, variety])