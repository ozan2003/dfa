"""
A module containing the `DFA` class, which represents a Deterministic Finite Automaton.

The `DFA` class is used to represent a DFA and provides methods for adding states,
transitions, and running the DFA on a string.

Classes:
    DFA: A class representing a Deterministic Finite Automaton (DFA).
"""

from dataclasses import dataclass, field
from typing import Optional

from .state import State


@dataclass
class DFA:
    """
    A class representing a Deterministic Finite Automaton (DFA).

    It is recommended to collect the states in a dictionary and
    pass it to the DFA constructor to avoid cluttering the code.

    Example:
        >>> alphabet = set("01")
        >>> states = {"s0": State("s0", True), "s1": State("s1", False)}

        >>> dfa = DFA(states["s0"], states, alphabet)

    Attributes:
        starting_state (State): The initial state of the DFA.
        states (dict[str, State]): A `dict` mapping states' names to `State` objects.
        alphabet (set[str]): The set of symbols that the DFA can recognize.
        transition_table (dict[State, dict[str, State]]):
            A `dict` mapping states to `dict`s that map symbols to the states they transition.
    """

    starting_state: State
    states: dict[str, State]
    alphabet: set[str]
    transition_table: dict[State, dict[str, State]] = field(
        default_factory=dict
    )  # q0 -> {"sigma" -> q1}

    def __str__(self) -> str:
        def transition_repr(transition: dict[str, State]) -> str:
            return ", ".join(f"{symbol!r} -> {state}" for symbol, state in transition.items())

        table = "\n".join(
            f"\t{from_state}: {transition_repr(transitions)}"
            for from_state, transitions in self.transition_table.items()
        )

        return (
            f"DFA(Starting state: {self.starting_state}, Σ: {self.alphabet}):\n{table}"
        )

    def get_state(self, state_name: str) -> Optional[State]:
        """
        Retrieve the state object associated with the given name.

        Args:
            state_name (str): The name of the `State` to retrieve.

        Returns:
            Optional[State]: The `State` object if found, otherwise `None`.
        """
        return self.states.get(state_name, None)

    def add_state(self, state_name: str, is_accepting: bool = False) -> None:
        """
        Add a new state to the DFA.

        Args:
            state_name (str): The name of the new state.
            is_accepting (bool): Whether the new state is an accepting state.

        Returns:
            None
        """

        self.states[state_name] = State(state_name, is_accepting)

    def add_transition(
        self, from_state_name: str, symbol: str, to_state_name: str
    ) -> None:
        """
        Adds a transition for the given symbol to the specified state.

        Args:
            symbol (str): The symbol for which the transition is being added.
            from_state_name (str): The name of the state from which the transition originates.
            to_state_name(str): The name of the state to which the transition leads to.

        Returns:
            None

        Raises:
            ValueError: If the `symbol` is not in the alphabet,
            or if the `from_state` or `to_state` are not in DFA's states.
        """
        # Check if the symbol is in the alphabet.
        if symbol not in self.alphabet:
            raise ValueError(f"Symbol '{symbol}' not in {self.alphabet}.")

        # Check if the states are in the DFA.
        if from_state_name not in self.states:
            raise ValueError(f"State '{from_state_name}' not in states.")

        if to_state_name not in self.states:
            raise ValueError(f"State '{to_state_name}' not in states.")

        # Check if the same transition from same state for the same symbol already exists.
        # state = self.transition_table.get(self.states[from_state_name])
        if (
            state := self.transition_table.get(self.states[from_state_name])
        ) is not None and state.get(symbol) is not None:
            raise ValueError(
                f"Transition from '{from_state_name}' for the same symbol '{symbol}' already exists."
            )

        # Add the transition to the transition table.
        if self.states[from_state_name] not in self.transition_table:
            self.transition_table[self.states[from_state_name]] = {}

        # Add the symbol to the `from_state`'s transition.
        # self.transition_table[self.states[from_state]][symbol] = self.states[to_state]
        self.transition_table[self.states[from_state_name]].update(
            {symbol: self.states[to_state_name]}
        )

    def run(self, string: str) -> bool:
        """
        Run the DFA on the given string.

        Args:
            string (str): The string to run the DFA on.

        Returns:
            bool: `True` if the DFA accepts the string, `False` otherwise.

        Raises:
            ValueError: If the a symbol in the string is not in the alphabet.
        """
        current_state = self.starting_state

        for symbol in string:
            # Check if the symbol is in the alphabet.
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol '{symbol}' not in alphabet.")

            # Go to the next state, or None if there is no transition.
            current_state = self.transition_table[current_state].get(symbol, None)
            # If the current state is None, the DFA is stuck and the string is not accepted.
            if current_state is None:
                return False
        return current_state.is_accepting

    def __getattr__(self, state_name: str) -> Optional[State]:
        """
        Get a state by name.

        Args:
            name (str): The name of the state to retrieve.

        Returns:
            Optional[State]: The `State` object if found, otherwise `None`.
        """
        return self.get_state(state_name)
