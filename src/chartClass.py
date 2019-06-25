#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from globalVars import _is_int
from globalVars import _DEFAULT_INDENT as _indent
from globalVars import _DEFAULT_p as _p
from globalVars import _DEFAULT_USER_INPUT as _user_input
from globalVars import _DEFAULT_VERBOSE as _verbose
from integrandClass import MapIntegrand as _map_integrand
from integrandClass import Integrand as _integrand
from integrandClass import _integral_printout
from interfaceZeta import _mono_chart_to_gen_func
from parseSingularExpr import _expr_to_terms
from sage.all import expand as _expand
from sage.all import factor as _factor
from sage.all import Ideal as _ideal
from sage.all import PolynomialRing as _polyring
from sage.all import Set as _set
from sage.all import var as _var
from sage.all import ZZ as _ZZ


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


# Given a list S of polynomials, return a set of variables, as strings, in the 
# set S
def _get_variable_support(S):
    mult = lambda x, y: x*y
    f = reduce(mult, S, 1)
    return {str(x) for x in f.variables()}


# Given an expression expr, units, non_units, and replacements repl, simplify 
# the expression to be monomial in the latest variables.
def _simplify_expr(expr, units, non_units, repl):
    sys_varbs = _get_variable_support(units + non_units)
    p = _var(_p)
    f = expr.factor_list()
    new_factors = []
    # Easier to compare polynomials as strings. This might bite me later.
    conv_to_str = lambda x: str(x)
    sage_int = lambda x: _ZZ.coerce(x)

    # Run through all the factors of expr
    for i in range(len(f)):
        d = f[i][0]
        # First we check that all the variables are contained in the support of 
        # the system. 
        if any(str(x) in sys_varbs for x in d.variables()):
            if str(d) in map(conv_to_str, units):
                # If the factor is a unit, replace it with 1
                new_factors.append(map(sage_int, [1, 1]))
            else:
                if str(d) in map(conv_to_str, non_units):
                    # If the factor is not a unit, replace it with p*z
                    j = non_units.index(d)
                    new_factors.append([p*repl[j], f[i][1]])
                else:
                    # In this case, the factor is neither in the set of units 
                    # nor is it in the set of non_units. **By the assumption 
                    # that this data corresponds to a locally monomial chart**, 
                    # we know this factor is just a unit. Therefore, we just 
                    # replace it with 1. 
                    new_factors.append(map(sage_int, [1, 1]))
        else: 
            new_factors.append([d, f[i][1]])

    # We might need to return a polynomial instead of a factorized polynomial.
    mult = lambda x, y: x*y
    power = lambda x: x[0]**x[1]
    out_poly = reduce(mult, map(power, new_factors), 1)
    return out_poly


# Given the chart, units, non_units, and the replacement variables, construct a 
# new chart from C with the given data.
def _simplify(C, units, non_units, repl, verbose=_verbose):
    # To be used to by 'map'
    _simp_map = lambda x: _simplify_expr(x, units, non_units, repl)

    # First we update the birational map.
    birat = tuple(map(_simp_map, C.birationalMap))

    # We update the cone.
    cone = [tuple(map(_simp_map, ineq)) for ineq in C.cone]

    # Finally we update the Jacobian.
    jacobian = _simp_map(C.jacDet)

    # Now we determine which variables are gone and which remain. 
    flatten = lambda x, y: list(x) + list(y)
    all_polys = list(birat) + reduce(flatten, cone, []) + [jacobian]
    non_const = lambda x: not _is_int(x)
    new_varbs_str = _get_variable_support(filter(non_const, all_polys))
    new_varbs = tuple([_var(x) for x in new_varbs_str if x != _p])

    sub_C = Chart(C.coefficients, new_varbs, # TODO: Need to be careful here!
        atlas = C.atlas,
        biratMap = birat,
        cent = C.cent,
        cone = cone,
        exDivs = C.exDivisors,
        factor = C.ambientFactor,
        focus = C.focus,
        jacDet = jacobian, 
        lastMap = C.lastMap,
        parent = C,
        path = C.path)
    return sub_C


# Given a chart C and a vertex v, construct the (monomial) subchart of C with 
# respect to v. This comes from the intersection lattice of C. 
def _construct_subchart(C, v, verbose=_verbose): 
    if verbose:
        print("%sConstructing the subchart from vertex: %s" % (_indent, v))

    # Get the data
    A = C.AmbientSpace()
    divs = [A.coerce(d) for d in C.intLat.divisors]
    n = len(divs)

    # Even though these are supposed to be sets, there's something about them 
    # that makes them not act like sets. You can only use difference and union 
    # to add or subtract elements...
    units = [divs[k - 1] for k in _set(range(n)).difference(v)]
    non_units = [divs[k - 1] for k in v]
    a = len(non_units)
    b = len(units)
    
    if verbose:
        print("%sUnits: %s" % (_indent*2, units))
        print("%sNon-units: %s" % (_indent*2, non_units))

    # Will replace non_unit[k] with new_varb[k].
    new_varbs = _safe_variables(C.variables, a + b)

    # Replace non_unit[k] with p*repl[k]
    repl = [new_varbs[i] for i in range(a + b)]

    if verbose:
        print("%sApplying the following change of variables:" % (_indent*2))
        add_up = lambda x, y: x + y
        if b > 0:
            dummy_vars = ["a" + str(i) for i in range(b)]
            chg_var_u = lambda x: "%s%s -> %s + %s*%s\n" % (_indent*3, x[0], x[2], _p, x[1])
            print(reduce(add_up, map(chg_var_u, zip(units, repl[a:], dummy_vars)), "")[:-1])
        if a > 0:
            chg_var_nu = lambda x: "%s%s -> %s*%s\n" % (_indent*3, x[0], _p, x[1])
            print(reduce(add_up, map(chg_var_nu, zip(non_units, repl[:a])), "")[:-1])
        

    # Build the subchart
    sub_C = _simplify(C, units, non_units, repl, verbose=verbose)

    # We modify the subchart just slightly. 
    # We give it an id from C
    vert_to_str = lambda x, y: str(x) + str(y)
    sub_C._id = int(str(C._id) + reduce(vert_to_str, v, ''))
    # We multiply by a factor of p
    b = len(_get_variable_support(divs))
    p = _var(_p)
    sub_C.jacDet *= p**b

    if verbose:
        print("%sMultiplying Jacobian by %s" % (_indent*2, p**b))

    return sub_C



class Chart():

    def __init__(self, R, X,
        atlas = None,
        biratMap = None,
        cent = None,
        cone = None,
        exDivs = None,
        factor = None,
        focus = None,
        identity = None,
        intLat = None,
        jacDet = None,
        lastMap = None,
        parent = None,
        path = None): 

        # 'Hidden' attributes
        self._id = identity
        self._parent = parent
        self._subcharts = None
        self._integralFactor = 1

        # 'Public' attributes
        self.coefficients = R
        self.variables = X
        self.atlas = atlas
        self.birationalMap = biratMap
        self.cent = cent
        self.cone = cone
        self.exDivisors = exDivs
        self.ambientFactor = factor
        self.focus = focus
        self.intLat = intLat
        self.jacDet = jacDet
        self.lastMap = lastMap
        self.path = path

        # We make sure the intersection lattice can point back to the chart
        if intLat != None:
            self.intLat.chart = self


    def __repr__(self):
        cat_strings = lambda x, y: x + " " + str(y)
        # Build strings to mimic Singular
        str_coeffs = "coefficients: %s\n" % self.coefficients
        str_num_vars = "number of vars: %s\n" % len(self.variables)
        str_b1_ord = "    block 1: ordering dp\n"
        str_names = "      names:" + reduce(cat_strings, self.variables, "")
        str_b2_ord = "\n    block 2: ordering C"
        
        # Put everything together
        return str_coeffs + str_num_vars + str_b1_ord + str_names + str_b2_ord


    # Decides if the cone data is monomial.
    def IsMonomial(self):
        flatten = lambda x: x[0]*x[1]
        def _is_monomial(x):
            s = str(flatten(x))
            if "+" in s or "-" in s[1:]:
                return False
            return True
        return all(map(_is_monomial, self.cone))


    # Returns the ambient space as a (quotient) polynomial ring.
    def AmbientSpace(self):
        R = _polyring(self.coefficients, self.variables)
        if self.ambientFactor == 0:
            return R
        I = _ideal(R, self.ambientFactor)
        S = R.quotient(I)
        return S


    # If the chart comes from an atlas, then we know how to define the integral 
    # from the root to the chart based on its data. This function will return 
    # the integrand.
    def Integrand(self):
        if self.atlas == None:
            raise ValueError("Chart does not come from an atlas; unsure how to define an integral.")
        return _map_integrand(self.atlas, self)
        

    # Constructs the subcharts based on the intersection lattice.
    def Subcharts(self, recompute=False, verbose=_verbose):
        # If the subcharts have already been computed, then do not do extra 
        # work if we do not need to.
        if not recompute and self._subcharts != None:
            return self._subcharts

        # Construct the set of vertices
        verts = self.intLat.vertices

        # Print statements for the user
        list_polys = lambda x, y: str(x) + ",\n" + _indent + str(y)
        if _verbose:
            print "The intersection lattice contains:"
            print "%s%s vertices," % (_indent, len(verts))
            print "%s%s edges," % (_indent, len(self.intLat.edges))
            print "%s%s divisors." % (_indent, len(self.intLat.divisors))
            print "The divisors are:"
            print "%s%s" % (_indent, reduce(list_polys, self.intLat.divisors))
            print "We construct a subchart for every vertex in the lattice."

        # Visit every vertex and construct a corresponding (monomial) subchart.
        charts = [_construct_subchart(self, v, verbose=verbose) for v in verts]

        if _verbose:
            print "Computing the p-rational points for each vertex in the intersection lattice. "

        # Next we determine the p-rational points on the charts
        _ = self.intLat.pRationalPoints(user_input=_user_input)
        p_rat_pts = self.intLat._vertexToPoints

        # We run through the charts and multiply the integralFactor by the 
        # corresponding p-rational count 
        for i in range(len(verts)):
            charts[i]._integralFactor *= p_rat_pts[i]

        if verbose:
            print "We are verifying that all subcharts are monomial..."
        for i in range(len(charts)):
            C = charts[i]
            if not C.IsMonomial():
                raise AssertionError("We expected these subcharts to be monomial. Something must have gone wrong with subchart associated to vertex %s. If the code is correct, then the original chart is not locally monomial." % (verts[i]))

        self._subcharts = tuple(charts)

        if _verbose:
            print _indent + "Passed."

        return tuple(charts)


    # Compute the integral for the zeta function on this chart
    def ZetaIntegral(self, user_input=_user_input, verbose=_verbose):
        # First decide if the chart is monomial
        if self.IsMonomial():
            subcharts = [self]
        else:
            if _verbose:
                print "Constructing monomial subcharts."

            # First we get the monomial subcharts
            subcharts = self.Subcharts(verbose=verbose)

        if _verbose:
            print "Constructing integral."

        # Now we determine the integrands for each subchart
        build_int = lambda C: _map_integrand(self.atlas, C)
        integrands = map(build_int, subcharts)

        if _verbose:
            print("Solving %s integrals." % (len(integrands)))

        chrt_int = zip(subcharts, integrands)
        gen_funcs = []
        for t in chrt_int:
            _integral_printout(t[0])
            gen_funcs.append(_mono_chart_to_gen_func(t[0], t[1]))

        add_up = lambda x, y: x + y

        return reduce(add_up, gen_funcs, 0)
