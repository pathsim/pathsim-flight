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
