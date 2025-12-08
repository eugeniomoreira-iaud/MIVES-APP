import math

import pytest

from logic.math_engine import MivesLogic


def test_lower_and_upper_bounds():
    ml = MivesLogic()
    # Increasing direction
    assert ml.calculate_mives_value(0.0, 1.0, 2.0, 1.0, 1.0, 1.0) == 0.0
    assert ml.calculate_mives_value(3.0, 1.0, 2.0, 1.0, 1.0, 1.0) == 1.0


def test_midrange_monotonic():
    ml = MivesLogic()
    v1 = ml.calculate_mives_value(1.25, 1.0, 2.0, 10.0, 0.5, 1.0)
    v2 = ml.calculate_mives_value(1.75, 1.0, 2.0, 10.0, 0.5, 1.0)
    assert 0.0 < v1 < v2 < 1.0


def test_invalid_saturation_order():
    ml = MivesLogic()
    # If x_sat_1 <= x_sat_0, the implementation should handle inputs gracefully
    # and return a clamped float in [0.0, 1.0]. We don't enforce a specific
    # convention here (caller may prefer 0 or 1), only that the function is
    # robust and returns a valid normalized value.
    val = ml.calculate_mives_value(1.5, 2.0, 1.0, 1.0, 1.0, 1.0)
    assert isinstance(val, float)
    assert 0.0 <= val <= 1.0


def test_numeric_stability_extreme_params():
    ml = MivesLogic()
    # Very small C, large K/P should not raise and should return clamped value
    val = ml.calculate_mives_value(1.5, 1.0, 2.0, 1e-8, 1e6, 10.0)
    assert isinstance(val, float)
    assert 0.0 <= val <= 1.0


def test_zero_range():
    ml = MivesLogic()
    # When x_sat_0 == x_sat_1, the implementation should be robust
    val = ml.calculate_mives_value(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    assert isinstance(val, float)
    assert 0.0 <= val <= 1.0
