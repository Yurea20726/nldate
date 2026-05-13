from datetime import date, datetime, timedelta
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

    match = re.fullmatch(r"in (\d+) days?", s)
    if match:
        return today + timedelta(days=int(match.group(1)))

    match = re.fullmatch(r"in (\d+) weeks?", s)
    if match:
        return today + timedelta(weeks=int(match.group(1)))

    match = re.fullmatch(r"(\d+) days? ago", s)
    if match:
        return today - timedelta(days=int(match.group(1)))

    match = re.fullmatch(r"(\d+) weeks? ago", s)
    if match:
        return today - timedelta(weeks=int(match.group(1)))

    match = re.fullmatch(r"next (\w+)", s)
    if match:
        weekday_name = match.group(1)
        if weekday_name not in WEEKDAYS:
            raise ValueError("Invalid weekday")

        delta = (WEEKDAYS[weekday_name] - today.weekday()) % 7
        if delta == 0:
            delta = 7
        return today + timedelta(days=delta)

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
