"""
This is the implementation file of DFA minimization algorithm.
"""

from typing import Optional
from .dfa import DFA
from .state import State


def minimize(dfa: DFA) -> DFA:
    """
    Minimize the DFA.
    The algorithm used here is the Hopcroft's algorithm[1].
    https://swaminathanj.github.io/fsm/dfaminimization.html

    [1]: https://en.wikipedia.org/wiki/DFA_minimization#Hopcroft's_algorithm

    Args:
        dfa (DFA): The DFA to be minimized.

    Returns:
        DFA: The minimized DFA.
    """
    # Step 1: Initial partition of states into accepting and non-accepting states.
    accepting_states: set[State] = {
        state for state in dfa.states.values() if state.is_accepting
    }
    non_accepting_states: set[State] = {
        state for state in dfa.states.values() if not state.is_accepting
    }
    state_partition: list[set[State]] = [accepting_states, non_accepting_states]

    # Helper function to find the group a state belongs to.
    def find_group(state: State, partition: list[set[State]]) -> Optional[int]:
        """
        Find the index of the group in the partition that contains the given state.

        Args:
            state (State): The state to find in the partition.
            partition (list[set[State]]): A list of sets of group of states.

        Returns:
            int: The index of the group that contains the state, or `None` if the state isn't found in any group.
        """
        for partition_index, group in enumerate(partition):
            if state in group:
                return partition_index
        return None

    # Step 2: Check all states in same partition have same behavior.
    # Two states are said to be exhibiting the same behavior if and only if for each input,
    # both the states makes transitions to the same partition (not necessarily the same state).
    is_consistent: bool = True
    while is_consistent:
        is_consistent = False
        new_partition: list[set[State]] = []

        for group in state_partition:
            # Split group into smaller groups based on transitions.
            split_groups: dict[tuple[Optional[int], ...], set[State]] = {}
            for state in group:
                signature: tuple[Optional[int], ...] = tuple(
                    find_group(dfa.transition_table[state][symbol], state_partition)
                    if symbol in dfa.transition_table[state]
                    else None
                    for symbol in dfa.alphabet
                )
                if signature not in split_groups:
                    split_groups[signature] = set()
                split_groups[signature].add(state)

            # Add split groups to the new partition.
            new_partition.extend(split_groups.values())

        # Check if the partition has changed.
        if len(new_partition) > len(state_partition):
            is_consistent = True

        # Re-compute the transitions with respect to the modified partition set.
        state_partition = new_partition

    # Step 3: Construct the minimized DFA.
    state_map: dict[State, int] = {
        state: partition_index
        for partition_index, group in enumerate(state_partition)
        for state in group
    }
    new_states: dict[str, State] = {
        f"s{partition_index}": State(
            f"s{partition_index}", any(s.is_accepting for s in group)
        )
        for partition_index, group in enumerate(state_partition)
    }
    new_transition_table: dict[State, dict[str, State]] = {}

    for partition_index, group in enumerate(state_partition):
        # Pick an arbitrary state from the group.
        representative: State = next(iter(group))
        new_state: State = new_states[f"s{partition_index}"]
        new_transition_table[new_state] = {}

        for symbol in dfa.alphabet:
            if symbol in dfa.transition_table[representative]:
                target_state: State = dfa.transition_table[representative][symbol]
                target_group: int = state_map[target_state]
                new_transition_table[new_state][symbol] = new_states[f"s{target_group}"]

    new_start_state: State = new_states[f"s{state_map[dfa.starting_state]}"]

    return DFA(new_start_state, new_states, dfa.alphabet, new_transition_table)
