#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#


__version__ = 0.1

print("Loading...")

# === This is very annoying during development =================================
import sys
sys.dont_write_bytecode = True
# ==============================================================================

# 'from foo import *' leaves hidden functions hidden and brings it up to 
# TensorSpace instead of TensorSpace.src

# Start a Singular run
from sage.all import singular as _singular
_ = _singular.eval("1 + 1;")

# Load interface
from src.interfaceSing import *
from src.ringClass import *
from src.parseSingularBasics import _parse_list as parseList #REMOVE
from src.parseSingularExpr import _expr_to_terms as exprToTerms #REMOVE

# Sage is still on python2.
print "RSSage %s loaded." % (__version__)