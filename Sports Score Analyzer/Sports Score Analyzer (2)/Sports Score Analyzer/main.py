from datetime import date
from storage import load_json, save_all, import_csv
from validation import validate_match
from analytics import summary, match_result, search_matches, warnings
from export import export_csv, export_summary, create_charts

def show_table(matches):
    if not matches:
        print("\nNo matches found."); return
    print("\n" + "-" * 112)
    print(f"{'ID':<8} {'Date':<12} {'Team A':<18} {'Score':<11} {'Team B':<18} {'Winner':<18} {'Status':<11}")
    print("-" * 112)
    for m in matches:
        score = f"{m['score_a']} - {m['score_b']}"
        print(f"{m['match_id']:<8} {m['date']:<12} {m['team_a'][:17]:<18} {score:<11} {m['team_b'][:17]:<18} {match_result(m)[:17]:<18} {m['status']:<11}")
    print("-" * 112)

def add_match(matches):
    print("\nADD NEW MATCH")
    raw = {
        "match_id": input("Match ID: ").strip(),
        "date": input("Date (YYYY-MM-DD): ").strip(),
        "tournament": input("Tournament: ").strip(),
        "sport": input("Sport: ").strip(),
        "team_a": input("Team A: ").strip(),
        "team_b": input("Team B: ").strip(),
        "score_a": input("Team A score: ").strip(),
        "score_b": input("Team B score: ").strip(),
        "venue": input("Venue: ").strip(),
        "status": input("Status (Completed/Scheduled/Abandoned): ").strip()
    }
    item, errors = validate_match(raw, {m["match_id"] for m in matches})
    if errors:
        print("\nPlease correct these issues:")
        for e in errors: print(" -", e)
        return
    matches.append(item); save_all(matches); print("Match saved successfully.")

def main():
    matches = load_json()
    while True:
        print("\n" + "=" * 52)
        print("             SPORTS SCORE ANALYZER")
        print("=" * 52)
        print("1. Add match        2. View matches")
        print("3. Search matches   4. Executive summary")
        print("5. Team rankings    6. Import CSV")
        print("7. Export reports   8. Generate charts")
        print("9. Warnings         0. Exit")
        choice = input("\nChoose an option: ").strip()
        if choice == "1": add_match(matches)
        elif choice == "2": show_table(matches)
        elif choice == "3":
            key = input("Search keyword: ").strip()
            status = input("Status filter (All/Completed/Scheduled/Abandoned): ").strip().title() or "All"
            if status not in ("All", "Completed", "Scheduled", "Abandoned"): status = "All"
            show_table(search_matches(matches, key, status))
        elif choice == "4":
            s = summary(matches)
            print(f"\nTotal: {s['total_matches']} | Completed: {s['completed']} | Scheduled: {s['scheduled']} | Abandoned: {s['abandoned']} | Draws: {s['draws']}")
            print(f"Average score: {s['average_score']} | Highest score: {s['highest_score']}")
        elif choice == "5":
            for i, (team, d) in enumerate(summary(matches)["ranking"], 1):
                print(f"{i:>2}. {team:<20} Played {d['played']:<3} Wins {d['wins']:<3} Runs {d['runs']:<5} Difference {d['runs']-d['against']}")
        elif choice == "6":
            path = input("CSV file path: ").strip().strip('"')
            new, errors = import_csv(path, matches)
            matches.extend(new); save_all(matches)
            print(f"Imported {len(new)} matches.")
            for e in errors: print(" -", e)
        elif choice == "7":
            print("Created:", export_csv(matches))
            print("Created:", *export_summary(matches))
        elif choice == "8":
            paths = create_charts(matches)
            print("Created charts:" if paths else "No charts created (no completed matches or Matplotlib unavailable).")
            for p in paths: print(" -", p)
        elif choice == "9":
            notes = warnings(matches)
            print("\n".join("⚠ " + n for n in notes) if notes else "No warnings.")
        elif choice == "0":
            save_all(matches); print("Data saved. Goodbye!"); break
        else: print("Invalid option. Enter a number from 0 to 9.")

if __name__ == "__main__":
    main()
