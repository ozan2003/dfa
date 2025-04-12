# DFA

This module is dedicated to the representation of a Deterministic Finite Automaton (DFA) as a graph data structure in Python.

## Supported operations

- Running arbitrary strings
- Minimization
- Intersection
- Union
- JSON serialization/deserialization

## How to use

```python
from dfa import Dfa, State

# Define the alphabet.
alphabet = set("01")

# Define the states.
states = {
    "s0": State("s0", True),
    "s1": State("s1"),
}

# Define the transitions.
transitions = {
    states["s0"]: {"0": states["s0"], "1": states["s1"]},
    states["s1"]: {"0": states["s1"], "1": states["s0"]},
}

# Create the DFA.
dfa = Dfa(states["s0"], states, alphabet, transitions)

# Run a string.
if dfa.run("010101"):
    print("Accepted")
else:
    print("Rejected")
```

### JSON Serialization Example

```python
from pathlib import Path

# Serialize the DFA to JSON.
dfa.dump_json(Path("my_dfa.json"))

# Load a DFA from JSON.
loaded_dfa = Dfa.from_json(Path("my_dfa.json"))

# The loaded DFA works exactly like the original.
assert loaded_dfa.run("010101") == dfa.run("010101")
```

## Dependencies

- Python 3.9 or higher
- [pytest](https://docs.pytest.org/en/stable/)
