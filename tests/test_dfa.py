"""
This is the test file for the DFA module. It tests the DFA class and its methods,
the way it handles edge cases,
including empty strings, invalid symbols, invalid transitions.

Various DFAs from the recent lectures may be tested here.
"""

from src.dfa.dfa import DFA
from src.dfa.state import State
from src.dfa.minimize import minimize

import unittest


class TestDFA(unittest.TestCase):
    def test_empty_string(self):
        alphabet = set("01")
        states = {"s0": State("s0", True), "s1": State("s1", False)}

        starting_state = states["s0"]

        dfa = DFA(starting_state, states, alphabet)

        self.assertEqual(dfa.run(""), starting_state.is_accepting)

    def test_multiples_of_three(self):
        alphabet = set("01")

        multiples_of_three = tuple(
            bin(num)[2:] for num in range(100, 500) if num % 3 == 0
        )
        # https://en.wikipedia.org/wiki/Deterministic_finite_automaton#/media/File:DFA_example_multiplies_of_3.svg
        states = {
            "s0": State("s0", True),
            "s1": State("s1", False),
            "s2": State("s2", False),
        }

        dfa = DFA(states["s0"], states, alphabet)

        dfa.add_transition("s0", "0", "s0")
        dfa.add_transition("s0", "1", "s1")
        dfa.add_transition("s1", "0", "s2")
        dfa.add_transition("s1", "1", "s0")
        dfa.add_transition("s2", "1", "s2")
        dfa.add_transition("s2", "0", "s1")

        # Check for multiples of three.
        for num in multiples_of_three:
            self.assertTrue(dfa.run(num))

        # Check for non-multiples of three. Make sure the DFA rejects them.
        self.assertFalse(dfa.run(bin(5)[2:]))
        self.assertFalse(dfa.run(bin(45773)[2:]))

    def test_invalid_symbol(self):
        alphabet = set("01")
        states = {"s0": State("s0", True), "s1": State("s1", False)}

        dfa = DFA(states["s0"], states, alphabet)

        with self.assertRaises(ValueError):
            dfa.run("2")

    def test_dfa_equivalence(self):
        alphabet = set("01")
        states1 = {"s0": State("s0", True), "s1": State("s1", False)}
        states2 = {"q0": State("q0", True), "q1": State("q1", False)}

        dfa1 = DFA(states1["s0"], states1, alphabet)

        dfa1.add_transition("s0", "0", "s1")
        dfa1.add_transition("s0", "1", "s0")
        dfa1.add_transition("s1", "0", "s1")
        dfa1.add_transition("s1", "1", "s0")

        dfa2 = DFA(states2["q0"], states2, alphabet)

        dfa2.add_transition("q0", "0", "q1")
        dfa2.add_transition("q0", "1", "q0")
        dfa2.add_transition("q1", "0", "q1")
        dfa2.add_transition("q1", "1", "q0")

        self.assertEqual(dfa1, dfa2)

    def test_invalid_transition(self):
        alphabet = set("01")
        s0 = State("s0", True)
        s1 = State("s1", False)

        dfa = DFA(s0, {"s0": s0, "s1": s1}, alphabet)

        with self.assertRaises(ValueError):
            dfa.add_transition("s0", "2", "s1")

    def test_same_transition_twice(self):
        # A DFA cannot accept the same symbol from the same state to two different states.
        alphabet = set("01")
        states = {"s0": State("s0", True), "s1": State("s1", False)}

        dfa = DFA(states["s0"], states, alphabet)

        dfa.add_transition("s0", "0", "s1")

        with self.assertRaises(ValueError):
            dfa.add_transition("s0", "0", "s0")

    def test_odd_ones(self):
        # A DFA that accepts strings that contain an odd number of 1s.
        alphabet = set("01")

        states = {"D": State("D", False), "E": State("E", True)}

        dfa = DFA(states["D"], states, alphabet)

        dfa.add_transition("D", "0", "D")
        dfa.add_transition("D", "1", "E")

        dfa.add_transition("E", "0", "E")
        dfa.add_transition("E", "1", "D")

        self.assertTrue(dfa.run("1"))
        self.assertTrue(dfa.run("1101"))
        self.assertTrue(dfa.run("1101101"))

        self.assertFalse(dfa.run("11"))
        self.assertFalse(dfa.run("11011"))
        self.assertFalse(dfa.run("000000"))

    def test_add_state(self):
        alphabet: set[str] = set()
        states = {"s0": State("s0", True)}

        dfa = DFA(states["s0"], states, alphabet)

        # Add a new state.
        dfa.add_state("s1", False)

        # Check if the state was added.
        self.assertIn("s1", dfa.states)
        self.assertEqual(dfa.states["s1"].name, "s1")
        self.assertFalse(dfa.states["s1"].is_accepting)

        # Add another state.s
        dfa.add_state("s2", True)

        # Check if the state was added.
        self.assertIn("s2", dfa.states)
        self.assertEqual(dfa.states["s2"].name, "s2")
        self.assertTrue(dfa.states["s2"].is_accepting)

    def test_minimize(self):
        # Check if the DFA is minimized correctly.
        alphabet = set("01")

        # Non-minimized DFA.
        non_minimized_states = {
            "a": State("a", False),
            "b": State("b", False),
            "c": State("c", True),
            "d": State("d", True),
            "e": State("e", True),
            "f": State("f", False),
        }

        non_minimized_dfa = DFA(
            non_minimized_states["a"], non_minimized_states, alphabet
        )

        non_minimized_dfa.add_transition("a", "0", "b")
        non_minimized_dfa.add_transition("a", "1", "c")

        non_minimized_dfa.add_transition("b", "0", "a")
        non_minimized_dfa.add_transition("b", "1", "d")

        non_minimized_dfa.add_transition("c", "0", "e")
        non_minimized_dfa.add_transition("c", "1", "f")

        non_minimized_dfa.add_transition("d", "0", "e")
        non_minimized_dfa.add_transition("d", "1", "f")

        non_minimized_dfa.add_transition("e", "0", "e")
        non_minimized_dfa.add_transition("e", "1", "f")

        non_minimized_dfa.add_transition("f", "0", "f")
        non_minimized_dfa.add_transition("f", "1", "f")

        # Minimized DFA by hand.
        minimized_dfa_states = {
            "a,b": State("a,b", False),
            "c,d,e": State("c,d,e", True),
            "f": State("f", False),
        }

        minimized_dfa = DFA(minimized_dfa_states["a,b"], minimized_dfa_states, alphabet)

        minimized_dfa.add_transition("a,b", "0", "a,b")
        minimized_dfa.add_transition("a,b", "1", "c,d,e")

        minimized_dfa.add_transition("c,d,e", "0", "c,d,e")
        minimized_dfa.add_transition("c,d,e", "1", "f")

        minimized_dfa.add_transition("f", "0", "f")
        minimized_dfa.add_transition("f", "1", "f")

        # Supposedly minimized DFA by the algorithm.
        supposedly_minimized_dfa = minimize(non_minimized_dfa)

        self.assertEqual(
            minimized_dfa, supposedly_minimized_dfa, msg="DFA not minimized correctly."
        )

    def test_minimize_2(self):
        # Something more complex.
        alphabet = set("ab")

        states = {
            "A": State("A", False),
            "B": State("B", False),
            "C": State("C", True),
            "D": State("D", False),
            "E": State("E", False),
            "F": State("F", False),
            "G": State("G", False),
        }

        transitions = {
            states["A"]: {"a": states["B"], "b": states["E"]},
            states["B"]: {"a": states["F"], "b": states["C"]},
            states["C"]: {"a": states["A"], "b": states["C"]},
            states["D"]: {"a": states["G"], "b": states["E"]},
            states["E"]: {"a": states["C"], "b": states["F"]},
            states["F"]: {"a": states["F"], "b": states["D"]},
            states["G"]: {"a": states["F"], "b": states["C"]},
        }

        non_minimized_dfa = DFA(states["A"], states, alphabet, transitions)

        minimized_states = {
            "A,D": State("A,D", False),
            "B,G": State("B,G", False),
            "C": State("C", True),
            "E": State("E", False),
            "F": State("F", False),
        }

        minimized_transitions = {
            minimized_states["A,D"]: {
                "a": minimized_states["B,G"],
                "b": minimized_states["E"],
            },
            minimized_states["B,G"]: {
                "a": minimized_states["F"],
                "b": minimized_states["C"],
            },
            minimized_states["C"]: {
                "a": minimized_states["A,D"],
                "b": minimized_states["C"],
            },
            minimized_states["E"]: {
                "a": minimized_states["C"],
                "b": minimized_states["F"],
            },
            minimized_states["F"]: {
                "a": minimized_states["F"],
                "b": minimized_states["A,D"],
            },
        }

        minimized_dfa = DFA(
            minimized_states["A,D"], minimized_states, alphabet, minimized_transitions
        )

        self.assertEqual(minimized_dfa, minimize(non_minimized_dfa))


def main():
    unittest.main()


if __name__ == "__main__":
    main()
