"""
This is the test file for the DFA module. It tests the DFA class and its methods,
the way it handles edge cases,
including empty strings, invalid symbols, invalid transitions.

Various DFAs from the recent lectures may be tested here.
"""

from src.dfa.dfa import Dfa
from src.dfa.state import State
from src.dfa.minimize import minimize

import unittest
import tempfile
from pathlib import Path


class TestDFA(unittest.TestCase):
    def test_empty_string(self):
        alphabet = set("01")
        states = {"s0": State("s0", True), "s1": State("s1")}

        starting_state = states["s0"]

        dfa = Dfa(starting_state, states, alphabet)

        self.assertEqual(dfa.run(""), starting_state.is_accepting)

    def test_multiples_of_three(self):
        alphabet = set("01")

        multiples_of_three = (bin(num)[2:] for num in range(100, 500) if num % 3 == 0)
        # https://en.wikipedia.org/wiki/Deterministic_finite_automaton#/media/File:DFA_example_multiplies_of_3.svg
        states = {
            "s0": State("s0", True),
            "s1": State("s1"),
            "s2": State("s2"),
        }

        dfa = Dfa(states["s0"], states, alphabet)

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
        states = {"s0": State("s0", True), "s1": State("s1")}

        dfa = Dfa(states["s0"], states, alphabet)

        with self.assertRaises(ValueError):
            dfa.run("2")

    def test_dfa_equivalence(self):
        alphabet = set("01")
        states1 = {"s0": State("s0", True), "s1": State("s1")}
        states2 = {"q0": State("q0", True), "q1": State("q1")}

        dfa1 = Dfa(states1["s0"], states1, alphabet)

        dfa1.add_transition("s0", "0", "s1")
        dfa1.add_transition("s0", "1", "s0")
        dfa1.add_transition("s1", "0", "s1")
        dfa1.add_transition("s1", "1", "s0")

        dfa2 = Dfa(states2["q0"], states2, alphabet)

        dfa2.add_transition("q0", "0", "q1")
        dfa2.add_transition("q0", "1", "q0")
        dfa2.add_transition("q1", "0", "q1")
        dfa2.add_transition("q1", "1", "q0")

        self.assertEqual(dfa1, dfa2)

    def test_invalid_transition(self):
        alphabet = set("01")
        s0 = State("s0", True)
        s1 = State("s1")

        dfa = Dfa(s0, {"s0": s0, "s1": s1}, alphabet)

        with self.assertRaises(ValueError):
            dfa.add_transition("s0", "2", "s1")

    def test_same_transition_twice(self):
        # A DFA cannot accept the same symbol from the same state to two different states.
        alphabet = set("01")
        states = {"s0": State("s0", True), "s1": State("s1")}

        dfa = Dfa(states["s0"], states, alphabet)

        dfa.add_transition("s0", "0", "s1")

        with self.assertRaises(ValueError):
            dfa.add_transition("s0", "0", "s0")

    def test_odd_ones(self):
        # A DFA that accepts strings that contain an odd number of 1s.
        alphabet = set("01")

        states = {"D": State("D"), "E": State("E", True)}

        dfa = Dfa(states["D"], states, alphabet)

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

        dfa = Dfa(states["s0"], states, alphabet)

        # Add a new state.
        dfa.add_state("s1")

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
            "a": State("a"),
            "b": State("b"),
            "c": State("c", True),
            "d": State("d", True),
            "e": State("e", True),
            "f": State("f"),
        }

        non_minimized_dfa = Dfa(
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
            "a,b": State("a,b"),
            "c,d,e": State("c,d,e", True),
            "f": State("f"),
        }

        minimized_dfa = Dfa(minimized_dfa_states["a,b"], minimized_dfa_states, alphabet)

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
            "A": State("A"),
            "B": State("B"),
            "C": State("C", True),
            "D": State("D"),
            "E": State("E"),
            "F": State("F"),
            "G": State("G"),
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

        non_minimized_dfa = Dfa(states["A"], states, alphabet, transitions)

        minimized_states = {
            "A,D": State("A,D"),
            "B,G": State("B,G"),
            "C": State("C", True),
            "E": State("E"),
            "F": State("F"),
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

        minimized_dfa = Dfa(
            minimized_states["A,D"], minimized_states, alphabet, minimized_transitions
        )

        self.assertEqual(minimized_dfa, minimize(non_minimized_dfa))

    # Test JSON serialization.
    def test_dump_json(self):
        alphabet = set("01")
        states = {"s0": State("s0", True), "s1": State("s1")}

        dfa = Dfa(states["s0"], states, alphabet)
        dfa.add_transition("s0", "0", "s1")
        dfa.add_transition("s0", "1", "s0")
        dfa.add_transition("s1", "0", "s1")
        dfa.add_transition("s1", "1", "s0")

        # Create temporary test file.
        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            temp_path = Path(temp_file.name)

            # Test dumping to JSON.
            dfa.dump_json(temp_path)

            # Test loading back produces equivalent DFA.
            loaded_dfa = Dfa.from_json(temp_path)
            self.assertEqual(dfa, loaded_dfa)

    # Test DFA intersection operation.
    def test_intersection(self):
        alphabet = set("01")
        # DFA that accepts strings containing a 1.
        states_1 = {
            "p": State("p"),
            "q": State("q", True),
        }

        dfa1 = Dfa(states_1["p"], states_1, alphabet)

        dfa1.add_transition("p", "0", "q")
        dfa1.add_transition("p", "1", "p")
        dfa1.add_transition("q", "0", "q")
        dfa1.add_transition("q", "1", "q")

        states_2 = {
            "r": State("r"),
            "s": State("s", True),
        }

        # DFA that accepts strings containing a 0.
        dfa2 = Dfa(states_2["r"], states_2, alphabet)

        dfa2.add_transition("r", "0", "r")
        dfa2.add_transition("r", "1", "s")
        dfa2.add_transition("s", "0", "s")
        dfa2.add_transition("s", "1", "s")

        # Supposedly intersection DFA by algorithm.
        intersection = dfa1.intersection(dfa2)

        # Handmade intersection DFA.
        states_intersection = {
            "p,r": State("p,r"),
            "p,s": State("p,s"),
            "q,r": State("q,r"),
            "q,s": State("q,s", True),
        }

        intersected_by_hand_dfa = Dfa(
            states_intersection["p,r"], states_intersection, alphabet
        )

        intersected_by_hand_dfa.add_transition("p,r", "0", "q,r")
        intersected_by_hand_dfa.add_transition("p,r", "1", "p,s")
        intersected_by_hand_dfa.add_transition("p,s", "0", "q,s")
        intersected_by_hand_dfa.add_transition("p,s", "1", "p,s")
        intersected_by_hand_dfa.add_transition("q,r", "0", "q,r")
        intersected_by_hand_dfa.add_transition("q,r", "1", "q,s")
        intersected_by_hand_dfa.add_transition("q,s", "0", "q,s")
        intersected_by_hand_dfa.add_transition("q,s", "1", "q,s")

        self.assertEqual(intersection, intersected_by_hand_dfa)

    def test_intersection2(self):
        # https://cs.stackexchange.com/a/7108
        alphabet = set("01")

        # DFA that accepts strings containing odd number of 1s.
        states_1 = {
            "x0": State("x0"),
            "x1": State("x1", True),
        }

        dfa1 = Dfa(states_1["x0"], states_1, alphabet)

        dfa1.add_transition("x0", "0", "x0")
        dfa1.add_transition("x0", "1", "x1")

        dfa1.add_transition("x1", "0", "x1")
        dfa1.add_transition("x1", "1", "x0")

        # DFA that accepts strings containing odd number of characters.
        states_2 = {
            "y0": State("y0", True),
            "y1": State("y1"),
        }

        dfa2 = Dfa(states_2["y0"], states_2, alphabet)

        dfa2.add_transition("y0", "0", "y1")
        dfa2.add_transition("y0", "1", "y1")

        dfa2.add_transition("y1", "0", "y0")
        dfa2.add_transition("y1", "1", "y0")

        # Supposedly intersection DFA by algorithm.
        intersection = dfa1.intersection(dfa2)

        # Handmade intersection DFA.
        states_intersection = {
            "x0,y0": State("x0,y0"),
            "x0,y1": State("x0,y1"),
            "x1,y0": State("x1,y0", True),
            "x1,y1": State("x1,y1"),
        }

        intersected_by_hand_dfa = Dfa(
            states_intersection["x0,y0"], states_intersection, alphabet
        )

        intersected_by_hand_dfa.add_transition("x0,y0", "0", "x0,y1")
        intersected_by_hand_dfa.add_transition("x0,y0", "1", "x1,y1")

        intersected_by_hand_dfa.add_transition("x0,y1", "0", "x0,y0")
        intersected_by_hand_dfa.add_transition("x0,y1", "1", "x1,y0")

        intersected_by_hand_dfa.add_transition("x1,y0", "0", "x1,y1")
        intersected_by_hand_dfa.add_transition("x1,y0", "1", "x0,y1")

        intersected_by_hand_dfa.add_transition("x1,y1", "0", "x1,y0")
        intersected_by_hand_dfa.add_transition("x1,y1", "1", "x0,y0")

        self.assertEqual(intersection, intersected_by_hand_dfa)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
