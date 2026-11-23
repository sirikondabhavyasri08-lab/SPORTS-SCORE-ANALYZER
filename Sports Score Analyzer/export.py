import csv
from pathlib import Path
from analytics import summary, match_result

ROOT = Path(__file__).resolve().parent
REPORTS = ROOT / "reports"
CHARTS = ROOT / "charts"

def export_csv(matches):
    REPORTS.mkdir(exist_ok=True)
    path = REPORTS / "matches_report.csv"
    fields = ["match_id","date","tournament","sport","team_a","team_b","score_a","score_b","winner","venue","status"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for m in matches:
            writer.writerow({**m, "winner": match_result(m)})
    return path

def export_summary(matches):
    REPORTS.mkdir(exist_ok=True)
    s = summary(matches)
    lines = [
        "# Sports Score Analyzer — Executive Summary", "",
        f"- Total matches: {s['total_matches']}",
        f"- Completed: {s['completed']}",
        f"- Scheduled: {s['scheduled']}",
        f"- Abandoned: {s['abandoned']}",
        f"- Draws: {s['draws']}",
        f"- Average team score: {s['average_score']}",
        f"- Highest score: {s['highest_score']}", "", "## Team rankings", "",
        "| Rank | Team | Played | Wins | Runs | Run difference |",
        "|---:|---|---:|---:|---:|---:|"
    ]
    for rank, (team, data) in enumerate(s["ranking"], 1):
        lines.append(f"| {rank} | {team} | {data['played']} | {data['wins']} | {data['runs']} | {data['runs']-data['against']} |")
    md = "\n".join(lines) + "\n"
    (REPORTS / "summary.md").write_text(md, encoding="utf-8")
    (REPORTS / "summary.txt").write_text(md.replace("#", "").replace("|", "  "), encoding="utf-8")
    return REPORTS / "summary.md", REPORTS / "summary.txt"

def create_charts(matches):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return []
    CHARTS.mkdir(exist_ok=True)
    done = [m for m in matches if m["status"] == "Completed"]
    created = []
    if done:
        fig, ax = plt.subplots(figsize=(10, 5))
        labels = [m["match_id"] for m in done]
        ax.plot(labels, [m["score_a"] for m in done], marker="o", label="Team A")
        ax.plot(labels, [m["score_b"] for m in done], marker="o", label="Team B")
        ax.set_title("Match Score Trends"); ax.set_xlabel("Match ID"); ax.set_ylabel("Score")
        ax.legend(); ax.grid(alpha=.25); fig.tight_layout()
        p = CHARTS / "sports_score_chart.png"; fig.savefig(p, dpi=160); plt.close(fig); created.append(p)

        s = summary(matches)
        if s["ranking"]:
            fig, ax = plt.subplots(figsize=(9, 5))
            teams = [x[0] for x in s["ranking"]]
            wins = [x[1]["wins"] for x in s["ranking"]]
            ax.bar(teams, wins); ax.set_title("Team Wins Ranking"); ax.set_ylabel("Wins")
            ax.tick_params(axis="x", rotation=35); fig.tight_layout()
            p = CHARTS / "team_performance.png"; fig.savefig(p, dpi=160); plt.close(fig); created.append(p)
    return created
