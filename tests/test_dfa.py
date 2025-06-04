"""
The test file for the DFA module. Tests the DFA class and its methods,
the way it handles edge cases,
including empty strings, invalid symbols, invalid transitions.
"""

import tempfile
from pathlib import Path

import pytest
from src.dfa.dfa import Dfa
from src.dfa.minimize import minimize
from src.dfa.state import State


class TestDFA:
    def test_empty_string(self):
        alphabet = set("01")
        states = {"s0": State("s0", True), "s1": State("s1")}

        starting_state = states["s0"]

        dfa = Dfa(
            starting_state,
            states,
            alphabet,
        )

        assert dfa.run("") == starting_state.is_accepting

    def test_multiples_of_three(self):
        alphabet = set("01")

        multiples_of_three = (
            bin(num)[2:] for num in range(100, 500) if num % 3 == 0
        )
        # https://en.wikipedia.org/wiki/Deterministic_finite_automaton#/media/File:DFA_example_multiplies_of_3.svg
        states = {
            "s0": State("s0", True),
            "s1": State("s1"),
            "s2": State("s2"),
        }

        dfa = Dfa(
            states["s0"],
            states,
            alphabet,
        )

        dfa.add_transition("s0", "0", "s0")
        dfa.add_transition("s0", "1", "s1")
        dfa.add_transition("s1", "0", "s2")
        dfa.add_transition("s1", "1", "s0")
        dfa.add_transition("s2", "1", "s2")
        dfa.add_transition("s2", "0", "s1")

        # Check for multiples of three.
        for num in multiples_of_three:
            assert dfa.run(num)

        # Check for non-multiples of three. Make sure the DFA rejects them.
        assert not dfa.run(bin(5)[2:])
        assert not dfa.run(bin(45773)[2:])

    def test_invalid_symbol(self):
        alphabet = set("01")
        states = {"s0": State("s0", True), "s1": State("s1")}

        dfa = Dfa(
            states["s0"],
            states,
            alphabet,
        )

        with pytest.raises(ValueError):
            dfa.run("2")

    def test_dfa_equivalence(self):
        alphabet = set("01")
        states1 = {"s0": State("s0", True), "s1": State("s1")}
        states2 = {"q0": State("q0", True), "q1": State("q1")}

        dfa1 = Dfa(
            states1["s0"],
            states1,
            alphabet,
        )

        dfa1.add_transition("s0", "0", "s1")
        dfa1.add_transition("s0", "1", "s0")
        dfa1.add_transition("s1", "0", "s1")
        dfa1.add_transition("s1", "1", "s0")

        dfa2 = Dfa(
            states2["q0"],
            states2,
            alphabet,
        )

        dfa2.add_transition("q0", "0", "q1")
        dfa2.add_transition("q0", "1", "q0")
        dfa2.add_transition("q1", "0", "q1")
        dfa2.add_transition("q1", "1", "q0")

        assert dfa1 == dfa2

    def test_invalid_transition(self):
        alphabet = set("01")
        s0 = State("s0", True)
        s1 = State("s1")

        dfa = Dfa(
            s0,
            {"s0": s0, "s1": s1},
            alphabet,
        )

        with pytest.raises(ValueError):
            dfa.add_transition("s0", "2", "s1")

    def test_same_transition_twice(self):
        # A DFA cannot accept the same symbol from the same state to two different states.
        alphabet = set("01")
        states = {"s0": State("s0", True), "s1": State("s1")}

        dfa = Dfa(states["s0"], states, alphabet)

        dfa.add_transition("s0", "0", "s1")

        with pytest.raises(ValueError):
            dfa.add_transition("s0", "0", "s0")

    def test_odd_ones(self):
        # A DFA that accepts strings that contain an odd number of 1s.
        alphabet = set("01")

        states = {"D": State("D"), "E": State("E", True)}

        dfa = Dfa(
            states["D"],
            states,
            alphabet,
        )

        dfa.add_transition("D", "0", "D")
        dfa.add_transition("D", "1", "E")

        dfa.add_transition("E", "0", "E")
        dfa.add_transition("E", "1", "D")

        assert dfa.run("1")
        assert dfa.run("1101")
        assert dfa.run("1101101")

        assert not dfa.run("11")
        assert not dfa.run("11011")
        assert not dfa.run("000000")

    def test_add_state(self):
        alphabet: set[str] = set()
        states = {"s0": State("s0", True)}

        dfa = Dfa(
            states["s0"],
            states,
            alphabet,
        )

        # Add a new state.
        dfa.add_state("s1")

        # Check if the state was added.
        assert "s1" in dfa.states
        assert dfa.states["s1"].name == "s1"
        assert not dfa.states["s1"].is_accepting

        # Add another state.s
        dfa.add_state("s2", True)

        # Check if the state was added.
        assert "s2" in dfa.states
        assert dfa.states["s2"].name == "s2"
        assert dfa.states["s2"].is_accepting

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
            non_minimized_states["a"],
            non_minimized_states,
            alphabet,
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

        minimized_dfa = Dfa(
            minimized_dfa_states["a,b"],
            minimized_dfa_states,
            alphabet,
        )

        minimized_dfa.add_transition("a,b", "0", "a,b")
        minimized_dfa.add_transition("a,b", "1", "c,d,e")

        minimized_dfa.add_transition("c,d,e", "0", "c,d,e")
        minimized_dfa.add_transition("c,d,e", "1", "f")

        minimized_dfa.add_transition("f", "0", "f")
        minimized_dfa.add_transition("f", "1", "f")

        # Supposedly minimized DFA by the algorithm.
        supposedly_minimized_dfa = minimize(non_minimized_dfa)

        assert minimized_dfa == supposedly_minimized_dfa

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

        non_minimized_dfa = Dfa(
            states["A"],
            states,
            alphabet,
            transitions,
        )

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
            minimized_states["A,D"],
            minimized_states,
            alphabet,
            minimized_transitions,
        )

        assert minimized_dfa == minimize(non_minimized_dfa)

    # Test JSON serialization.
    def test_dump_json(self):
        alphabet = set("01")
        states = {"s0": State("s0", True), "s1": State("s1")}

        dfa = Dfa(
            states["s0"],
            states,
            alphabet,
        )
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
            assert dfa == loaded_dfa

    # Test DFA intersection operation.
    def test_intersection(self):
        alphabet = set("01")
        # DFA that accepts strings containing a 1.
        states_1 = {
            "p": State("p"),
            "q": State("q", True),
        }

        dfa1 = Dfa(
            states_1["p"],
            states_1,
            alphabet,
        )

        dfa1.add_transition("p", "0", "q")
        dfa1.add_transition("p", "1", "p")
        dfa1.add_transition("q", "0", "q")
        dfa1.add_transition("q", "1", "q")

        states_2 = {
            "r": State("r"),
            "s": State("s", True),
        }

        # DFA that accepts strings containing a 0.
        dfa2 = Dfa(
            states_2["r"],
            states_2,
            alphabet,
        )

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
            states_intersection["p,r"],
            states_intersection,
            alphabet,
        )

        intersected_by_hand_dfa.add_transition("p,r", "0", "q,r")
        intersected_by_hand_dfa.add_transition("p,r", "1", "p,s")
        intersected_by_hand_dfa.add_transition("p,s", "0", "q,s")
        intersected_by_hand_dfa.add_transition("p,s", "1", "p,s")
        intersected_by_hand_dfa.add_transition("q,r", "0", "q,r")
        intersected_by_hand_dfa.add_transition("q,r", "1", "q,s")
        intersected_by_hand_dfa.add_transition("q,s", "0", "q,s")
        intersected_by_hand_dfa.add_transition("q,s", "1", "q,s")

        assert intersection == intersected_by_hand_dfa

    def test_intersection2(self):
        # https://cs.stackexchange.com/a/7108
        alphabet = set("01")

        # DFA that accepts strings containing odd number of 1s.
        states_1 = {
            "x0": State("x0"),
            "x1": State("x1", True),
        }

        dfa1 = Dfa(
            states_1["x0"],
            states_1,
            alphabet,
        )

        dfa1.add_transition("x0", "0", "x0")
        dfa1.add_transition("x0", "1", "x1")

        dfa1.add_transition("x1", "0", "x1")
        dfa1.add_transition("x1", "1", "x0")

        # DFA that accepts strings containing odd number of characters.
        states_2 = {
            "y0": State("y0"),
            "y1": State("y1", True),
        }

        dfa2 = Dfa(
            states_2["y0"],
            states_2,
            alphabet,
        )

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
            "x1,y0": State("x1,y0"),
            "x1,y1": State("x1,y1", True),
        }

        intersected_by_hand_dfa = Dfa(
            states_intersection["x0,y0"],
            states_intersection,
            alphabet,
        )

        intersected_by_hand_dfa.add_transition("x0,y0", "0", "x0,y1")
        intersected_by_hand_dfa.add_transition("x0,y0", "1", "x1,y1")

        intersected_by_hand_dfa.add_transition("x0,y1", "0", "x0,y0")
        intersected_by_hand_dfa.add_transition("x0,y1", "1", "x1,y0")

        intersected_by_hand_dfa.add_transition("x1,y0", "0", "x1,y1")
        intersected_by_hand_dfa.add_transition("x1,y0", "1", "x0,y1")

        intersected_by_hand_dfa.add_transition("x1,y1", "0", "x1,y0")
        intersected_by_hand_dfa.add_transition("x1,y1", "1", "x0,y0")

        assert intersection == intersected_by_hand_dfa

    # Test DFA union operation.
    def test_union(self):
        alphabet = set("01")

        # DFA that accepts strings containing even number of 1s.
        states_1 = {
            "q_even": State("q_even", True),
            "q_odd": State("q_odd"),
        }

        dfa1 = Dfa(
            states_1["q_even"],
            states_1,
            alphabet,
        )

        dfa1.add_transition("q_even", "0", "q_even")
        dfa1.add_transition("q_even", "1", "q_odd")

        dfa1.add_transition("q_odd", "0", "q_odd")
        dfa1.add_transition("q_odd", "1", "q_even")

        # DFA that accepts strings containing even number of characters.
        states_2 = {
            "q_even": State("q_even", True),
            "q_odd": State("q_odd"),
        }

        dfa2 = Dfa(
            states_2["q_even"],
            states_2,
            alphabet,
        )

        dfa2.add_transition("q_even", "0", "q_odd")
        dfa2.add_transition("q_even", "1", "q_odd")

        dfa2.add_transition("q_odd", "0", "q_even")
        dfa2.add_transition("q_odd", "1", "q_even")

        # Supposedly union DFA by algorithm.
        union = dfa1.union(dfa2)

        # Handmade union DFA.
        states_union = {
            "q_even,q_even": State("q_even,q_even", True),
            "q_even,q_odd": State("q_even,q_odd", True),
            "q_odd,q_even": State("q_odd,q_even", True),
            "q_odd,q_odd": State("q_odd,q_odd"),
        }

        union_by_hand_dfa = Dfa(
            states_union["q_even,q_even"],
            states_union,
            alphabet,
        )

        union_by_hand_dfa.add_transition("q_even,q_even", "0", "q_odd,q_even")
        union_by_hand_dfa.add_transition("q_even,q_even", "1", "q_odd,q_odd")

        union_by_hand_dfa.add_transition("q_even,q_odd", "0", "q_odd,q_odd")
        union_by_hand_dfa.add_transition("q_even,q_odd", "1", "q_odd,q_even")

        union_by_hand_dfa.add_transition("q_odd,q_even", "0", "q_even,q_even")
        union_by_hand_dfa.add_transition("q_odd,q_even", "1", "q_even,q_odd")

        union_by_hand_dfa.add_transition("q_odd,q_odd", "0", "q_even,q_odd")
        union_by_hand_dfa.add_transition("q_odd,q_odd", "1", "q_even,q_even")

        assert union == union_by_hand_dfa

    def test_set_difference(self):
        alphabet = set("01")

        # DFA that accepts strings with even number of 1s
        states_1 = {
            "a0": State("a0", True),  # accepting state for even number of 1s
            "a1": State("a1"),  # non-accepting state for odd number of 1s
        }

        dfa1 = Dfa(
            states_1["a0"],
            states_1,
            alphabet,
        )

        dfa1.add_transition("a0", "0", "a0")  # 0 doesn't change parity
        dfa1.add_transition("a0", "1", "a1")  # 1 changes parity to odd
        dfa1.add_transition("a1", "0", "a1")  # 0 doesn't change parity
        dfa1.add_transition("a1", "1", "a0")  # 1 changes parity back to even

        # DFA that accepts strings ending with 1
        states_2 = {
            "b0": State("b0"),  # non-accepting state
            "b1": State(
                "b1", True
            ),  # accepting state for strings ending with 1
        }

        dfa2 = Dfa(
            states_2["b0"],
            states_2,
            alphabet,
        )

        dfa2.add_transition("b0", "0", "b0")  # String now ends with 0
        dfa2.add_transition("b0", "1", "b1")  # String now ends with 1
        dfa2.add_transition("b1", "0", "b0")  # String now ends with 0
        dfa2.add_transition("b1", "1", "b1")  # String now ends with 1

        # Let's verify the individual DFAs first
        # DFA1 - Accepts strings with even number of 1s
        assert dfa1.run("")  # 0 ones - even - accept
        assert dfa1.run("0")  # 0 ones - even - accept
        assert not dfa1.run("1")  # 1 one - odd - reject
        assert dfa1.run("11")  # 2 ones - even - accept
        assert not dfa1.run("111")  # 3 ones - odd - reject

        # DFA2 - Accepts strings ending with 1
        assert not dfa2.run("")  # Empty string doesn't end with 1 - reject
        assert not dfa2.run("0")  # Ends with 0 - reject
        assert dfa2.run("1")  # Ends with 1 - accept
        assert not dfa2.run("10")  # Ends with 0 - reject
        assert dfa2.run("11")  # Ends with 1 - accept

        # The set difference should accept strings with even number of 1s
        # that do not end with 1 (even parity AND not ending with 1)
        difference = dfa1.set_difference(dfa2)

        # Test some strings
        # "" - empty string, even number of 1s (0) and doesn't end with 1 - should be accepted
        assert dfa1.run("")
        assert not dfa2.run("")
        assert difference.run("")

        # "0" - even number of 1s (0) and ends with 0 - should be accepted
        assert dfa1.run("0")
        assert not dfa2.run("0")
        assert difference.run("0")

        # "1" - odd number of 1s (1) and ends with 1 - should be rejected
        assert not dfa1.run("1")
        assert dfa2.run("1")
        assert not difference.run("1")

        # "10" - odd number of 1s (1) and ends with 0 - should be rejected
        assert not dfa1.run("10")
        assert not dfa2.run("10")
        assert not difference.run("10")

        # "11" - even number of 1s (2) and ends with 1 - should be rejected
        assert dfa1.run("11")
        assert dfa2.run("11")
        assert not difference.run("11")

        # "110" - even number of 1s (2) and ends with 0 - should be accepted
        assert dfa1.run("110")
        assert not dfa2.run("110")
        assert difference.run("110")

        # "100" - odd number of 1s (1) and ends with 0 - should be rejected
        assert not dfa1.run("100")
        assert not dfa2.run("100")
        assert not difference.run("100")
