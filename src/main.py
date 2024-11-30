from dfa.dfa import DFA
from dfa.state import State

def main():
    states = {
        "s0": State("s0", is_accepting=False),
        "s1": State("s1", is_accepting=False),
        "s2": State("s2", is_accepting=True),
    }

    alphabet = set("01")

    dfa = DFA(states["s0"], states, alphabet)

    dfa.add_transition("s0", "0", "s1")
    dfa.add_transition("s0", "1", "s0")
    dfa.add_transition("s1", "0", "s2")
    dfa.add_transition("s1", "1", "s0")
    dfa.add_transition("s2", "0", "s2")
    dfa.add_transition("s2", "1", "s2")

    print(dfa)


if __name__ == "__main__":
    main()
