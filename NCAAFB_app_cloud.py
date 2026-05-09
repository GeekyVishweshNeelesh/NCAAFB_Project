"""
NCAAFB Data Explorer — Streamlit Cloud Version
------------------------------------------------
Reads directly from CSV files in the data/ folder.
No database connection needed — works on Streamlit Cloud.

Folder structure required:
    data/
        1_teams.csv, 2_venues.csv, 3_conferences.csv,
        4_players.csv, 5_coaches.csv, 6_seasons.csv,
        7_rankings.csv, 8_divisions.csv, 9_player_statistics.csv

Run:
    streamlit run NCAAFB_App_Cloud.py
"""

import streamlit as st
import pandas as pd
import os

# ===========================
# PAGE CONFIG
# ===========================

st.set_page_config(
    page_title="NCAAFB Data Explorer",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;600;700&family=Source+Sans+3:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }
    h1, h2, h3 { font-family: 'Oswald', sans-serif !important; letter-spacing: 0.5px; }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a1628 0%, #0d2137 100%);
        border-right: 3px solid #e8a020;
    }
    section[data-testid="stSidebar"] * { color: #f0f0f0 !important; }
    section[data-testid="stSidebar"] .stRadio label {
        font-family: 'Oswald', sans-serif !important; font-size: 15px !important;
    }
    [data-testid="metric-container"] {
        background: #0d2137; border: 1px solid #1e3a5f;
        border-left: 4px solid #e8a020; border-radius: 6px; padding: 12px 16px;
    }
    [data-testid="metric-container"] label {
        color: #e8a020 !important; font-size: 12px !important;
        text-transform: uppercase; letter-spacing: 1px;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #ffffff !important; font-size: 28px !important;
    }
    .page-header {
        background: linear-gradient(135deg, #0a1628 60%, #1a3a5c);
        border-left: 5px solid #e8a020; border-radius: 4px;
        padding: 18px 24px; margin-bottom: 24px;
    }
    .page-header h1 { color: #ffffff; margin: 0; font-size: 28px; font-family: 'Oswald', sans-serif; }
    .page-header p  { color: #9ab0c8; margin: 4px 0 0 0; font-size: 14px; }
    .sidebar-logo { text-align: center; padding: 10px 0 20px 0; border-bottom: 1px solid #1e3a5f; margin-bottom: 20px; }
    .sidebar-logo h2 { color: #e8a020 !important; font-family: 'Oswald', sans-serif !important; font-size: 22px !important; margin: 0; letter-spacing: 2px; }
    .sidebar-logo span { color: #9ab0c8 !important; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ===========================
# LOAD DATA
# ===========================

DATA_DIR = "data"

@st.cache_data
def load_all():
    teams       = pd.read_csv(os.path.join(DATA_DIR, "1_teams.csv"),               dtype=str).fillna("")
    venues      = pd.read_csv(os.path.join(DATA_DIR, "2_venues.csv"),              dtype=str).fillna("")
    conferences = pd.read_csv(os.path.join(DATA_DIR, "3_conferences.csv"),         dtype=str).fillna("")
    players     = pd.read_csv(os.path.join(DATA_DIR, "4_players.csv"),             dtype=str).fillna("")
    coaches     = pd.read_csv(os.path.join(DATA_DIR, "5_coaches.csv"),             dtype=str).fillna("")
    seasons     = pd.read_csv(os.path.join(DATA_DIR, "6_seasons.csv"),             dtype=str).fillna("")
    rankings    = pd.read_csv(os.path.join(DATA_DIR, "7_rankings.csv"),            dtype=str).fillna("")
    divisions   = pd.read_csv(os.path.join(DATA_DIR, "8_divisions.csv"),           dtype=str).fillna("")
    stats       = pd.read_csv(os.path.join(DATA_DIR, "9_player_statistics.csv"),   dtype=str).fillna("")

    # Convert numeric columns
    for col in ["capacity"]:
        venues[col] = pd.to_numeric(venues[col], errors="coerce")
    rankings["rank"] = pd.to_numeric(rankings["rank"], errors="coerce")
    rankings["week"] = pd.to_numeric(rankings["week"], errors="coerce")
    rankings["points"]   = pd.to_numeric(rankings["points"],   errors="coerce")
    rankings["fp_votes"] = pd.to_numeric(rankings["fp_votes"], errors="coerce")

    # Join teams with conferences, divisions, venues
    teams = (teams
        .merge(conferences.rename(columns={"name": "conference_name", "alias": "conference_alias"}),
               on="conference_id", how="left")
        .merge(divisions.rename(columns={"name": "division_name", "alias": "division_alias"}),
               on="division_id", how="left")
        .merge(venues[["venue_id","name","city","state"]].rename(columns={"name": "venue_name"}),
               on="venue_id", how="left")
    )
    teams.fillna("", inplace=True)

    # Join players with team info
    players = players.merge(
        teams[["team_id","name","market","conference_name"]].rename(
            columns={"name": "team_name", "market": "team_market"}),
        on="team_id", how="left"
    ).fillna("")

    # Join coaches with team + conference
    coaches = coaches.merge(
        teams[["team_id","name","market","conference_name"]].rename(
            columns={"name": "team_name", "market": "team_market"}),
        on="team_id", how="left"
    ).fillna("")

    return teams, venues, conferences, players, coaches, seasons, rankings, divisions, stats

try:
    teams, venues, conferences, players, coaches, seasons, rankings, divisions, stats = load_all()
except Exception as e:
    st.error(f"❌ Could not load data: {e}")
    st.info("Make sure all 9 CSV files are inside a 'data/' folder next to this app.")
    st.stop()

# ===========================
# SIDEBAR
# ===========================

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h2>🏈 NCAAFB</h2>
        <span>Data Explorer</span>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "🏠 Home Dashboard",
        "🧩 Teams Explorer",
        "👥 Players Explorer",
        "📅 Season Viewer",
        "🏆 Rankings Table",
        "🏟 Venue Directory",
        "🧑‍💼 Coaches Table",
        "📊 SQL Analysis",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<span style='font-size:11px; color:#9ab0c8;'>GUVI NCAAFB Project<br>NCAA Football Analytics</span>", unsafe_allow_html=True)

# ===========================
# PAGE 1 — HOME DASHBOARD
# ===========================

if page == "🏠 Home Dashboard":
    st.markdown('<div class="page-header"><h1>🏠 Home Dashboard</h1><p>Overview of the NCAA Football database</p></div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Total Teams",    len(teams))
    with c2: st.metric("Active Players", len(players[players["status"] == "ACT"]))
    with c3: st.metric("Conferences",    len(conferences))
    with c4: st.metric("Seasons",        len(seasons))
    with c5: st.metric("Total Players",  len(players))

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📋 All Teams & Conferences")
        display = teams[["market","name","alias","conference_name","division_name"]].copy()
        display.columns = ["Market","Team","Alias","Conference","Division"]
        st.dataframe(display, use_container_width=True, height=350)

    with col_b:
        st.subheader("📅 Available Seasons")
        display = seasons[["season_id","year","type_code"]].copy()
        st.dataframe(display, use_container_width=True, height=160)

        st.subheader("👥 Active Players Sample")
        active = players[players["status"] == "ACT"][
            ["first_name","last_name","position","eligibility","team_name"]
        ].head(50).copy()
        active.columns = ["First Name","Last Name","Position","Eligibility","Team"]
        st.dataframe(active, use_container_width=True, height=200)

# ===========================
# PAGE 2 — TEAMS EXPLORER
# ===========================

elif page == "🧩 Teams Explorer":
    st.markdown('<div class="page-header"><h1>🧩 Teams Explorer</h1><p>Browse and filter all NCAA Football teams</p></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    conf_opts = ["All"] + sorted([x for x in conferences["name"].unique() if x])
    div_opts  = ["All"] + sorted([x for x in divisions["name"].unique()   if x])

    with col1: sel_conf = st.selectbox("Conference", conf_opts)
    with col2: sel_div  = st.selectbox("Division",   div_opts)
    with col3: search   = st.text_input("Search by team name or alias", "")

    filtered = teams.copy()
    if sel_conf != "All": filtered = filtered[filtered["conference_name"] == sel_conf]
    if sel_div  != "All": filtered = filtered[filtered["division_name"]   == sel_div]
    if search:
        mask = (filtered["name"].str.contains(search, case=False, na=False) |
                filtered["alias"].str.contains(search, case=False, na=False) |
                filtered["market"].str.contains(search, case=False, na=False))
        filtered = filtered[mask]

    display = filtered[["market","name","alias","founded","mascot","championships_won",
                         "conference_name","division_name","venue_name","venue_city","venue_state"]].copy()
    display.columns = ["Market","Team","Alias","Founded","Mascot","Championships",
                        "Conference","Division","Venue","City","State"]
    st.markdown(f"**{len(display)} teams found**")
    st.dataframe(display, use_container_width=True, height=420)

    st.markdown("---")
    st.subheader("👕 View Team Roster")
    team_options = sorted((teams["market"] + " " + teams["name"]).tolist())
    sel_team = st.selectbox("Select a team", team_options)
    parts    = sel_team.split(" ", 1)
    team_row = teams[(teams["market"] == parts[0]) & (teams["name"] == parts[1])] if len(parts) == 2 else pd.DataFrame()
    if not team_row.empty:
        tid    = team_row["team_id"].values[0]
        roster = players[players["team_id"] == tid][
            ["first_name","last_name","position","height","weight","status","eligibility"]
        ].copy()
        roster.columns = ["First Name","Last Name","Position","Height","Weight","Status","Eligibility"]
        st.markdown(f"**{len(roster)} players on roster**")
        st.dataframe(roster, use_container_width=True, height=350)

# ===========================
# PAGE 3 — PLAYERS EXPLORER
# ===========================

elif page == "👥 Players Explorer":
    st.markdown('<div class="page-header"><h1>👥 Players Explorer</h1><p>Search and filter all NCAA Football players</p></div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    pos_opts  = ["All"] + sorted([x for x in players["position"].unique()    if x])
    stat_opts = ["All"] + sorted([x for x in players["status"].unique()      if x])
    elig_opts = ["All"] + sorted([x for x in players["eligibility"].unique() if x])

    with col1: sel_pos  = st.selectbox("Position",    pos_opts)
    with col2: sel_stat = st.selectbox("Status",      stat_opts)
    with col3: sel_elig = st.selectbox("Eligibility", elig_opts)
    with col4: p_search = st.text_input("Search by name or team", "")

    filtered = players.copy()
    if sel_pos  != "All": filtered = filtered[filtered["position"]    == sel_pos]
    if sel_stat != "All": filtered = filtered[filtered["status"]      == sel_stat]
    if sel_elig != "All": filtered = filtered[filtered["eligibility"] == sel_elig]
    if p_search:
        mask = (filtered["first_name"].str.contains(p_search, case=False, na=False) |
                filtered["last_name"].str.contains(p_search,  case=False, na=False) |
                filtered["team_name"].str.contains(p_search,  case=False, na=False))
        filtered = filtered[mask]

    display = filtered[["first_name","last_name","position","height","weight",
                         "status","eligibility","birth_place","team_name"]].head(500).copy()
    display.columns = ["First Name","Last Name","Position","Height","Weight",
                        "Status","Eligibility","Birth Place","Team"]
    st.markdown(f"**{len(filtered)} players found** (showing first 500)")
    st.dataframe(display, use_container_width=True, height=480)

# ===========================
# PAGE 4 — SEASON VIEWER
# ===========================

elif page == "📅 Season Viewer":
    st.markdown('<div class="page-header"><h1>📅 Season & Schedule Viewer</h1><p>View all available seasons and related rankings</p></div>', unsafe_allow_html=True)

    year_opts = ["All"] + sorted([x for x in seasons["year"].unique() if x], reverse=True)
    sel_year  = st.selectbox("Filter by Year", year_opts)

    filtered = seasons.copy()
    if sel_year != "All":
        filtered = filtered[filtered["year"] == sel_year]

    display = filtered[["season_id","year","type_code"]].copy()
    st.dataframe(display, use_container_width=True)

    st.markdown("---")
    st.subheader("🏆 Rankings for a Season")
    # Only show seasons that have actual rankings data
    ranking_years = rankings["season_id"].astype(str).unique().tolist()
    seasons_with_data = seasons[
        seasons["year"].astype(str).isin(ranking_years)
    ]["season_id"].tolist()

    if seasons_with_data:
        sel_season  = st.selectbox("Select Season", seasons_with_data)
        season_year = str(sel_season).split("_")[0]
        rank_df = rankings[rankings["season_id"].astype(str) == season_year][[
            "week","poll_name","rank","points","fp_votes","wins","losses"
        ]].copy()
        rank_df["rank"] = pd.to_numeric(rank_df["rank"], errors="coerce")
        rank_df["week"] = pd.to_numeric(rank_df["week"], errors="coerce")
        rank_df = rank_df.sort_values(["week","rank"])
        if not rank_df.empty:
            rank_df.columns = ["Week","Poll","Rank","Points","FP Votes","Wins","Losses"]
            st.markdown(f"**{len(rank_df)} ranking records found**")
            st.dataframe(rank_df, use_container_width=True)
        else:
            st.info("No rankings data found for this season.")
    else:
        st.info("No seasons with rankings data available.")

# ===========================
# PAGE 5 — RANKINGS TABLE
# ===========================

elif page == "🏆 Rankings Table":
    st.markdown('<div class="page-header"><h1>🏆 Rankings Table</h1><p>Weekly AP Poll rankings with filters</p></div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    # rankings.season_id is just the year e.g. '2025'
    seas_opts = ["All"] + sorted([x for x in rankings["season_id"].unique() if x], reverse=True)
    week_opts = ["All"] + sorted([int(x) for x in rankings["week"].dropna().unique()
                                   if str(x) != ""])

    with col1: sel_season = st.selectbox("Season",   seas_opts)
    with col2: sel_week   = st.selectbox("Week",     ["All"] + [str(w) for w in week_opts if w != "All"])
    with col3: rank_min   = st.number_input("Min Rank", min_value=1, max_value=25, value=1)
    with col4: rank_max   = st.number_input("Max Rank", min_value=1, max_value=25, value=25)
    poll_search = st.text_input("Search by poll name", "")

    filtered = rankings.copy()
    filtered = filtered[filtered["rank"].between(rank_min, rank_max)]
    if sel_season != "All": filtered = filtered[filtered["season_id"].astype(str) == str(sel_season)]
    if sel_week   != "All": filtered = filtered[filtered["week"] == float(sel_week)]
    if poll_search: filtered = filtered[filtered["poll_name"].str.contains(poll_search, case=False, na=False)]

    display = filtered[["season_id","week","poll_name","rank","previous_rank",
                         "points","fp_votes","wins","losses","ties"]].sort_values(["week","rank"]).copy()
    display.columns = ["Season","Week","Poll","Rank","Prev Rank","Points","FP Votes","Wins","Losses","Ties"]
    st.markdown(f"**{len(display)} records found**")
    st.dataframe(display, use_container_width=True, height=480)

# ===========================
# PAGE 6 — VENUE DIRECTORY
# ===========================

elif page == "🏟 Venue Directory":
    st.markdown('<div class="page-header"><h1>🏟 Venue Directory</h1><p>All NCAA Football stadiums and arenas</p></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    state_opts   = ["All"] + sorted([x for x in venues["state"].unique()     if x])
    roof_opts    = ["All"] + sorted([x for x in venues["roof_type"].unique() if x])
    surface_opts = ["All"] + sorted([x for x in venues["surface"].unique()   if x])

    with col1: sel_state   = st.selectbox("State",     state_opts)
    with col2: sel_roof    = st.selectbox("Roof Type", roof_opts)
    with col3: sel_surface = st.selectbox("Surface",   surface_opts)

    filtered = venues.copy()
    if sel_state   != "All": filtered = filtered[filtered["state"]     == sel_state]
    if sel_roof    != "All": filtered = filtered[filtered["roof_type"] == sel_roof]
    if sel_surface != "All": filtered = filtered[filtered["surface"]   == sel_surface]

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Venues Found", len(filtered))
    with c2:
        avg = pd.to_numeric(filtered["capacity"], errors="coerce").mean()
        st.metric("Avg Capacity", f"{int(avg):,}" if pd.notna(avg) else "N/A")
    with c3:
        mx = pd.to_numeric(filtered["capacity"], errors="coerce").max()
        st.metric("Largest Stadium", f"{int(mx):,}" if pd.notna(mx) else "N/A")

    display = filtered[["name","city","state","country","capacity","surface","roof_type","address","zip"]].copy()
    display.columns = ["Venue","City","State","Country","Capacity","Surface","Roof Type","Address","ZIP"]
    st.dataframe(display, use_container_width=True, height=450)

# ===========================
# PAGE 7 — COACHES TABLE
# ===========================

elif page == "🧑‍💼 Coaches Table":
    st.markdown('<div class="page-header"><h1>🧑‍💼 Coaches Table</h1><p>All coaching staff across NCAA Football teams</p></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1: coach_search = st.text_input("Search by coach name", "")
    with col2: team_search  = st.text_input("Search by team name",  "")

    filtered = coaches.copy()
    if coach_search: filtered = filtered[filtered["full_name"].str.contains(coach_search, case=False, na=False)]
    if team_search:
        filtered = filtered[
            filtered["team_name"].str.contains(team_search,   case=False, na=False) |
            filtered["team_market"].str.contains(team_search, case=False, na=False)
        ]

    display = filtered[["full_name","position","team_market","team_name","conference_name"]].copy()
    display.columns = ["Coach Name","Role","Market","Team","Conference"]
    st.markdown(f"**{len(display)} coaches found**")
    st.dataframe(display, use_container_width=True, height=500)

# ===========================
# PAGE 8 — SQL ANALYSIS
# ===========================

elif page == "📊 SQL Analysis":
    st.markdown('<div class="page-header"><h1>📊 SQL Analysis</h1><p>Analytical queries answering key NCAA Football insights</p></div>', unsafe_allow_html=True)

    st.info("Results computed from CSV data using pandas — equivalent to the SQL queries in queries.sql")

    # ── Q1 ──────────────────────────────────────────────────
    st.subheader("Q1 — Teams in Top 5 Rankings")
    st.code("""
SELECT team_id, COUNT(*) AS times_in_top5,
       MIN(rank) AS best_rank
FROM rankings WHERE rank <= 5
GROUP BY team_id ORDER BY times_in_top5 DESC;
    """, language="sql")
    df1 = rankings.copy()
    df1["rank"] = pd.to_numeric(df1["rank"], errors="coerce")
    df1["points"] = pd.to_numeric(df1["points"], errors="coerce")
    df1 = df1[df1["rank"] <= 5]
    if not df1.empty:
        df1_grp = df1.groupby("team_id").agg(
            times_in_top5=("rank","count"),
            best_rank=("rank","min"),
            total_points=("points","sum")
        ).reset_index().sort_values("times_in_top5", ascending=False)
        st.dataframe(df1_grp, use_container_width=True)
    else:
        st.info("No Top 5 ranking data found.")

    st.markdown("---")

    # ── Q2 ──────────────────────────────────────────────────
    st.subheader("Q2 — Ranking Points Per Team Position")
    st.code("""
SELECT season_id AS Season, CAST(rank AS UNSIGNED) AS Rank_Position,
       CAST(points AS UNSIGNED) AS Points,
       CAST(fp_votes AS UNSIGNED) AS First_Place_Votes, poll_name AS Poll
FROM rankings
ORDER BY CAST(season_id AS UNSIGNED) DESC, CAST(rank AS UNSIGNED) ASC;
    """, language="sql")
    df2 = rankings.copy()
    df2["rank"]     = pd.to_numeric(df2["rank"],     errors="coerce")
    df2["points"]   = pd.to_numeric(df2["points"],   errors="coerce")
    df2["fp_votes"] = pd.to_numeric(df2["fp_votes"], errors="coerce")
    df2 = df2[["season_id","rank","points","fp_votes","poll_name"]].copy()
    df2.columns = ["Season","Rank_Position","Points","First_Place_Votes","Poll"]
    df2 = df2.sort_values(["Season","Rank_Position"], ascending=[False,True])
    st.dataframe(df2, use_container_width=True)

    st.markdown("---")

    # ── Q3 ──────────────────────────────────────────────────
    st.subheader("Q3 — First-Place Votes Per Rank Position")
    st.code("""
SELECT CAST(rank AS UNSIGNED) AS Rank_Position, poll_name AS Poll,
       CAST(fp_votes AS UNSIGNED) AS First_Place_Votes,
       CAST(points AS UNSIGNED) AS Points, season_id AS Season
FROM rankings WHERE CAST(fp_votes AS UNSIGNED) > 0
ORDER BY First_Place_Votes DESC;
    """, language="sql")
    df3 = rankings.copy()
    df3["rank"]     = pd.to_numeric(df3["rank"],     errors="coerce")
    df3["fp_votes"] = pd.to_numeric(df3["fp_votes"], errors="coerce")
    df3["points"]   = pd.to_numeric(df3["points"],   errors="coerce")
    df3 = df3[df3["fp_votes"] > 0][["rank","poll_name","fp_votes","points","season_id"]].copy()
    df3.columns = ["Rank_Position","Poll","First_Place_Votes","Points","Season"]
    df3 = df3.sort_values("First_Place_Votes", ascending=False)
    st.dataframe(df3, use_container_width=True)

    st.markdown("---")

    # ── Q4 ──────────────────────────────────────────────────
    st.subheader("Q4 — Players Appearing in Multiple Seasons")
    st.code("""
SELECT player_id AS Player_ID, team_id AS Team_ID,
       COUNT(stat_id) AS Seasons_Played,
       SUM(games_played) AS Total_Games,
       SUM(rushing_yards) AS Total_Rushing_Yds,
       SUM(receiving_yards) AS Total_Receiving_Yds
FROM player_statistics
GROUP BY player_id, team_id
HAVING COUNT(stat_id) > 1
ORDER BY Seasons_Played DESC LIMIT 20;
    """, language="sql")
    df4 = stats.copy()
    for col in ["games_played","rushing_yards","receiving_yards",
                "rushing_touchdowns","receiving_touchdowns"]:
        df4[col] = pd.to_numeric(df4[col], errors="coerce").fillna(0)
    df4_grp = df4.groupby(["player_id","team_id"]).agg(
        Seasons_Played=("season_id","count"),
        Season_IDs=("season_id", lambda x: ", ".join(x.unique())),
        Total_Games=("games_played","sum"),
        Total_Rushing_Yds=("rushing_yards","sum"),
        Total_Receiving_Yds=("receiving_yards","sum"),
        Total_Rush_TDs=("rushing_touchdowns","sum"),
        Total_Rec_TDs=("receiving_touchdowns","sum")
    ).reset_index()
    df4_grp.columns = ["Player_ID","Team_ID","Seasons_Played","Season_IDs",
                        "Total_Games","Total_Rushing_Yds","Total_Receiving_Yds",
                        "Total_Rush_TDs","Total_Rec_TDs"]
    df4_grp = df4_grp[df4_grp["Seasons_Played"] > 1].sort_values(
        ["Seasons_Played","Total_Games"], ascending=False).head(20)
    if not df4_grp.empty:
        st.markdown(f"**{len(df4_grp)} players found across multiple seasons**")
        st.dataframe(df4_grp, use_container_width=True)
    else:
        st.info("No players found across multiple seasons in current dataset.")

    st.markdown("---")

    # ── Q5 ──────────────────────────────────────────────────
    st.subheader("Q5 — Player Position Distribution")
    st.code("""
SELECT position, COUNT(*) AS total_players,
       COUNT(DISTINCT team_id) AS teams_with_position,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM players), 2) AS percentage
FROM players WHERE position != ''
GROUP BY position ORDER BY total_players DESC;
    """, language="sql")
    df5 = players[players["position"] != ""].copy()
    total = len(df5)
    df5_grp = df5.groupby("position").agg(
        total_players=("player_id","count"),
        teams_with_position=("team_id","nunique")
    ).reset_index()
    df5_grp["percentage"] = (df5_grp["total_players"] * 100 / total).round(2)
    df5_grp = df5_grp.sort_values("total_players", ascending=False)
    st.dataframe(df5_grp, use_container_width=True)

    st.markdown("---")

    # ── BONUS Q6 ──────────────────────────────────────────────────
    st.subheader("Bonus — Top 10 Venues by Capacity")
    df6 = venues.copy()
    df6["capacity"] = pd.to_numeric(df6["capacity"], errors="coerce")
    df6 = df6[df6["capacity"] > 0].sort_values("capacity", ascending=False).head(10)
    st.dataframe(df6[["name","city","state","surface","roof_type","capacity"]], use_container_width=True)

    st.markdown("---")

    # ── BONUS Q7 ──────────────────────────────────────────────────
    st.subheader("Bonus — Conference-wise Player Distribution")
    df7 = players[players["position"] != ""].copy()
    df7["weight"] = pd.to_numeric(df7["weight"], errors="coerce")
    df7["height"] = pd.to_numeric(df7["height"], errors="coerce")
    df7_grp = df7.groupby("conference_name").agg(
        total_players=("player_id","count"),
        total_teams=("team_id","nunique"),
        avg_weight=("weight","mean"),
        avg_height=("height","mean")
    ).reset_index()
    df7_grp["avg_weight"] = df7_grp["avg_weight"].round(1)
    df7_grp["avg_height"] = df7_grp["avg_height"].round(1)
    df7_grp = df7_grp[df7_grp["conference_name"] != ""].sort_values("total_players", ascending=False)
    df7_grp.columns = ["Conference","Total Players","Total Teams","Avg Weight (lbs)","Avg Height (in)"]
    st.dataframe(df7_grp, use_container_width=True)
