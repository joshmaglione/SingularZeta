#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import var as _var
from sage.all import Polyhedron as _polyhedron

# There is a problem with nonpositive vectors in the Polyhedron code, so we 
# clean up our cone data.
def _clean_cone_data(varbs, cone):
    clean_varbs = list(varbs)
    clean_cone = cone
    i = 0
    j = 0

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
            for x in f.variables():
                if x in clean_varbs:
                    clean_varbs.remove(x)
            clean_cone = clean_cone[:j] + clean_cone[j + 1:]
        else:
            j += 1
    
    return clean_varbs, clean_cone


# Given cone data and variables, return the corresponding matrix
def _cone_mat(varbs, cone):
    a = len(varbs)
    b = len(cone)
    p = _var('p')
    cone_conditions = [[0 for i in range(a + 1)] for j in range(a + b)]

    # Get the rows corresponding to nonnegative integers
    for i in range(len(varbs)):
        cone_conditions[i][i + 1] = 1

    # Get the rows from the actual cone data
    for i in range(b):
        lhs = cone[i][0]
        rhs = cone[i][1]
        if lhs != 1:
            cone_conditions[a + i][0] -= lhs.degree(p)
            for j in range(len(varbs)):
                cone_conditions[a + i][j + 1] -= lhs.degree(varbs[j])
            if rhs != 1:
                cone_conditions[a + i][0] += rhs.degree(p)
                for j in range(len(varbs)):
                    cone_conditions[a + i][j + 1] += rhs.degree(varbs[j])

    to_tup = lambda x: tuple(x)
    return list(map(to_tup, cone_conditions))


# Given a monomial chart, return its generating function. The output is from 
# Zeta.
def _mono_chart_to_gen_func(C):
    # Clean up the variables and cone data
    c_varbs, c_cone = _clean_cone_data(C.variables, C.cone)
    # Get the matrix of inequalities so Polyhedron can read it
    cone_mat = _cone_mat(c_varbs, c_cone)
    P = _polyhedron(ieqs=cone_mat)

    # Run Zeta
    return P
