# Sports Score Analyzer — GreenFuture Hack Project #93

A beginner-friendly, local-first Python application for storing match scores, validating records, calculating results and rankings, searching records, importing CSV datasets, exporting reports and plotting performance charts.

## Included interfaces
- **Streamlit GUI**: modern dashboard with navigation, metrics, match forms, search, analytics, CSV import, exports and warnings.
- **Terminal UI**: menu-driven interface in `main.py`.

## Requirements
- Python 3.10 or newer
- Internet connection only for the first-time installation of packages

## Run on Windows
1. Extract the ZIP file.
2. Open the extracted `Sports_Score_Analyzer` folder.
3. Double-click `run_windows.bat`, or open PowerShell in this folder and run:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

If PowerShell blocks activation, use `run_windows.bat`; activation is not required to run the commands.

## Run on macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Run the terminal version
```bash
python main.py
```

## Data files
- `data/matches.json` — primary structured record store
- `data/matches.csv` — synchronized CSV copy
- `data/sample_matches.json` and `data/sample_matches.csv` — 40 sample records

The application creates empty storage files automatically if they are missing. A malformed JSON file is moved to `matches.corrupt.json` before a clean store is initialized.

## CSV import format
Required columns:
`match_id,date,tournament,sport,team_a,team_b,score_a,score_b,venue,status`

Date format: `YYYY-MM-DD`. Status must be `Completed`, `Scheduled` or `Abandoned`. Duplicate IDs, missing fields, invalid scores and malformed rows are rejected with row-specific messages.

## Features checklist
- Menu-driven terminal interface
- Modern Streamlit GUI
- Defensive input validation and range checks
- Match result / winner / draw calculation
- Team wins, averages and rankings
- JSON and CSV local persistence
- Keyword search and status filtering
- Executive summary and trends
- Matplotlib score trend and team ranking charts
- Markdown, TXT and CSV report exports
- Threshold warnings for past scheduled matches, unusually high scores and unusually large score margins
- Bulk CSV import with row-by-row validation
- 40 sample match records
- Automated unit tests

## Notes
This is a local demo application. Sample records are illustrative, not live sports results. No external sports API is required.
