from __future__ import annotations

from datetime import date


def add_months(start: date, months: int) -> date:
    """Return a date advanced by a number of whole months.

    Preserves the day of month when possible, otherwise clamps to the last
    valid day in the target month.
    """
    if months < 0:
        raise ValueError("months must be non-negative")
    year = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    day = min(start.day, _days_in_month(year, month))
    return date(year, month, day)


def _days_in_month(year: int, month: int) -> int:
    if month == 2:
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            return 29
        return 28
    if month in {4, 6, 9, 11}:
        return 30
    return 31


__all__ = ["add_months"]
