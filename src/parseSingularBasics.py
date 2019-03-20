#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import QQ as _QQ
from sage.all import ZZ as _ZZ
from sage.all import var as _var


def _attr_value(printout, attr):
    start = printout.rindex(attr)
    p_out = printout[start:]
    end = p_out.index("\n")
    exerpt = p_out[:end]
    space = exerpt.index(" ")
    result = exerpt[space + 1:]

    # The "names" attr is formatted in a strange way.
    # This while loop will fix it.
    while len(result) > 0 and result[0] == " ":
        result = result[1:]

    return result

# Assumed just the Singular printout of the coefficient ring.
def _parse_coeff(str_coeff):
    if str_coeff == "QQ":
        return _QQ
    elif str_coeff == "ZZ":
        return _ZZ
    elif "ZZ/" in str_coeff:
        n = _ZZ.coerce(int(str_coeff.replace("ZZ/", "")))
        return _ZZ.quo(n)
    else:
        raise ValueError("Unknown Singular ring.")

# Assumed variables are separated by white space.
def _parse_vars(str_vars):
    str_vars_form = str_vars.replace("(", "").replace(")", "").split(" ")
    varbs = [_var(s) for s in str_vars_form]
    return tuple(varbs)

# Assumed to be just the Singluar printout of the ring.
def _parse_printout(printout):
    coeff = _parse_coeff(_attr_value(printout, "coefficients"))
    varbs = _parse_vars(_attr_value(printout, "names"))
    return (coeff, varbs)
