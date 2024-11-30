"""
This is the implementation file of DFA minimization algorithm.
"""

from .dfa import DFA
from .state import State


def minimize(dfa: DFA) -> DFA:
    """
    Minimize the DFA.

    Args:
        dfa (DFA): The DFA to be minimized.

    Returns:
        DFA: The minimized DFA.
    """
    # Step 1: Initial partition of states into final and non-final states
    final_states: set[State] = {
        state for state in dfa.states.values() if state.is_accepting
    }
    non_final_states: set[State] = {
        state for state in dfa.states.values() if not state.is_accepting
    }
    partition: list[set[State]] = [final_states, non_final_states]

    # Helper function to find the group a state belongs to
    def find_group(state: State, partition: list[set[State]]) -> int:
        for i, group in enumerate(partition):
            if state in group:
                return i
        return -1

    # Step 2: Iteratively refine the partition
    refined: bool = True
    while refined:
        refined = False
        new_partition: list[set[State]] = []

        for group in partition:
            # Split group into smaller groups based on transitions
            split_groups: dict[tuple[int, ...], set[State]] = {}
            for state in group:
                # Signature: tuple of groups reached on input symbols
                signature: tuple[int, ...] = tuple(
                    find_group(dfa.transition_table[state][symbol], partition)
                    if symbol in dfa.transition_table[state]
                    else -1
                    for symbol in dfa.alphabet
                )
                if signature not in split_groups:
                    split_groups[signature] = set()
                split_groups[signature].add(state)

            # Add split groups to the new partition
            new_partition.extend(split_groups.values())

        # Check if the partition has changed
        if len(new_partition) > len(partition):
            refined = True

        partition = new_partition

    # Step 3: Construct the minimized DFA
    state_map: dict[State, int] = {
        state: i for i, group in enumerate(partition) for state in group
    }
    new_states: dict[str, State] = {
        f"s{i}": State(f"s{i}", any(s.is_accepting for s in group))
        for i, group in enumerate(partition)
    }
    new_transition_table: dict[State, dict[str, State]] = {}

    for i, group in enumerate(partition):
        # Pick an arbitrary state from the group.
        representative: State = next(iter(group))
        new_state: State = new_states[f"s{i}"]
        new_transition_table[new_state] = {}

        for symbol in dfa.alphabet:
            if symbol in dfa.transition_table[representative]:
                target_state: State = dfa.transition_table[representative][symbol]
                target_group: int = state_map[target_state]
                new_transition_table[new_state][symbol] = new_states[f"s{target_group}"]

    new_start_state: State = new_states[f"s{state_map[dfa.starting_state]}"]

    return DFA(new_start_state, new_states, dfa.alphabet, new_transition_table)
