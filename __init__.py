#
#   Copyright 2020 Joshua Maglione 
#
#   Distributed under MIT License
#


__version__ = 1.0

print("Loading...")

# Load the global variables that the user can change.  
from src.globalVars import _DEFAULT_INDENT as _indent
from src.globalVars import _DEFAULT_LOAD_DB as _load
from src.globalVars import _DEFAULT_p as _p
from src.globalVars import _DEFAULT_t as _t
from src.globalVars import _DEFAULT_USER_INPUT as _user_input
from src.globalVars import _DEFAULT_VERBOSE as _verbose

if not isinstance(_indent, str):
    raise TypeError("Global variable '_DEFAULT_INDENT' must be a string.")

if not isinstance(_load, bool):
    raise TypeError("Global variable '_DEFAULT_LOAD_DB' must be set to boolean: True or False.")

if not isinstance(_p, str):
    raise TypeError("Global variable '_DEFAULT_p' must be a string.")

if not isinstance(_t, str):
    raise TypeError("Global variable '_DEFAULT_t' must be a string.")

if not isinstance(_user_input, bool):
    raise TypeError("Global variable '_DEFAULT_USER_INPUT' must be set to boolean: True or False.")

if not isinstance(_verbose, int):
    raise TypeError("Global variable '_DEFAULT_VERBOSE' must be set to an integer: True or False.")
    

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
print(_indent + "Loading Singular.")
from sage.all import singular as _singular
_ = _singular.eval("1 + 1;")

# See if Zeta is already imported.
print(_indent + "Loading Zeta.")
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
        print(_indent*2 + "Something unexpected went wrong while loading Zeta.")
except:
    print(_indent*2 + "Something unexpected went wrong while looking for Zeta.")


# Report what we know
if Zeta_ver:
    print(_indent*2 + "Found Zeta version %s." % (Zeta.__version__))
else:
    print(_indent*2 + "Could not find Zeta! Most functions unavailable.")
    print(_indent*2 + "Zeta url: http://www.maths.nuigalway.ie/~rossmann/Zeta/")
del Zeta_ver


# 'from foo import *' leaves hidden functions hidden and brings it up to 
# foo instead of foo.src
print(_indent + "Importing functions.")
from src.atlasClass import *
from src.atlasReport import *
from src.chartClass import *
from src.integrandClass import *
from src.interfaceSingular import *
from src.intLatticeClass import *
from src.localZFTest import *
from src.propertyTests import *


print(_indent + "User defined default settings:")
print(_indent*2 + "Load database: %s" % (_load))
print(_indent*2 + "User input: %s" % (_user_input))
print(_indent*2 + "Variable names: %s" % ([_p, _t]))
print(_indent*2 + "Verbose level: %s" % (_verbose))

print("SingularZeta v%s loaded." % (__version__))