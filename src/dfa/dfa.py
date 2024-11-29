from dataclasses import dataclass, field
from typing import Optional

from src.dfa.state import State


@dataclass
class DFA:
    """
    A class representing a Deterministic Finite Automaton (DFA).
    Attributes:
        starting_state (State): The initial state of the DFA.
        states (dict[str, State]): A dictionary mapping state names to State objects.
        alphabet (set[str]): The set of symbols that the DFA can recognize.
        transition_table (dict[State, dict[str, State]]): A dictionary mapping states to dictionaries that map symbols to the states they transition.
    Methods:
        __str__() -> str:
            Returns a string representation of the DFA.
        get_state(name: str) -> Optional[State]:
        add_state(state: State) -> None:
        run(string: str) -> bool:
        __getattr__(name: str) -> Optional[State]:
    """

    starting_state: State
    states: dict[str, State]
    alphabet: set[str]
    transition_table: dict[State, dict[str, State]] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"DFA({self.starting_state}, {self.alphabet}, {self.states})"

    def get_state(self, state_name: str) -> Optional[State]:
        """
        Retrieve the state object associated with the given name.

        Args:
            name (str): The name of the state to retrieve.

        Returns:
            Optional[State]: The state object if found, otherwise None.
        """
        if state_name in self.states:
            return self.states[state_name]
        else:
            return None

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

    def add_transition(self, from_state: str, symbol: str, to_state: str) -> None:
        """
        Adds a transition for the given symbol to the specified state.

        Args:
            symbol (str): The symbol for which the transition is being added.
            from_state (str): The name of the state from which the transition originates.
            to_state (str): The name of the state to which the transition leads.

        Returns:
            None
        """

        if symbol not in self.alphabet:
            raise ValueError(f"Symbol '{symbol}' not in alphabet.")

        if from_state not in self.states:
            raise ValueError(f"State '{from_state}' not in states.")

        if to_state not in self.states:
            raise ValueError(f"State '{to_state}' not in states.")

        if self.states[from_state] not in self.transition_table:
            self.transition_table[self.states[from_state]] = {}
            
        self.transition_table[self.states[from_state]][symbol] = self.states[to_state]

    def run(self, string: str) -> bool:
        """
        Run the DFA on the given string.

        :param string: The string to run the DFA on.
        :return: True if the DFA accepts the string, False otherwise.
        """
        current_state = self.starting_state
        for symbol in string:
            # Check if the symbol is in the alphabet.
            if symbol not in self.alphabet:
                raise ValueError(f"Symbol '{symbol}' not in alphabet.")

            # current_state = current_state.get_state(symbol)
            current_state = self.transition_table[current_state].get(symbol, None) # Go to the next state.
            # If the current state is None, the DFA is stuck and the string is not accepted.
            if current_state is None:
                return False
        return current_state.is_accepting

    def __getattr__(self, name: str) -> Optional[State]:
        """
        Get a state by name.

        :param name: The name of the state.
        :return: The state with the given name, or None if it does not exist.
        """
        return self.get_state(name)
