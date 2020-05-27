#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

# This file contains a test based on theorems from two papers. 
#   1. Stanislav Atanasov, Nathan Kaplan, Benjamin Krakoff, and Julian Menzel,
#      Counting Finite Index Subrings of Z^n, https://arxiv.org/abs/1609.06433.
#   2. Ricky Ini Liu, Counting subrings of Z^n of index k, J. Combin. Theory 
#      Ser. A, 114 (2007), no. 2, 278--299.
#

from globalVars import _is_int
from globalVars import _DEFAULT_p as _p
from globalVars import _DEFAULT_t as _t
from globalVars import _DEFAULT_VERBOSE as _verbose
from sage.all import binomial as _binom
from sage.all import taylor as _taylor
from sage.all import var as _var


def IsLocalSubringZF_Zn(Z, n, unital=True, Taylor=True, verbose=_verbose):
    # Type checking input.
    if not _is_int(n):
        raise TypeError("Excepted to receive an integer.")
    if not isinstance(unital, bool):
        raise TypeError("Expected parameter 'unital' to be boolean.")
    if not isinstance(Taylor, bool):
        raise TypeError("Expected parameter 'Taylor' to be boolean.")
    if not isinstance(verbose, int):
        raise TypeError("Expected parameter 'verbose' to be an integer.")

    # Do a quick change to make everything about *unital* subrings.
    if unital == False:
        n += 1
    
    # Rule out the dumb case.
    if n == 1:
        return Z == 1

    # Make sure we can handle the input Z. 
    try:
        if len(Z.variables()) > 2:
            raise ValueError("Expected input to be a symbolic function in at most two variables.")
        if not all(map(lambda x: str(x) in [_p, _t], Z.variables())):
            raise ValueError("Unsure which variable is which. Please use %s for p and %s for p^-s." % (_p, _t))
    except AttributeError:
        raise TypeError("Expected to receive a symbolic function.")

    # Define the variables as symbols
    p = _var(_p)
    t = _var(_t)
    
    # Theorems for the local unital zeta functions up to n = 4.
    local2 = lambda X, Y: 1/(1 - Y)
    local3 = lambda X, Y: (1 - Y**2)**2/((1 - Y)**3*(1 - X*Y**3))
    local4N = lambda X, Y: 1 + 4*Y + 2*Y**2 + (4*X - 3)*Y**3 + (5*X - 1)*Y**4 + (X**2 - 5*X)*Y**5 + (3*X**2 - 4*X)*Y**6 - 2*X**2*Y**7 - 4*X**2*Y**8 - X**2*Y**9 
    local4D = lambda X, Y: (1 - Y)**2 * (1 - X**2*Y**4) * (1 - X**3*Y**6)
    local4 = lambda X, Y: local4N(X, Y) / local4D(X, Y)
    local_zeta = [local2, local3, local4]

    # Theorems for the taylor expansion of the local unital zeta functions for 
    # terms up to t^8. Note as of 31 July 2019, terms t^5 and beyond have not 
    # been peer reviewed. Atanasov et al claimed Liu made a typo in his t^5 
    # term.
    zeta_terms = [
        lambda N, k: 1,
        lambda N, k: _binom(N, 2),
        lambda N, k: _binom(N, 2) + _binom(N, 3) + 3*_binom(N, 4),
        lambda N, k: _binom(N, 2) + (k + 1)*_binom(N, 3) + 7*_binom(N, 4) + 10*_binom(N, 5) + 15*_binom(N, 6),
        lambda N, k: _binom(N, 2) + (3*k + 1)*_binom(N, 3) + (k**2 + k + 10)*_binom(N, 4) + (10*k + 21)*_binom(N, 5) + 70*_binom(N, 6) + 105*_binom(N, 7) + 105*_binom(N, 8),
        lambda N, k: _binom(N, 2) + (4*k + 1)*_binom(N, 3) + (7*k**2 + k + 13)*_binom(N, 4) + (k**3 + k**2 + 41*k + 31)*_binom(N, 5) + (15*k**2 + 35*k + 141)*_binom(N, 6) + (105*k + 371)*_binom(N, 7) + 910*_binom(N, 8) + 1260*_binom(N, 9) + 945*_binom(N, 10)
    ]

    # A dictionary of tests
    tests = {}

    # Test against local zeta functions we already know. 
    if n <= 4:
        if verbose >= 1:
            print("Testing candidate local zeta function against the local unital zeta function for Z^%s" % (n))
        zeta = local_zeta[n - 2]
        diff = (zeta(p, t) - Z).simplify()
        are_equal = (diff == 0)
        if are_equal:
            return True
        else:
            tests['difference'] = diff
            ratio = (zeta(p, t)/Z).simplify().factor().simplify()
            tests['ratio'] = ratio

    # A function to get the coefficient of the kth term of the taylor expansion.
    def kth_Taylor(F, k): 
        if k == 0:
            return _taylor(F, t, 0, 0)
        else:
            return (_taylor(F, t, 0, k) - _taylor(F, t, 0, k-1))(t=1)

    # Now do a Taylor expansion to determine if the first few terms match.
    if Taylor:
        k = 0
        matching = True
        while matching and k < 6:
            k_term = kth_Taylor(Z, k)
            if k_term - zeta_terms[k](n, p) == 0:
                tests['Taylor-t-' + str(k)] = True
            else:
                tests['Taylor-t-' + str(k)] = {"target": zeta_terms[k](n, p), "candidate": k_term}
                matching = False
            k += 1

    return tests