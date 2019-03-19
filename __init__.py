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

# Load interface
from src.interfaceSing import *
from src.ringClass import *

# Sage is still on python2.
print "RSSage %s loaded." % (__version__)