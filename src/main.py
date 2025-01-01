from dfa.dfa import Dfa, State
from dfa.minimize import minimize
from pathlib import Path

def main():
    # Vizede sorulan DFA.
    alphabet = set("ab")

    states = {
        "1": State("1", False),
        "2": State("2", False),
        "3": State("3", False),
        "4": State("4", True),
        "5": State("5", False),
        "6": State("6", True),
        "7": State("7", True),
    }

    transitions = {
        states["1"]: {"a": states["2"], "b": states["3"]},
        states["2"]: {"a": states["4"], "b": states["5"]},
        states["3"]: {"a": states["6"], "b": states["7"]},
        states["4"]: {"a": states["4"], "b": states["5"]},
        states["5"]: {"a": states["6"], "b": states["7"]},
        states["6"]: {"a": states["4"], "b": states["5"]},
        states["7"]: {"a": states["6"], "b": states["7"]},
    }

    non_minimized_dfa = Dfa(states["1"], states, alphabet, transitions)

    print(f"Non-minimized DFA: {non_minimized_dfa}")

    minimized_dfa = minimize(non_minimized_dfa)

    print(f"Minimized DFA: {minimized_dfa}")


if __name__ == "__main__":
    main()
