from datetime import date, datetime, timedelta
import calendar
import re

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}


def _num(text: str) -> int:
    if text.isdigit():
        return int(text)
    if text in NUMBER_WORDS:
        return NUMBER_WORDS[text]
    raise ValueError(f"Invalid number: {text}")


def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def _add_unit(d: date, amount: int, unit: str) -> date:
    if unit.startswith("day"):
        return d + timedelta(days=amount)
    if unit.startswith("week"):
        return d + timedelta(weeks=amount)
    if unit.startswith("month"):
        return _add_months(d, amount)
    if unit.startswith("year"):
        return _add_years(d, amount)
    raise ValueError(f"Invalid unit: {unit}")


def _apply_multiple_units(d: date, expr: str, sign: int) -> date:
    parts = re.split(r",| and ", expr)

    for part in parts:
        part = part.strip()

        match = re.fullmatch(r"(\d+|[a-z]+) (days?|weeks?|months?|years?)", part)
        if not match:
            raise ValueError(f"Invalid duration: {part}")

        amount = _num(match.group(1)) * sign
        unit = match.group(2)
        d = _add_unit(d, amount, unit)

    return d


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)

    if s == "today":
        return today

    if s == "tomorrow":
        return today + timedelta(days=1)

    if s == "the day after tomorrow":
        return today + timedelta(days=2)

    if s == "yesterday":
        return today - timedelta(days=1)

    if s == "the day before yesterday":
        return today - timedelta(days=2)

    match = re.fullmatch(
        r"(?:in |after )?(\d+|[a-z]+) (days?|weeks?|months?|years?)", s
    )
    if match:
        amount = _num(match.group(1))
        unit = match.group(2)
        return _add_unit(today, amount, unit)

    match = re.fullmatch(r"(.+) ago", s)
    if match:
        return _apply_multiple_units(today, match.group(1), -1)

    match = re.fullmatch(r"(.+) from now", s)
    if match:
        return _apply_multiple_units(today, match.group(1), 1)

    match = re.fullmatch(r"(.+) from tomorrow", s)
    if match:
        return _apply_multiple_units(today + timedelta(days=1), match.group(1), 1)

    match = re.fullmatch(r"(.+) after (.+)", s)
    if match:
        base = parse(match.group(2), today)
        return _apply_multiple_units(base, match.group(1), 1)

    match = re.fullmatch(r"(.+) before (.+)", s)
    if match:
        base = parse(match.group(2), today)
        return _apply_multiple_units(base, match.group(1), -1)

    match = re.fullmatch(r"next (\w+)", s)
    if match:
        weekday_name = match.group(1)
        if weekday_name not in WEEKDAYS:
            raise ValueError("Invalid weekday")

        delta = (WEEKDAYS[weekday_name] - today.weekday()) % 7
        if delta == 0:
            delta = 7
        return today + timedelta(days=delta)

    match = re.fullmatch(r"last (\w+)", s)
    if match:
        weekday_name = match.group(1)
        if weekday_name not in WEEKDAYS:
            raise ValueError("Invalid weekday")

        delta = (today.weekday() - WEEKDAYS[weekday_name]) % 7
        if delta == 0:
            delta = 7
        return today - timedelta(days=delta)

    try:
        return date.fromisoformat(s)
    except ValueError:
        pass

    match = re.fullmatch(r"(\d{4})/(\d{1,2})/(\d{1,2})", s)
    if match:
        year, month, day = map(int, match.groups())
        return date(year, month, day)

    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", s)
    cleaned = cleaned.replace(".", "")

    for fmt in [
        "%B %d %Y",
        "%b %d %Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Could not parse date: {s}")
