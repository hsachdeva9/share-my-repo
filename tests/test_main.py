import pytest
from src.main import _coerce_list_or_string_to_csv

class TestCoerceListOrStringToCSV:

    def test_none_input(self):
        assert _coerce_list_or_string_to_csv(None) is None

    def test_string_input(self):
        assert _coerce_list_or_string_to_csv("hello") == "hello"
        assert _coerce_list_or_string_to_csv("") == ""

    def test_list_of_strings(self):
        val = ["one", "two", "three"]
        assert _coerce_list_or_string_to_csv(val) == "one,two,three"

    def test_tuple_of_strings(self):
        val = ("a", "b", "c")
        assert _coerce_list_or_string_to_csv(val) == "a,b,c"

    def test_list_with_none_values(self):
        val = ["x", None, "y"]
        assert _coerce_list_or_string_to_csv(val) == "x,y"

    def test_mixed_type_list(self):
        val = ["x", 5, True, None]
        assert _coerce_list_or_string_to_csv(val) == "x,5,True"

    def test_non_list_non_string_input(self):
        assert _coerce_list_or_string_to_csv(42) == "42"
        assert _coerce_list_or_string_to_csv(3.14) == "3.14"
        assert _coerce_list_or_string_to_csv(True) == "True"
