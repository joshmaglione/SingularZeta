#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import Set as _set
from sage.all import var as _var
from util import _my_odom

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


# Given the variables of a chart C_varbs and the non-units, return a compatible 
# choice to replace the non-units with variables. 
def _determine_change(C_varbs, non_units, units):
    # Determine which variables in the expressions from non_units get replaced.
    replaced = [False for x in C_varbs] 
    # Our check function
    def _compatible(choice):
        temp = replaced
        for x in choice:
            i = C_varbs.index(x)
            if temp[i] == False:
                temp[i] = True
            else:
                return False
        return True

    # We need to enrich our set of units. For example, if x - 1 = 0 (mod p), 
    # then x is a unit. 
    enriched_units = _set([u for u in units])
    for f in non_units:
        # We add the variables with nonzero support in polynomials of the form 
        # X^a + k = 0, where k != 0.
        if f.number_of_terms() == 2 and f.constant_coefficient() != 0:
            enriched_units.union(_set(f.variables()))

    print (units, enriched_units)
    # I see no reason for these to be "unique," so we proceed as though it is 
    # not. If there happens to be only one choice, then the following code is a 
    # bit unnecessary, but still essentially the same amount of work.
    linears = [[m for m in f.monomials() if m.degree() == 1] for f in non_units]
    # In case there's not an obvious linear
    while any(map(lambda x: len(x) == 0, linears)):
        # In this case, there is no obvious linear term, so we need to look 
        # more carefully at terms that do not appear linear. For example, 
        # something like xy + 1 = 0 (mod p), where both x and y are units. 
        i = linears.index([])
        f = non_units[i] # Problems with uni- vs. multi-variate polynomials!
        candidates = [x for x in f.variables() if f.degree(x) == 1]
        # This shouldn't happen, but just in case...
        if candidates == []:
            raise AssertionError("Cannot find a good variable substitution.")
        # The good variables are the ones where the coeff is a unit.
        good_varbs = []
        for x in candidates:
            coeff = f.coefficient(x).factor()
            facts = [g for g in coeff if g[0] in enriched_units]
            if len(facts) == len(coeff): 
                good_varbs.append(x)
        linears[i] = good_varbs


    # Now proceed to make a choice based on the above data. 
    # Note for future: it seems like there might be a chance that we have to 
    # run through the while loop for all non_units, not just the ones without 
    # an obvious linear term. I think this just amounts to removing the line 
    # with 'i' and replacing the while loop with a for loop. 
    potentials = [len(L) - 1 for L in linears]
    choices = _my_odom(potentials)
    inds = choices.next()
    temp_choice = lambda x: [linears[k][x[k]] for k in range(len(x))]
    while not _compatible(temp_choice(inds)):
        inds = choices.next()

    return temp_choice(inds)


# Given the birational map of a chart, and the relevant data of the new subchart, 'clean' up the birational map: replace units with 1, 
# def _clean_birational(birat, units, non_units, new_varbs):


# Given a chart C and a vertex v, construct the (monomial) subchart of C with 
# respect to v. This comes from the intersection lattice of C. 
def _construct_subchart(C, v): 
    # Get the data
    divs = C.intLat.divisors
    n = len(divs)
    units = tuple([divs[k - 1] for k in _set(range(1, n+1)).difference(v)])
    non_units = tuple([divs[k - 1] for k in v])

    # Will replace non_unit[k] with new_varb[k].
    new_varbs = _safe_variables(C.variables, len(non_units))

    # Get the variables we will replace with the new ones.
    # Incorporating the focus because I don't want to replace a variable in the 
    # focus. I don't think I will be forced to do this, but that's why this 
    # comment is here.
    print v
    repl = _determine_change(C.variables, non_units, units)


    return repl