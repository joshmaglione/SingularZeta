#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#

from sage.all import QQ as _QQ
from sage.all import ZZ as _ZZ
from sage.all import var as _var
from parseSingularExpr import _expr_to_tup, _format_var


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
    str_vars_form = _format_var(str_vars).split(" ")
    varbs = [_var(s) for s in str_vars_form]
    return tuple(varbs)


# Assumed to be just the Singluar printout of the ring.
def _parse_printout(printout):
    coeff = _parse_coeff(_attr_value(printout, "coefficients"))
    varbs = _parse_vars(_attr_value(printout, "names"))
    return (coeff, varbs)


# Given list of lines of a Singular printout of a list, create a tuple whose 
# entries are the strings in the given list. Note that sing_list is assumed to essentially be a singular list split by '\n'
def _parse_list(sing_list):
    # Singular indents with 3 spaces.
    indent = 3

    # If it is not a list, just return it. This is the "base" case.
    if not "[1]:" in sing_list[0]:
        one_line = reduce(lambda x, y: x + y, sing_list, "")
        return _expr_to_tup(one_line)

    # Now we recurse.
    L = []
    i = 0
    while i < len(sing_list):
        if "[" == sing_list[i][0]:
            i += 1
            j = i + 1
            while j < len(sing_list) and sing_list[j][:indent] == " "*indent: 
                j += 1
            # Remove the indent and recurse.
            sub_list = map(lambda x: x[indent:], sing_list[i:j])
            L.append(_parse_list(sub_list))
        else:
            raise AssertionError("Wasn't expecting to be here...")
        # i is either the next line starting with [n]: or i is too large.
        i = j
    
    return L
