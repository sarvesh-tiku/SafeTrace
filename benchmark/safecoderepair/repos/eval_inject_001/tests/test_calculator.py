import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calculator import evaluate_expression


def test_integer_addition():
    assert evaluate_expression("1+2") == 3.0


def test_three_terms():
    assert evaluate_expression("1+2+3") == 6.0


def test_float_result_preserved():
    assert abs(evaluate_expression("1.5+1.6") - 3.1) < 1e-9
