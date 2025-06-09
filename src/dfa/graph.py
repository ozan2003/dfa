"""
Graphing utility for DFA. Uses graphviz to create visual representations of DFA.
"""

from enum import Enum
from typing import Any

import graphviz  # mypy: ignore: import-untyped

from .dfa import Dfa


class GraphFormat(Enum):
    """
    Enum for direction of graph layout.
    """

    TOP_BOTTOM = "TB"
    LEFT_RIGHT = "LR"
    BOTTOM_TOP = "BT"
    RIGHT_LEFT = "RL"


def visualize(
    dfa: Dfa,
    filename: str,
    *,
    format_type: str = "png",
    rankdir: GraphFormat = GraphFormat.LEFT_RIGHT,
    **kwargs: Any,
) -> graphviz.Digraph:
    """
    Create a visual representation of a DFA.

    Args:
        dfa: The DFA to visualize
        filename: Output filename (without extension)
        format_type: Output format ("png", "pdf", "svg", etc.)
        engine: Graphviz layout engine
        rankdir: Direction of graph layout ("LR", "TB", "RL", "BT")
        **kwargs: Additional arguments passed to graphviz.Digraph
    Returns:
        graphviz.Digraph: The graphviz Digraph object

    """
    # Create a new directed graph
    dot = graphviz.Digraph(
        filename=filename.partition(".")[0],
        format=format_type,
        **kwargs,
    )

    # Set graph attributes for better visualization
    dot.attr(rankdir=rankdir)
    dot.attr("node", shape="circle", fontname="Arial", fontsize="12")
    dot.attr("edge", fontname="Arial", fontsize="10")
    dot.attr(
        "graph",
        label=f"DFA with alphabet {{{', '.join(sorted(dfa.alphabet))}}}",
    )
    dot.attr("graph", fontsize="18")

    # Add an invisible start node and arrow to indicate the starting state
    dot.node("start", style="invisible")
    dot.edge("start", dfa.starting_state.name, color="green")

    # Add all states
    for state in dfa.states.values():
        if state.is_accepting:
            # Accepting states have double circles
            dot.node(
                state.name,
                label=state.name,
                shape="doublecircle",
            )
        else:
            # Regular states have single circles
            dot.node(state.name, label=state.name)

    # Add transitions
    # Group transitions by (from_state, to_state) to combine multiple symbols
    transition_groups: dict[tuple[str, str], list[str]] = {}

    for from_state, transitions in dfa.transition_table.items():
        for symbol, to_state in transitions.items():
            key = (from_state.name, to_state.name)

            if key not in transition_groups:
                transition_groups[key] = []
            transition_groups[key].append(symbol)

    # Add edges with combined labels
    for (from_state_name, to_state_name), symbols in transition_groups.items():
        label = ", ".join(sorted(symbols))
        dot.edge(from_state_name, to_state_name, label=label)

    return dot


def save_dfa_graph(
    dfa: Dfa, filename: str, *, format_type: str = "png", **kwargs: Any
) -> None:
    """
    Save a DFA visualization to a specific file path.

    Args:
        dfa: The DFA to visualize
        filename: Full name for the output file (without extension)
        format_type: Output format
        **kwargs: Additional arguments passed to visualize

    """
    dot = visualize(dfa, filename=filename, format_type=format_type, **kwargs)
    dot.render(cleanup=True)
