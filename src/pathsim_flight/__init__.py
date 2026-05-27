"""
PathSim-Flight: Flight Dynamics Blocks for PathSim

A toolbox providing specialized blocks for flight dynamics simulations
in the PathSim framework.
"""

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

__all__ = ["__version__"]

# Pure-Python submodules — eager.
from .atmosphere import *  # noqa: F401,F403
from .utils import *  # noqa: F401,F403

# `jsbsim` wraps the native JSBSim Python bindings, which can't load in
# Pyodide. Re-export the wrapper only when the import succeeds; on a normal
# pip install it loads eagerly.
try:
    from .jsbsim import *  # noqa: F401,F403
except ImportError:
    pass
