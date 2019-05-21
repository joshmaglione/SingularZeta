#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

# from globalVars import _is_int
from sage.all import Set as _set
from chartClass import Chart as _chart
from sage.all import var as _var
# from util import _my_odom

# Given a list of variables and an integer n, return an n-tuple of new, safe 
# variables.
def _safe_variables(varbs, n):
    i = 1
    letter = 'z'
    varbs_str = {str(x) for x in varbs}
    new_varbs = []
    for k in range(n):
        if not letter + str(i) in varbs_str:
            new_varbs.append(_var(letter + str(i)))
        i += 1
    return tuple(new_varbs)


# # Given the non_units, units, and an expression to test, determine if test is a 
# # unit or not.
# def _is_unit(non_units, units, test):
#     # It is far easier to test if an expression is in a set or not, so we build 
#     # an "enriched" set of units. It seems for many examples, this is enough.
#     enriched_units = [u for u in units]
#     for f in non_units:
#         # We add the variables with nonzero support in polynomials of the form 
#         # X^a + k = 0, where k != 0.
#         if f.number_of_terms() == 2 and f.constant_coefficient() != 0:
#             for x in f.variables():
#                 if not x in enriched_units:
#                     enriched_units.append(x)

#     # Quick test
#     if test in enriched_units: 
#         return True
#     if test in non_units:
#         return False

#     # This tests when a monomial is a unit or not. 
#     def _test_monos(m):
#         if _is_int(m):
#             return True
#         varbs = list(m.variables())
#         in_units = lambda x : x in enriched_units
#         return all(map(in_units, varbs))

#     # Break the polynomial up into monomials. If there is exactly one term that 
#     # is a unit, then it returns True. If none of the terms are units, then it 
#     # returns false. 
#     monos = test.monomials()
#     mono_unit = map(_test_monos, monos)
#     if any(mono_unit):
#         if list(mono_unit).count(True) == 1:
#             return True
#     else:
#         return False

#     # We just ask the user
#     print "Here's what I know:"
#     print "    Units: %s" % (enriched_units)
#     print "    Non-units: %s" % (non_units)
#     print "Is this a unit: "
#     print "    %s" % (test)
#     nahs = {_var('n'), _var('N')} # Still needs to be defined.... eyeroll
#     yays = {_var('y'), _var('Y')}
#     y_or_n = input("Y/N? ")
#     return y_or_n in yays



# # Given the ambient space A, variables of a chart C_varbs, the non-units, and 
# # the units, return a compatible choice to replace the non-units with 
# # variables. 
# def _determine_change(C_varbs, non_units, units):
#     # Our check function
#     def _compatible(choice):
#         temp = [False for x in C_varbs] 
#         for x in choice:
#             i = C_varbs.index(x)
#             if temp[i] == False:
#                 temp[i] = True
#             else:
#                 return False
#         return True

#     # Define them locally so we can add to them as we learn
#     enriched_units = units
#     enriched_non_units = non_units

#     # I see no reason for these to be "unique," so we proceed as though it is 
#     # not. If there happens to be only one choice, then the following code is a 
#     # bit unnecessary, but still essentially the same amount of work.
#     linears = [[] for f in non_units]
#     # In case there's not an obvious linear
#     for i in range(len(linears)):
#         # In this case, there is no obvious linear term, so we need to look 
#         # more carefully at terms that do not appear linear. For example, 
#         # something like xy + 1 = 0 (mod p), where both x and y are units. 
#         f = non_units[i] 
#         # Problems with uni- vs. multi-variate polynomials!
#         if len(f.variables()) == 1:
#             candidates = [x for x in f.variables() if f.degree() == 1]
#             linears[i] = candidates
#         else:
#             candidates = [x for x in f.variables() if f.degree(x) == 1]
#             # This shouldn't happen, but just in case...
#             if candidates == []:
#                 raise AssertionError("Cannot find a good variable substitution because there is no variable of degree 1.")
#             # The good variables are the ones where the coeff is a unit.
#             good_varbs = []
#             for x in candidates:
#                 coeff = f.coefficient(x).factor()
#                 facts = []
#                 # Going to test if g is a unit or not, and we are going to 
#                 # learn from this test.
#                 for g in coeff:
#                     if _is_unit(enriched_non_units, enriched_units, g[0]):
#                         facts.append(g)
#                         if not g[0] in enriched_units:
#                             enriched_units.append(g[0])
#                     else:
#                         if not g[0] in enriched_non_units:
#                             enriched_non_units.append(g[0])
#                 if len(facts) == len(coeff): 
#                     good_varbs.append(x)
#             linears[i] = good_varbs

#     # Now proceed to make a choice based on the above data. 
#     potentials = [len(L) - 1 for L in linears]
#     if -1 in potentials:
#         raise AssertionError("Could not determine a valid change of variables because there were no potential choices.")
#     choices = _my_odom(potentials)
#     inds = choices.next()
#     temp_choice = lambda x: [linears[k][x[k]] for k in range(len(x))]
#     while not _compatible(temp_choice(inds)):
#         try:
#             inds = choices.next()
#         except StopIteration:
#             raise StopIteration("Could not determine a valid change of variables among the potential choices.")

#     return temp_choice(inds)


# Given the birational map of a chart, and the relevant data of the new subchart, 'clean' up the birational map: replace units with 1, 
# def _clean_birational(birat, units, non_units, new_varbs):


# # Given a chart C and a vertex v, construct the (monomial) subchart of C with 
# # respect to v. This comes from the intersection lattice of C. 
# def _construct_subchart(C, v): 
#     # Get the data
#     A = C.AmbientSpace()
#     divs = [A.coerce(d) for d in C.intLat.divisors]
#     n = len(divs)

#     # Even though these are supposed to be sets, there's something about them 
#     # that makes them not act like sets. You can only use difference and union 
#     # to add or subtract elements...
#     units = [divs[k - 1] for k in _set(range(1, n+1)).difference(v)]
#     non_units = [divs[k - 1] for k in v]

#     # Will replace non_unit[k] with new_varb[k].
#     new_varbs = _safe_variables(C.variables, len(non_units))
#     print v
#     # Get the variables we will replace with the new ones.
#     repl = _determine_change(C.variables, non_units, units)


#     return repl

# Given an expression expr, units, non_units, and replacements repl, simplify 
# the expression to be monomial in the latest variables.
def _simplify_expr(expr, units, non_units, repl):
    p = _var('p')
    f = expr.factor()
    # Run through all the factors of expr
    for i in range(len(f)):
        d = f[i][0]
        if d in units:
            # If the factor is a unit, replace it with 1
            f[i][0] = 1
        else:
            # If the factor is not a unit, replace it with p*z
            if d in non_units:
                j = non_units.index(d)
                f[i][0] = p*repl[j]
            else:
                raise AssertionError("When doing a variable substitution, expected a factor to be in the set of units or non-units. Is the intersection lattice compatible with the chart?")
    # We might need to return a polynomial instead of a factorized polynomial.
    return f

# Given the chart, units, non_units, and the replacement variables, construct a 
# new chart from C with the given data.
def _simplify(C, units, non_units, repl):
    # To be used to by 'map'
    _simp_map = lambda x: _simplify_expr(x, units, non_units, repl)

    # First we update the birational map.
    birat = tuple(map(_simp_map, C.biratMap))

    # We update the cone.
    cone = [tuple(map(_simp_map, ineq)) for ineq in C.cone]

    # Finally we update the Jacobian.
    jacobian = _simp_map(C.jacDet)

    # Now we determine which variables are gone and which remain. 
    new_varbs = []
    app_to_list = lambda x: new_varbs.extend(list(x.variables()))
    _ = map(app_to_list, birat)
    _ = [tuple(map(_simp_map, ineq)) for ineq in cone]
    _ = app_to_list(jacobian)
    

    sub_C = _chart(C.coefficient, new_varbs, 
        atlas = C.atlas,
        biratMap = birat,
        cent = C.cent,
        cone = cone,
        exDivs = C.exDivs,
        factor = C.factor,
        focus = C.focus,
        jacDet = jacobian, 
        lastMap = C.lastMap,
        parent = C,
        path = C.path)
    return sub_C


# Given a chart C and a vertex v, construct the (monomial) subchart of C with 
# respect to v. This comes from the intersection lattice of C. 
def _construct_subchart(C, v): 
    # Get the data
    A = C.AmbientSpace()
    divs = [A.coerce(d) for d in C.intLat.divisors]
    n = len(divs)

    # Even though these are supposed to be sets, there's something about them 
    # that makes them not act like sets. You can only use difference and union 
    # to add or subtract elements...
    units = [divs[k - 1] for k in _set(range(1, n+1)).difference(v)]
    non_units = [divs[k - 1] for k in v]

    # Determine the variables in the divs.
    varbs = {x for d in divs for x in d.variables()}
    a = min(n, len(varbs))

    # Will replace non_unit[k] with new_varb[k].
    new_varbs = _safe_variables(C.variables, a)

    # Replace non_unit[k] with p*repl[k]
    repl = [new_varbs[i] for i in range(len(non_units))]

    # Build the subchart
    sub_C = _simplify(C, units, non_units, repl)

    # We modify the subchart just slightly. 
    # We give it an id from C
    vert_to_str = lambda x, y: str(x) + y
    sub_C._id = int(str(C._id) + reduce(vert_to_str, v, ''))
    # We multiply by a factor of p
    rem = a - len(new_varbs)

    return sub_C
