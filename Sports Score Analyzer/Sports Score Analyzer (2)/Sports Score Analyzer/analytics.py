from collections import Counter, defaultdict
from datetime import date, datetime

def match_result(match):
    if match["status"] != "Completed":
        return "Pending"
    if match["score_a"] > match["score_b"]: return match["team_a"]
    if match["score_b"] > match["score_a"]: return match["team_b"]
    return "Draw"

def completed(matches):
    return [m for m in matches if m["status"] == "Completed"]

def summary(matches):
    done = completed(matches)
    all_scores = [m[k] for m in done for k in ("score_a", "score_b")]
    wins = Counter()
    for m in done:
        result = match_result(m)
        if result != "Draw": wins[result] += 1
    teams = defaultdict(lambda: {"played": 0, "wins": 0, "runs": 0, "against": 0, "draws": 0})
    for m in done:
        a, b = m["team_a"], m["team_b"]
        teams[a]["played"] += 1; teams[b]["played"] += 1
        teams[a]["runs"] += m["score_a"]; teams[b]["runs"] += m["score_b"]
        teams[a]["against"] += m["score_b"]; teams[b]["against"] += m["score_a"]
        result = match_result(m)
        if result == "Draw":
            teams[a]["draws"] += 1; teams[b]["draws"] += 1
        else:
            teams[result]["wins"] += 1
    ranking = sorted(teams.items(), key=lambda x: (x[1]["wins"], x[1]["runs"]-x[1]["against"], x[1]["runs"]), reverse=True)
    return {
        "total_matches": len(matches), "completed": len(done),
        "scheduled": sum(m["status"] == "Scheduled" for m in matches),
        "abandoned": sum(m["status"] == "Abandoned" for m in matches),
        "draws": sum(match_result(m) == "Draw" for m in done),
        "average_score": round(sum(all_scores)/len(all_scores), 2) if all_scores else 0,
        "highest_score": max(all_scores) if all_scores else 0,
        "wins": dict(wins), "ranking": ranking
    }

def warnings(matches):
    notes = []
    today = date.today()
    for m in matches:
        try: match_date = datetime.strptime(m["date"], "%Y-%m-%d").date()
        except ValueError: continue
        if m["status"] == "Scheduled" and match_date < today:
            notes.append(f'{m["match_id"]}: scheduled match date has passed ({m["date"]}). Review status.')
        if m["status"] == "Completed" and max(m["score_a"], m["score_b"]) > 500:
            notes.append(f'{m["match_id"]}: unusually high score; verify the entry.')
        if abs(m["score_a"] - m["score_b"]) > 200:
            notes.append(f'{m["match_id"]}: score margin exceeds 200; verify the entry.')
    return notes

def search_matches(matches, keyword="", category="All"):
    key = keyword.casefold().strip()
    result = []
    for m in matches:
        if category != "All" and m["status"] != category: continue
        haystack = " ".join(str(v) for v in m.values()).casefold()
        if not key or key in haystack: result.append(m)
    return result
