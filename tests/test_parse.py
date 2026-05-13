from datetime import date
from nldate import parse


TODAY = date(2025, 5, 13)


def test_today():
    assert parse("today", TODAY) == date(2025, 5, 13)


def test_tomorrow():
    assert parse("tomorrow", TODAY) == date(2025, 5, 14)


def test_yesterday():
    assert parse("yesterday", TODAY) == date(2025, 5, 12)


def test_in_days():
    assert parse("in 5 days", TODAY) == date(2025, 5, 18)


def test_days_ago():
    assert parse("3 days ago", TODAY) == date(2025, 5, 10)


def test_next_monday():
    assert parse("next monday", TODAY) == date(2025, 5, 19)


def test_next_friday():
    assert parse("next friday", TODAY) == date(2025, 5, 16)


def test_iso_date():
    assert parse("2025-12-25") == date(2025, 12, 25)


def test_full_month():
    assert parse("December 25 2025") == date(2025, 12, 25)


def test_short_month():
    assert parse("Dec 25 2025") == date(2025, 12, 25)