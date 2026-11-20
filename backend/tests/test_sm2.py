from datetime import date

import pytest

from sm2 import MIN_EASE, review

TODAY = date(2026, 1, 1)


def test_first_correct_answer_comes_back_tomorrow():
    result = review(2.5, 0, 0, quality=4, today=TODAY)
    assert result.interval == 1
    assert result.repetitions == 1
    assert result.due_date == date(2026, 1, 2)


def test_second_correct_answer_waits_six_days():
    result = review(2.5, 1, 1, quality=4, today=TODAY)
    assert result.interval == 6
    assert result.repetitions == 2


def test_later_intervals_grow_by_ease_factor():
    result = review(2.5, 6, 2, quality=4, today=TODAY)
    assert result.interval == 15   # round(6 * 2.5)


def test_failing_resets_but_keeps_ease():
    result = review(2.2, 20, 5, quality=1, today=TODAY)
    assert result.repetitions == 0
    assert result.interval == 1
    assert result.ease_factor == 2.2


def test_easy_answer_raises_ease_and_hard_answer_lowers_it():
    assert review(2.5, 0, 0, quality=5, today=TODAY).ease_factor == 2.6
    assert review(2.5, 0, 0, quality=3, today=TODAY).ease_factor == 2.36


def test_ease_never_drops_below_minimum():
    result = review(MIN_EASE, 6, 2, quality=3, today=TODAY)
    assert result.ease_factor == MIN_EASE


@pytest.mark.parametrize("quality", [-1, 6])
def test_rejects_quality_outside_0_to_5(quality):
    with pytest.raises(ValueError):
        review(2.5, 0, 0, quality=quality, today=TODAY)
