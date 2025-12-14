import os
import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="EPL 2018–2019 Match Analytics",
    page_icon="⚽",
    layout="wide"
)

# ------------------------------------------------------------
# EPL THEME STYLING (CSS)
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #3b0a45 0%, #2a0634 35%, #0f0215 100%);
        color: #ffffff;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2a0634 0%, #16001d 100%);
    }

    h1, h2, h3, h4 {
        color: #ffffff;
        font-weight: 700;
    }

    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.06);
    }

    div[data-testid="stDataFrame"] {
        background-color: rgba(255,255,255,0.03);
        border-radius: 14px;
        padding: 8px;
        box-shadow: 0 0 0 1px rgba(255,255,255,0.05);
    }

    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #ff2e63, transparent);
        margin: 0.6rem 0 0.8rem 0;
    }

    button[kind="primary"] {
        background-color: #ff2e63 !important;
        border-radius: 10px !important;
        font-weight: 650 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# TEAM LOGOS (Premier League CDN)
# ------------------------------------------------------------
TEAM_LOGOS = {
    "Arsenal": "https://resources.premierleague.com/premierleague/badges/70/t3.png",
    "Bournemouth": "https://resources.premierleague.com/premierleague/badges/70/t91.png",
    "Brighton": "https://resources.premierleague.com/premierleague/badges/70/t36.png",
    "Burnley": "https://resources.premierleague.com/premierleague/badges/70/t90.png",
    "Cardiff": "https://resources.premierleague.com/premierleague/badges/70/t97.png",
    "Chelsea": "https://resources.premierleague.com/premierleague/badges/70/t8.png",
    "Crystal Palace": "https://resources.premierleague.com/premierleague/badges/70/t31.png",
    "Everton": "https://resources.premierleague.com/premierleague/badges/70/t11.png",
    "Fulham": "https://resources.premierleague.com/premierleague/badges/70/t54.png",
    "Huddersfield": "https://resources.premierleague.com/premierleague/badges/70/t38.png",
    "Leicester": "https://resources.premierleague.com/premierleague/badges/70/t13.png",
    "Liverpool": "https://resources.premierleague.com/premierleague/badges/70/t14.png",
    "Man City": "https://resources.premierleague.com/premierleague/badges/70/t43.png",
    "Man United": "https://resources.premierleague.com/premierleague/badges/70/t1.png",
    "Newcastle": "https://resources.premierleague.com/premierleague/badges/70/t4.png",
    "Southampton": "https://resources.premierleague.com/premierleague/badges/70/t20.png",
    "Tottenham": "https://resources.premierleague.com/premierleague/badges/70/t6.png",
    "Watford": "https://resources.premierleague.com/premierleague/badges/70/t57.png",
    "West Ham": "https://resources.premierleague.com/premierleague/badges/70/t21.png",
    "Wolves": "https://resources.premierleague.com/premierleague/badges/70/t39.png",
}

# EPL logo (public SVG)
EPL_LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/f/f2/Premier_League_Logo.svg"

# Result mapping (UI)
FTR_TO_TEXT = {"H": "Home Win", "D": "Draw", "A": "Away Win"}
TEXT_TO_FTR = {"Home Win": "H", "Draw": "D", "Away Win": "A"}

# ------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------
DB_PATH = "epl_2018_2019.db"

@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data
def read_df(sql, params=()):
    return pd.read_sql_query(sql, get_conn(), params=params)

# ------------------------------------------------------------
# SIDEBAR CONTROLS
# ------------------------------------------------------------
st.sidebar.header("Controls")

story_mode = st.sidebar.toggle("Story mode", value=True)
show_debug = st.sidebar.toggle("Show debug panels", value=False)

filter_mode = st.sidebar.radio("Filter by", ["None", "Team", "Referee"], index=1)

# ------------------------------------------------------------
# LOAD BASE DATASET
# ------------------------------------------------------------
BASE_SQL = """
SELECT
  m.MatchID,
  m.MatchDate,
  t1.TeamName AS HomeTeam,
  t2.TeamName AS AwayTeam,
  m.FTHG, m.FTAG, m.FTR,
  r.RefereeName,
  m.HY, m.AY, m.HR, m.AR
FROM Matches m
JOIN Teams t1 ON m.HomeTeamID = t1.TeamID
JOIN Teams t2 ON m.AwayTeamID = t2.TeamID
JOIN Referees r ON m.RefereeID = r.RefereeID
ORDER BY m.MatchDate DESC;
"""
df_all = read_df(BASE_SQL)

teams = sorted(set(df_all["HomeTeam"]).union(df_all["AwayTeam"]))
refs = sorted(df_all["RefereeName"].unique())

selected_team = None
selected_ref = None

if filter_mode == "Team":
    selected_team = st.sidebar.selectbox("Select team", teams)
elif filter_mode == "Referee":
    selected_ref = st.sidebar.selectbox("Select referee", refs)

rows = st.sidebar.slider("Rows in table", 25, 380, 100, 25)

if selected_team and selected_team in TEAM_LOGOS:
    st.sidebar.image(TEAM_LOGOS[selected_team], width=85)

if st.sidebar.button("Reset filters"):
    st.cache_data.clear()
    st.rerun()

# ------------------------------------------------------------
# APPLY FILTERS
# ------------------------------------------------------------
df_view = df_all.copy()

if selected_team:
    df_view = df_view[
        (df_view["HomeTeam"] == selected_team) |
        (df_view["AwayTeam"] == selected_team)
    ]

if selected_ref:
    df_view = df_view[df_view["RefereeName"] == selected_ref]

# ------------------------------------------------------------
# HEADER (EPL LOGO + TITLE)
# ------------------------------------------------------------
st.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:16px;">
        <img src="{EPL_LOGO_URL}" width="60">
        <div>
            <h1 style="margin-bottom:0;">EPL 2018–2019 Match Analytics</h1>
            <div style="color:#d1d5db; font-size:0.95rem;">
                Interactive analysis of outcomes, goals, discipline, and officiating (SQLite-backed)
            </div>
        </div>
    </div>
    <hr/>
    """,
    unsafe_allow_html=True
)

if story_mode:
    st.markdown(
        """
        **What this dashboard does:**  
        Explore match results, scoring patterns, and referee-related trends from the EPL 2018–2019 season.
        All views are generated from SQL queries on a normalized SQLite database.
        """
    )
    st.caption("Branding is used for *visual inspiration only* as part of an academic project.")

# Team overview header (optional)
if selected_team and selected_team in TEAM_LOGOS:
    c1, c2 = st.columns([1, 7])
    with c1:
        st.image(TEAM_LOGOS[selected_team], width=65)
    with c2:
        st.markdown(f"### {selected_team} — Filtered Season View")

# ------------------------------------------------------------
# KPI METRICS (FILTERED)
# ------------------------------------------------------------
total_matches = int(len(df_view))
unique_teams = int(len(set(df_view["HomeTeam"]).union(df_view["AwayTeam"])))
total_goals = int((df_view["FTHG"] + df_view["FTAG"]).sum())
total_cards = int((df_view["HY"] + df_view["AY"] + df_view["HR"] + df_view["AR"]).sum())
avg_goals = round((total_goals / total_matches), 2) if total_matches else 0.0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Matches (filtered)", total_matches)
k2.metric("Teams (filtered)", unique_teams)
k3.metric("Total goals (filtered)", total_goals)
k4.metric("Total cards (filtered)", total_cards)
k5.metric("Avg goals / match", avg_goals)

if story_mode and total_matches > 0:
    st.info(
        "Tip: Use **Team** filters to see club-specific performance, or **Referee** filters to explore officiating patterns."
    )

st.divider()

# ------------------------------------------------------------
# TABS
# ------------------------------------------------------------
tab_browse, tab_analytics, tab_compare, tab_crud = st.tabs(
    ["📋 Browse", "📈 Analytics", "⚔️ Compare Teams", "✍️ CRUD Demo"]
)

# ---------------- BROWSE TAB ----------------
with tab_browse:
    st.subheader("Browse matches")
    st.caption("Use filters on the left or search below. Scroll horizontally to see all columns.")

    search = st.text_input("Search team or referee")

    df_show = df_view.copy()
    df_show["Score"] = df_show["FTHG"].astype(str) + " - " + df_show["FTAG"].astype(str)

    # OPTION 3: Replace H/D/A with readable text in the table (and CSV)
    df_show["Full-Time Result"] = df_show["FTR"].map(FTR_TO_TEXT).fillna(df_show["FTR"])

    if search:
        df_show = df_show[
            df_show["HomeTeam"].str.contains(search, case=False) |
            df_show["AwayTeam"].str.contains(search, case=False) |
            df_show["RefereeName"].str.contains(search, case=False)
        ]

    cols = ["MatchID", "MatchDate", "HomeTeam", "AwayTeam", "Score", "Full-Time Result", "RefereeName"]
    st.dataframe(df_show[cols].head(rows), width="stretch")

    st.download_button(
        "Download current view (CSV)",
        df_show[cols].to_csv(index=False).encode("utf-8"),
        "epl_filtered_matches.csv",
        "text/csv"
    )

# ---------------- ANALYTICS TAB ----------------
with tab_analytics:
    st.subheader("Team-level analytics")

    if story_mode:
        st.info("This chart aggregates goals by team (computed via SQL aggregation queries).")

    GOALS_SQL = """
    SELECT t.TeamName AS TeamName, SUM(m.FTHG + m.FTAG) AS TotalGoals
    FROM Matches m
    JOIN Teams t ON m.HomeTeamID = t.TeamID
    GROUP BY t.TeamName
    ORDER BY TotalGoals DESC;
    """
    df_goals = read_df(GOALS_SQL)

    fig, ax = plt.subplots()
    ax.bar(df_goals["TeamName"], df_goals["TotalGoals"])
    ax.set_xticks(range(len(df_goals)))
    ax.set_xticklabels(df_goals["TeamName"], rotation=90)
    ax.set_ylabel("Goals")
    ax.set_title("Total Goals by Team (EPL 2018–2019)")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)

# ---------------- COMPARE TEAMS TAB ----------------
with tab_compare:
    st.subheader("Compare two teams")
    st.caption("Quick side-by-side comparison using SQL-based aggregation.")

    default_a = "Liverpool" if "Liverpool" in teams else teams[0]
    default_b = "Man City" if "Man City" in teams else teams[1] if len(teams) > 1 else teams[0]

    c1, c2 = st.columns(2)
    with c1:
        team_a = st.selectbox("Team A", teams, index=teams.index(default_a))
    with c2:
        team_b = st.selectbox("Team B", teams, index=teams.index(default_b))

    def team_stats(team):
        q = """
        SELECT
          COUNT(*) AS Matches,
          SUM(CASE WHEN t1.TeamName = ? THEN m.FTHG ELSE m.FTAG END) AS GoalsFor,
          SUM(CASE WHEN t1.TeamName = ? THEN m.FTAG ELSE m.FTHG END) AS GoalsAgainst
        FROM Matches m
        JOIN Teams t1 ON m.HomeTeamID = t1.TeamID
        JOIN Teams t2 ON m.AwayTeamID = t2.TeamID
        WHERE t1.TeamName = ? OR t2.TeamName = ?;
        """
        return read_df(q, (team, team, team, team)).iloc[0]

    a = team_stats(team_a)
    b = team_stats(team_b)

    m1, m2, m3 = st.columns(3)
    m1.metric(f"{team_a} matches", int(a["Matches"]))
    m2.metric(f"{team_a} goals for", int(a["GoalsFor"]))
    m3.metric(f"{team_a} goals against", int(a["GoalsAgainst"]))

    n1, n2, n3 = st.columns(3)
    n1.metric(f"{team_b} matches", int(b["Matches"]))
    n2.metric(f"{team_b} goals for", int(b["GoalsFor"]))
    n3.metric(f"{team_b} goals against", int(b["GoalsAgainst"]))

# ---------------- CRUD TAB ----------------
with tab_crud:
    st.subheader("CRUD Demo (UPDATE)")
    st.info("This operation updates the local SQLite database for demonstration purposes (stores H/D/A internally).")

    c1, c2 = st.columns(2)
    with c1:
        match_id = st.number_input("MatchID", min_value=1, step=1)
    with c2:
        new_ftr_label = st.selectbox("New full-time result", ["Home Win", "Draw", "Away Win"])

    new_ftr_code = TEXT_TO_FTR[new_ftr_label]

    if st.button("Update Match Result", type="primary"):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE Matches SET FTR=? WHERE MatchID=?", (new_ftr_code, int(match_id)))
        conn.commit()

        # Clear cached reads so UI reflects updates
        st.cache_data.clear()

        st.success(f"Updated MatchID {int(match_id)} → {new_ftr_label} (stored as '{new_ftr_code}')")

        # Show updated row (proof in demo video)
        updated_sql = """
        SELECT
          m.MatchID, m.MatchDate,
          t1.TeamName AS HomeTeam, t2.TeamName AS AwayTeam,
          m.FTHG, m.FTAG, m.FTR, r.RefereeName
        FROM Matches m
        JOIN Teams t1 ON m.HomeTeamID = t1.TeamID
        JOIN Teams t2 ON m.AwayTeamID = t2.TeamID
        JOIN Referees r ON m.RefereeID = r.RefereeID
        WHERE m.MatchID = ?;
        """
        df_updated = read_df(updated_sql, (int(match_id),))
        if not df_updated.empty:
            df_updated["Full-Time Result"] = df_updated["FTR"].map(FTR_TO_TEXT).fillna(df_updated["FTR"])
            st.dataframe(
                df_updated[["MatchID", "MatchDate", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "Full-Time Result", "RefereeName"]],
                width="stretch"
            )

# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.divider()
st.caption(
    "Data source: English Premier League 2018–2019 season. "
    "Data stored in a normalized SQLite database. "
    "All analytics are computed via SQL queries at runtime."
)

if show_debug:
    st.write("Working directory:", os.getcwd())
    st.write("Database exists:", os.path.exists(DB_PATH))
