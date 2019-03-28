#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#


__version__ = 0.1

print("Loading...")

# === This is very annoying during development =================================
import sys as _sys
_sys.dont_write_bytecode = True
# ==============================================================================

# Enables us to turn off printing.
from os import devnull as _DEVNULL
import sys as _sys
class _HiddenPrints:
    def __enter__(self):
        self._original_stdout = _sys.stdout
        _sys.stdout = open(_DEVNULL, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        _sys.stdout.close()
        _sys.stdout = self._original_stdout


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
            # TODO: EVENTUALLY SPECIFY.
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
del Zeta_ver

# 'from foo import *' leaves hidden functions hidden and brings it up to 
# TensorSpace instead of TensorSpace.src
# Load interface
from src.interfaceSing import *
from src.ringClass import *
from src.parseEdges import * # REMOVE

# Sage is still on python2.
print "RSSage %s loaded." % (__version__)