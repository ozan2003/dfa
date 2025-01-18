"""
A module containing the `DFA` class, which represents a Deterministic Finite Automaton.

The `DFA` class is used to represent a DFA and provides methods for adding states,
transitions, and running the DFA on a string.

Classes:
    DFA: A class representing a Deterministic Finite Automaton (DFA).
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import json
from pathlib import Path

from .state import State


@dataclass
class Dfa:
    """
    A class representing a Deterministic Finite Automaton (DFA).

    It is recommended to collect the states in a dictionary and
    pass it to the DFA constructor to avoid cluttering the code.

    Example:
        >>> alphabet = frozenset("01")
        >>> states = {"s0": State("s0", True), "s1": State("s1")}
        >>> transitions = {
        ...     states["s0"]: {"0": states["s0"], "1": states["s1"]},
        ...     states["s1"]: {"0": states["s1"], "1": states["s0"]},
        ... }

        >>> dfa = DFA(states["s0"], states, alphabet, transitions)

    Attributes:
        starting_state (State): The initial state of the DFA.
        states (dict[str, State]): A `dict` mapping states' names to `State` objects.
        alphabet (set[str] | frozenset[str]): The set of symbols that the DFA can recognize.
        transition_table (dict[State, dict[str, State]]):
            A `dict` mapping states to `dict`s that map symbols to the states they transition.
    """

    starting_state: State
    states: dict[str, State]
    alphabet: set[str] | frozenset[str]
    transition_table: dict[State, dict[str, State]] = field(
        default_factory=dict
    )  # q0 -> {"sigma" -> q1}

    def __post_init__(self):
        # Convert alphabet to frozenset for immutability and serializability.
        self.alphabet = frozenset(self.alphabet)

    def __str__(self) -> str:
        def transition_repr(transition: dict[str, State]) -> str:
            return "{{{0}}}".format(
                ", ".join(
                    f"{symbol!r} -> {state}" for symbol, state in transition.items()
                )
            )

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

    def __eq__(self, other: object) -> bool:
        """
        Check if two DFA objects are equivalent by comparing their canonical forms.

        Args:
            other (object): The other DFA to compare with.

        Returns:
            bool: True if the two DFA objects are equivalent, False otherwise.
        """
        if not isinstance(other, Dfa):
            return NotImplemented

        # Step 1: Check if alphabets are the same.
        if self.alphabet != other.alphabet:
            return False

        # Step 2: Canonicalize both DFAs.
        def canonical_form(dfa: Dfa) -> tuple[dict[State, int], dict[int, State]]:
            """
            Computes the canonical form of a given DFA (Deterministic Finite Automaton).

            This function assigns a unique index to each state in the DFA using a breadth-first search (BFS)
            starting from the DFA's starting state.

            Args:
                dfa (DFA): The deterministic finite automaton to be converted to its canonical form.

            Returns:
                tuple[dict[State, int], dict[int, State]]:
                    - state_to_index: A dictionary mapping each state to a unique index.
                    - index_to_state: A dictionary mapping each index back to its corresponding state.
            """
            state_to_index: dict[State, int] = {}
            index_to_state: dict[int, State] = {}
            state_queue: list[State] = [dfa.starting_state]
            visited_states: set[State] = set()

            # BFS to assign indices.
            next_index = 0
            while len(state_queue) > 0:
                state = state_queue.pop(0)
                if state in visited_states:
                    continue
                visited_states.add(state)
                state_to_index[state] = next_index
                index_to_state[next_index] = state
                next_index += 1

                # Enqueue transitions.
                for symbol in dfa.alphabet:
                    if symbol in dfa.transition_table[state]:
                        next_state = dfa.transition_table[state][symbol]

                        if next_state not in visited_states:
                            state_queue.append(next_state)

            return state_to_index, index_to_state

        def get_canonical_transitions(
            dfa: Dfa, state_to_index: dict[State, int]
        ) -> dict[int, dict[str, int]]:
            """
            Generate the canonical transitions for a given DFA.

            Args:
                dfa (DFA): The DFA to generate canonical transitions for.
                state_to_index (dict[State, int]):
                    A mapping from DFA states to their corresponding indices.

            Returns:
                dict[int, dict[str, int]]: A canonical transition table where states
                are represented by their indices.
            """
            canonical_transitions: dict[int, dict[str, int]] = {}

            for state, state_index in state_to_index.items():
                canonical_transitions[state_index] = {
                    symbol: state_to_index[dfa.transition_table[state][symbol]]
                    for symbol in dfa.alphabet
                    if symbol in dfa.transition_table[state]
                }

            return canonical_transitions

        state_to_index_self, _ = canonical_form(self)
        state_to_index_other, _ = canonical_form(other)

        # Step 3: Compare canonical forms
        if len(state_to_index_self) != len(state_to_index_other):
            return False

        # Compare transition tables.
        canonical_transitions_of_self = get_canonical_transitions(
            self, state_to_index_self
        )
        canonical_transitions_of_other = get_canonical_transitions(
            other, state_to_index_other
        )

        if canonical_transitions_of_self != canonical_transitions_of_other:
            return False

        # Compare accepting states.
        accepting_states_of_self = {
            index for state, index in state_to_index_self.items() if state.is_accepting
        }
        accepting_states_of_other = {
            index for state, index in state_to_index_other.items() if state.is_accepting
        }

        return accepting_states_of_self == accepting_states_of_other

    def dump_json(self, path: Path) -> None:
        """
        Dump the DFA object to a JSON file.

        Args:
            path (Path): The path to the JSON file.

        Returns:
            None
        """
        # Convert the DFA to a serializable dictionary
        dfa_dict: dict[str, Any] = {
            "starting_state": self.starting_state.name,  # Just store the name
            "states": {
                name: {"name": state.name, "is_accepting": state.is_accepting}
                for name, state in self.states.items()
            },
            "alphabet": tuple(self.alphabet),  # Convert set to tuple for serialization
            "transition_table": {
                from_state.name: {  # Use state names as keys
                    symbol: to_state.name  # Store state names instead of State objects
                    for symbol, to_state in transitions.items()
                }
                for from_state, transitions in self.transition_table.items()
            },
        }
        # json.dump(dfa_dict, path.open("w"), indent=2)
        with path.open("w") as file:
            json.dump(dfa_dict, file, indent=2)

    @classmethod
    def from_json(cls, path: Path) -> "Dfa":
        """
        Load the DFA object from a JSON file.

        Args:
            path (Path): The path to the JSON file.

        Returns:
            Dfa: The DFA object loaded from the JSON file.
        """
        with path.open("r") as file:
            data = json.load(file)

        # First recreate all states
        states = {
            name: State(state_data["name"], state_data["is_accepting"])
            for name, state_data in data["states"].items()
        }

        # Reconstruct transition table using the recreated states
        transition_table: dict[State, dict[str, State]] = {}
        for from_state_name, transitions in data["transition_table"].items():
            from_state = states[from_state_name]
            transition_table[from_state] = {
                symbol: states[to_state_name]
                for symbol, to_state_name in transitions.items()
            }

        return cls(
            starting_state=states[data["starting_state"]],
            states=states,
            alphabet=set(data["alphabet"]),
            transition_table=transition_table,
        )
