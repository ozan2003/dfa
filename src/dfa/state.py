"""
This module contains the `State` class which used for representing states in a finite automaton.
"""

from typing import NamedTuple

class State(NamedTuple):
    """
    Represents a state in a finite automaton.
    The states own their name and whether they are accepting states.
    
    Attributes:
        name (str): The name of the state.
        is_accepting (bool): Indicates if the state is an accepting state.
    """

    name: str
    is_accepting: bool
