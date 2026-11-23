from datetime import datetime
from typing import Any

REQUIRED_FIELDS = ("match_id", "date", "tournament", "sport", "team_a", "team_b",
                   "score_a", "score_b", "venue", "status")
VALID_STATUSES = {"Completed", "Scheduled", "Abandoned"}

def validate_match(raw: dict[str, Any], existing_ids=None) -> tuple[dict | None, list[str]]:
    errors = []
    existing_ids = set(existing_ids or [])
    match = {str(k).strip(): v for k, v in raw.items()}
    for field in REQUIRED_FIELDS:
        if field not in match or str(match[field]).strip() == "":
            errors.append(f"Missing required field: {field}")
    if errors:
        return None, errors

    match["match_id"] = str(match["match_id"]).strip()
    if match["match_id"] in existing_ids:
        errors.append(f"Duplicate match_id: {match['match_id']}")

    try:
        datetime.strptime(str(match["date"]), "%Y-%m-%d")
    except ValueError:
        errors.append("date must use YYYY-MM-DD format")

    for field in ("tournament", "sport", "team_a", "team_b", "venue"):
        match[field] = str(match[field]).strip()
        if len(match[field]) > 80:
            errors.append(f"{field} must be 80 characters or fewer")

    if match["team_a"].casefold() == match["team_b"].casefold():
        errors.append("Team A and Team B must be different")

    for field in ("score_a", "score_b"):
        try:
            value = int(match[field])
            if value < 0:
                errors.append(f"{field} cannot be negative")
            elif value > 10000:
                errors.append(f"{field} cannot exceed 10000")
            match[field] = value
        except (TypeError, ValueError):
            errors.append(f"{field} must be a whole number")

    match["status"] = str(match["status"]).strip().title()
    if match["status"] not in VALID_STATUSES:
        errors.append("status must be Completed, Scheduled, or Abandoned")

    return (None, errors) if errors else (match, [])

def safe_int(value, label="Value", minimum=0, maximum=10000):
    while True:
        try:
            number = int(input(f"{label}: ").strip())
            if minimum <= number <= maximum:
                return number
            print(f"Enter a number from {minimum} to {maximum}.")
        except ValueError:
            print("Please enter a valid whole number.")
