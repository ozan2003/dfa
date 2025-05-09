"""
Module containing the Deterministic Finite Automaton (DFA) implementation and related utilities.
"""

from .dfa import Dfa
from .minimize import minimize
from .state import State

__all__ = [
    "Dfa",
    "State",
    "minimize",
]  # Control what is imported when `from dfa import *` is used.
