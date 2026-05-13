from datetime import date, timedelta
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


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = s.lower().strip()

    if s == "today":
        return today

    if s == "tomorrow":
        return today + timedelta(days=1)

    if s == "yesterday":
        return today - timedelta(days=1)

    # in X days
    match = re.match(r"in (\d+) days?", s)
    if match:
        days = int(match.group(1))
        return today + timedelta(days=days)

    # X days ago
    match = re.match(r"(\d+) days? ago", s)
    if match:
        days = int(match.group(1))
        return today - timedelta(days=days)

    # next weekday
    match = re.match(r"next (\w+)", s)
    if match:
        weekday_name = match.group(1)

        if weekday_name not in WEEKDAYS:
            raise ValueError("Invalid weekday")

        target = WEEKDAYS[weekday_name]
        current = today.weekday()

        delta = (target - current) % 7

        if delta == 0:
            delta = 7

        return today + timedelta(days=delta)

    # YYYY-MM-DD
    try:
        return date.fromisoformat(s)
    except ValueError:
        pass

    # Month Day Year
    cleaned = re.sub(r"(st|nd|rd|th)", "", s)

    for fmt in [
        "%B %d %Y",
        "%b %d %Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]:
        try:
            from datetime import datetime

            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Could not parse date: {s}")