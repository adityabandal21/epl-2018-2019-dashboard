# EPL 2018–2019 Match Analytics Dashboard

A Streamlit dashboard backed by a normalized SQLite database to explore EPL 2018–2019 match outcomes, goals, discipline, and referee trends.

## Files
- `app.py` — Streamlit application
- `epl_2018_2019.db` — SQLite database (normalized)
- `2018-2019.csv` — Raw dataset (CSV)
- `requirements.txt` — Python dependencies

## Features
- Filter by Team / Referee
- Browse matches + search + CSV export
- Analytics (goals by team)
- Compare two teams
- CRUD demo (UPDATE match result)

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Notes
This is an academic project. Premier League branding is used for visual inspiration only.
