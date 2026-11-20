"""SM-2 spaced repetition algorithm.

After each review the learner rates their recall from 0 to 5:
  5 perfect, 4 correct after hesitation, 3 correct but difficult,
  2 wrong but felt familiar, 1 wrong, 0 complete blackout.

Ratings below 3 count as a failure: the card starts over and comes back tomorrow.
Ratings of 3+ grow the interval: 1 day, then 6 days, then interval x ease factor.
The ease factor (min 1.3) goes up for easy answers and down for hard ones,
so cards you find hard come back more often.
"""

from dataclasses import dataclass
from datetime import date, timedelta

MIN_EASE = 1.3


@dataclass
class ReviewResult:
    ease_factor: float
    interval: int
    repetitions: int
    due_date: date


def review(ease_factor: float, interval: int, repetitions: int,
           quality: int, today: date) -> ReviewResult:
    if not 0 <= quality <= 5:
        raise ValueError("quality must be between 0 and 5")

    if quality < 3:
        # Forgot it: start the repetitions again, keep the ease factor
        repetitions = 0
        interval = 1
    else:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ease_factor)
        repetitions += 1
        ease_factor += 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        ease_factor = max(MIN_EASE, round(ease_factor, 2))

    return ReviewResult(
        ease_factor=ease_factor,
        interval=interval,
        repetitions=repetitions,
        due_date=today + timedelta(days=interval),
    )
