#
#   Copyright 2019 Joshua Maglione 
#
#   Distributed under MIT License
#


__version__ = 0.5

print "Loading..."


from src.globalVars import _DEFAULT_INDENT as _indent
from src.globalVars import _DEFAULT_VERBOSE as _verbose

# Load the global variables that the user can change.  
if not isinstance(_indent, str):
    raise TypeError("Global variable '_DEFAULT_INDENT' must be a string.")

if not isinstance(_verbose, bool):
    raise TypeError("Global variable '_DEFAULT_VERBOSE' must be set to boolean: True or False.")
    

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


# ------------------------------------------------------------------------------
#   We front-load some functions so that the initial call after loading the 
#   SingularZeta is not slow. 
# ------------------------------------------------------------------------------
# Start a Singular run
print _indent + "Loading Singular."
from sage.all import singular as _singular
_ = _singular.eval("1 + 1;")


# Is this needed??????????????????????????????????????
# Load up the 'roots' command
print _indent + "Loading Sage functions."
from sage.all import var as _var
_ = _var('x')


# See if Zeta is already imported.
print _indent + "Loading Zeta."
try:
    Zeta_ver = isinstance(Zeta.__version__, str)
except NameError:
    try: 
        # This just turns off printing because the Zeta banner always comes up.
        with _HiddenPrints():
            # TODO: Eventually specify what we need.
            import Zeta 
        Zeta_ver = isinstance(Zeta.__version__, str)
    except ImportError:
        Zeta_ver = False
    except:
        print _indent*2 + "Something unexpected went wrong while loading Zeta."
except:
    print _indent*2 + "Something unexpected went wrong while looking for Zeta."


# Report what we know
if Zeta_ver:
    print _indent*2 + "Found Zeta version %s." % (Zeta.__version__)
else:
    print _indent*2 + "Could not find Zeta! Most functions unavailable."
    print _indent*2 + "Zeta url: http://www.maths.nuigalway.ie/~rossmann/Zeta/"
del Zeta_ver


# 'from foo import *' leaves hidden functions hidden and brings it up to 
# foo instead of foo.src
print _indent + "Importing functions."
from src.atlasClass import *
from src.chartClass import *
from src.integrandClass import *
from src.interfaceSingular import *
from src.intLatticeClass import *
from src.chartClass import _construct_subchart


# Verify verbose printing
if _verbose:
        print _indent + "Verbose printing turned on."


# Sage is still on python2.
print "SingularZeta %s loaded." % (__version__)