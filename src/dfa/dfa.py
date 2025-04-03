"""
A module containing the `DFA` class, which represents a Deterministic Finite Automaton.

The `DFA` class is used to represent a DFA and provides methods for adding states,
transitions, and running the DFA on a string.

Classes:
    DFA: A class representing a Deterministic Finite Automaton (DFA).
"""

# ruff: noqa: FA102, FA100

import json
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

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
            return "{{{}}}".format(
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
            msg = f"Symbol '{symbol}' not in {self.alphabet}."
            raise ValueError(msg)

        # Check if the states are in the DFA.
        if from_state_name not in self.states:
            msg = f"State '{from_state_name}' not in states."
            raise ValueError(msg)

        if to_state_name not in self.states:
            msg = f"State '{to_state_name}' not in states."
            raise ValueError(msg)

        # Check if the same transition from same state for the same symbol already exists.
        if (
            state := self.transition_table.get(self.states[from_state_name])
        ) is not None and state.get(symbol) is not None:
            msg = f"Transition from '{from_state_name}' for the same symbol '{symbol}' already exists."
            raise ValueError(msg)

        # Add the transition to the transition table.
        if self.states[from_state_name] not in self.transition_table:
            self.transition_table[self.states[from_state_name]] = {}

        # Add the symbol to the `from_state`'s transition.
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
                msg = f"Symbol '{symbol}' not in alphabet."
                raise ValueError(msg)

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
            state_name (str): The name of the state to retrieve.

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
        def canonical_form(
            dfa: Dfa,
        ) -> dict[State, int]:  # tuple[dict[State, int], dict[int, State]]:
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
            # index_to_state: dict[int, State] = {}  # noqa: ERA001
            state_queue: deque[State] = deque([dfa.starting_state])
            visited_states: set[State] = set()

            # BFS to assign indices.
            next_index = 0
            while len(state_queue) > 0:
                state = state_queue.popleft()
                if state in visited_states:
                    continue
                visited_states.add(state)
                state_to_index[state] = next_index
                # index_to_state[next_index] = state  # noqa: ERA001
                next_index += 1

                # Enqueue transitions.
                for symbol in dfa.alphabet:
                    if symbol in dfa.transition_table[state]:
                        next_state = dfa.transition_table[state][symbol]

                        if next_state not in visited_states:
                            state_queue.append(next_state)

            return state_to_index  # , index_to_state

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

        # state_to_index_self, _ = canonical_form(self)  # noqa: ERA001
        # state_to_index_other, _ = canonical_form(other)  # noqa: ERA001
        state_to_index_self = canonical_form(self)
        state_to_index_other = canonical_form(other)

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

    def __bin_op(self, other: "Dfa", op: Callable[[State, State], bool]) -> "Dfa":
        """
        Helper generic function to perform binary operations on two DFAs.

        Args:
            other (Dfa): The other DFA to perform the operation with.
            op (Callable[[State, State], bool]): The binary operation to perform on the states.

        Returns:
            Dfa: The resulting DFA after the binary operation.

        Raises:
            ValueError: If the alphabets of the two DFAs are not the same.

        """
        if self.alphabet != other.alphabet:
            msg = "Alphabets of the two DFAs are not the same."
            raise ValueError(msg)

        new_states: dict[str, State] = {}

        def make_state_name(q1: State, q2: State) -> str:
            """
            Function to generate state names and maintain consistent naming.

            Args:
                q1 (State): The first state.
                q2 (State): The second state.

            Returns:
                str: The name of the state. Format: (q1.name,q2.name)

            """
            return f"({q1.name},{q2.name})"

        # Create the starting state.
        start_state_name = make_state_name(self.starting_state, other.starting_state)
        start_state = State(
            start_state_name,
            op(self.starting_state, other.starting_state),
        )
        new_states[start_state_name] = start_state

        # Initialize the work queue with unprocessed state pairs.
        unprocessed_pairs: deque[tuple[State, State]] = deque(
            [(self.starting_state, other.starting_state)]
        )
        processed_pairs: set[tuple[State, State]] = set()

        # Initialize the transition table for the new DFA.
        new_transitions: dict[State, dict[str, State]] = {}

        # Process all reachable state pairs.
        while unprocessed_pairs:
            current_q1, current_q2 = unprocessed_pairs.popleft()
            if (current_q1, current_q2) in processed_pairs:
                continue

            processed_pairs.add((current_q1, current_q2))

            current_state_name = make_state_name(current_q1, current_q2)
            current_state = new_states[current_state_name]

            # Initialize transitions for current state.
            new_transitions[current_state] = {}

            # For each symbol in the alphabet...
            for symbol in self.alphabet:
                # Only process if both DFAs have transitions for this symbol.
                if (
                    symbol in self.transition_table[current_q1]
                    and symbol in other.transition_table[current_q2]
                ):
                    # Get next states in both DFAs.
                    next_q1 = self.transition_table[current_q1][symbol]
                    next_q2 = other.transition_table[current_q2][symbol]

                    # Create new state name for the pair.
                    next_state_name = make_state_name(next_q1, next_q2)

                    # Create new state if we haven't seen it before.
                    if next_state_name not in new_states:
                        new_states[next_state_name] = State(
                            next_state_name,
                            op(next_q1, next_q2),
                        )
                        unprocessed_pairs.append((next_q1, next_q2))

                    # Add transition.
                    new_transitions[current_state][symbol] = new_states[next_state_name]

        return Dfa(
            starting_state=start_state,
            states=new_states,
            alphabet=self.alphabet,
            transition_table=new_transitions,
        )

    def intersection(self, other: "Dfa") -> "Dfa":
        """
        Compute the intersection of two DFAs using product construction.

        Args:
            other (Dfa): The other DFA to intersect with.

        Returns:
            Dfa: The DFA resulting from the intersection of the two DFAs.

        Raises:
            ValueError: If the alphabets of the two DFAs are not the same.

        """
        return self.__bin_op(other, lambda q1, q2: q1.is_accepting and q2.is_accepting)

    def __and__(self, other: "Dfa") -> "Dfa":
        """
        Shorthand for the `intersection` method.
        """
        return self.intersection(other)

    def __rand__(self, other: "Dfa") -> "Dfa":
        return self & other

    def union(self, other: "Dfa") -> "Dfa":
        """
        Compute the union of two DFAs using product construction.

        Args:
            other (Dfa): The other DFA to union with.

        Returns:
            Dfa: The DFA resulting from the union of the two DFAs.

        Raises:
            ValueError: If the alphabets of the two DFAs are not the same.

        """
        return self.__bin_op(other, lambda q1, q2: q1.is_accepting or q2.is_accepting)

    def __or__(self, other: "Dfa") -> "Dfa":
        """
        Shorthand for the `union` method.
        """
        return self.union(other)

    def __ror__(self, other: "Dfa") -> "Dfa":
        return self | other

    def set_difference(self, other: "Dfa") -> "Dfa":
        """
        Compute the set difference of two DFAs using product construction.

        Args:
            other (Dfa): The other DFA to compute the set difference with.

        Returns:
            Dfa: The DFA resulting from the set difference of the two DFAs.

        Raises:
            ValueError: If the alphabets of the two DFAs are not the same.

        """
        return self.__bin_op(
            other, lambda q1, q2: q1.is_accepting and not q2.is_accepting
        )

    def __sub__(self, other: "Dfa") -> "Dfa":
        """
        Shorthand for the `set_difference` method.
        """
        return self.set_difference(other)

    def __rsub__(self, other: "Dfa") -> "Dfa":
        return self - other
