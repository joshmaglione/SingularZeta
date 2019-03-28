#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#


__version__ = 0.1

print("Loading...")

# === This is very annoying during development =================================
import sys, os
sys.dont_write_bytecode = True
# ==============================================================================

# Enables us to turn off printing.
class _HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


# Start a Singular run
from sage.all import singular as _singular
_ = _singular.eval("1 + 1;")


# See if Zeta is already imported.
try:
    Zeta_ver = isinstance(Zeta.__version__, str)
except NameError:
    try: 
        # This just turns off printing because the Zeta banner always comes up.
        with _HiddenPrints():
            import Zeta
        Zeta_ver = isinstance(Zeta.__version__, str)
    except ImportError:
        Zeta_ver = False
    except:
        print "Something unexpected went wrong while loading Zeta."
except:
    print "Something unexpected went wrong while looking for Zeta."


# Report what we know
if Zeta_ver:
    print "    Found Zeta version %s." % (Zeta.__version__)
else:
    print "    Could not find Zeta! Most functions unavailable."
    print "    Zeta url: http://www.maths.nuigalway.ie/~rossmann/Zeta/"


# 'from foo import *' leaves hidden functions hidden and brings it up to 
# TensorSpace instead of TensorSpace.src
# Load interface
from src.interfaceSing import *
from src.ringClass import *
from src.parseSingularBasics import _parse_list as parseList #REMOVE
from src.parseSingularExpr import _expr_to_terms as exprToTerms #REMOVE


# Sage is still on python2.
print "RSSage %s loaded." % (__version__)