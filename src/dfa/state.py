from typing import NamedTuple

class State(NamedTuple):
    """
    Represents a state in a finite automaton.
    Attributes:
        name (str): The name of the state.
        is_accepting (bool): Indicates if the state is an accepting state.
    """

    name: str
    is_accepting: bool
