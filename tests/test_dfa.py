"""
This is the test file for the DFA module. It tests the DFA class and its methods,
the way it handles edge cases,
including empty strings, invalid symbols, invalid transitions.

Various DFAs from the recent lectures may be tested here.
"""

from src.dfa.dfa import DFA
from src.dfa.state import State

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

        multiples_of_three = tuple(bin(num)[2:] for num in range(100, 500) if num % 3 == 0)
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


def main():
    unittest.main()


if __name__ == "__main__":
    main()