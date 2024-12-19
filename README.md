# DFA

This module is dedicated to the implementation of a Deterministic Finite Automaton (DFA) in Python.

## How to use

```python
from dfa import DFA

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
dfa = DFA(states["s0"], states, alphabet, transitions)

# Run a string.
if dfa.run("010101"):
    print("Accepted")
else:
    print("Rejected")
```

## Supported operations

- Running arbitrary strings
- Minimization
