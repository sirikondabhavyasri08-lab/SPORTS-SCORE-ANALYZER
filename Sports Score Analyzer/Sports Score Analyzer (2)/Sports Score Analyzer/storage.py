import csv, json
from pathlib import Path
from validation import validate_match, REQUIRED_FIELDS

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
JSON_PATH = DATA_DIR / "matches.json"
CSV_PATH = DATA_DIR / "matches.csv"

def ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not JSON_PATH.exists():
        save_json([])
    if not CSV_PATH.exists():
        save_csv([])

def load_json():
    ensure_storage()
    try:
        with JSON_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON root must be a list")
        clean, ids = [], set()
        for row in data:
            item, errors = validate_match(row, ids)
            if item:
                clean.append(item); ids.add(item["match_id"])
        return clean
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        # Preserve the damaged file for inspection, then initialize a clean store.
        if JSON_PATH.exists():
            backup = JSON_PATH.with_suffix(".corrupt.json")
            try: JSON_PATH.replace(backup)
            except OSError: pass
        save_json([])
        return []

def save_json(matches):
    ensure_dir = DATA_DIR
    ensure_dir.mkdir(parents=True, exist_ok=True)
    temp = JSON_PATH.with_suffix(".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(matches, f, indent=2, ensure_ascii=False)
    temp.replace(JSON_PATH)

def save_csv(matches):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_FIELDS)
        writer.writeheader()
        writer.writerows(matches)

def save_all(matches):
    save_json(matches)
    save_csv(matches)

def import_csv(path, existing_matches):
    imported, errors = [], []
    existing_ids = {m["match_id"] for m in existing_matches}
    try:
        with Path(path).open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            missing = set(REQUIRED_FIELDS) - set(reader.fieldnames or [])
            if missing:
                return [], [f"CSV missing columns: {', '.join(sorted(missing))}"]
            for line, row in enumerate(reader, start=2):
                item, row_errors = validate_match(row, existing_ids)
                if row_errors:
                    errors.append(f"Row {line}: " + "; ".join(row_errors))
                else:
                    imported.append(item); existing_ids.add(item["match_id"])
    except (OSError, UnicodeError, csv.Error) as exc:
        errors.append(f"Could not read CSV: {exc}")
    return imported, errors
