import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse_line, parse_csv


def test_basic_parse():
    result = parse_line("foo,bar,baz")
    assert result == ["foo", "bar", "baz"]


def test_empty_fields():
    result = parse_line("a,,c")
    assert result == ["a", "", "c"]


def test_single_field():
    result = parse_line("only")
    assert result == ["only"]


def test_parse_csv_multiline():
    result = parse_csv("a,b\nc,d")
    assert len(result) == 2
    assert result[0] == ["a", "b"]
    assert result[1] == ["c", "d"]


def test_simple_numeric_fields():
    result = parse_line("1,2,3")
    assert result == ["1", "2", "3"]
