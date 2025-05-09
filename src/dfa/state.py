"""
Module containing the `State` class for representing states in a finite automaton.
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
    is_accepting: bool = False

    def __str__(self) -> str:
        is_accepting_mark = "✓" if self.is_accepting else "✗"
        return f"{self.name} ({is_accepting_mark})"
