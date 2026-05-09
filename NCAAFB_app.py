"""
NCAAFB Data Explorer — Streamlit App (Local / Evaluator Version)
-----------------------------------------------------------------
Connects to local MariaDB ncaafb database.
Run NCAAFB_Database.py first to populate the database.

Run:
    streamlit run NCAAFB_App.py
"""

import streamlit as st
import pymysql
import pandas as pd

# ===========================
# CONFIG
# ===========================

DB_CONFIG = {
    "host": "localhost",
    "user": "vishwesh",
    "password": "Vish1408",
    "port": 3306,
    "database": "ncaafb",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

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
# DB HELPERS
# ===========================

@st.cache_resource
def get_connection():
    return pymysql.connect(**DB_CONFIG)

def run_query(sql, params=None):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            rows = cursor.fetchall()
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Query error: {e}")
        return pd.DataFrame()

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
    with c1:
        n = run_query("SELECT COUNT(*) as c FROM teams")
        st.metric("Total Teams", int(n["c"][0]) if not n.empty else 0)
    with c2:
        n = run_query("SELECT COUNT(*) as c FROM players WHERE status = 'ACT'")
        st.metric("Active Players", int(n["c"][0]) if not n.empty else 0)
    with c3:
        n = run_query("SELECT COUNT(*) as c FROM conferences")
        st.metric("Conferences", int(n["c"][0]) if not n.empty else 0)
    with c4:
        n = run_query("SELECT COUNT(*) as c FROM seasons")
        st.metric("Seasons", int(n["c"][0]) if not n.empty else 0)
    with c5:
        n = run_query("SELECT COUNT(*) as c FROM players")
        st.metric("Total Players", int(n["c"][0]) if not n.empty else 0)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📋 All Teams & Conferences")
        df = run_query("""
            SELECT t.market, t.name AS team_name, t.alias,
                   c.name AS conference, d.name AS division
            FROM teams t
            LEFT JOIN conferences c ON t.conference_id = c.conference_id
            LEFT JOIN divisions   d ON t.division_id   = d.division_id
            ORDER BY c.name, t.market
        """)
        st.dataframe(df, use_container_width=True, height=350)

    with col_b:
        st.subheader("📅 Available Seasons")
        df = run_query("SELECT season_id, year, type_code FROM seasons ORDER BY year DESC")
        st.dataframe(df, use_container_width=True, height=160)

        st.subheader("👥 Active Players Sample")
        df = run_query("""
            SELECT p.first_name, p.last_name, p.position, p.eligibility, t.name AS team
            FROM players p
            LEFT JOIN teams t ON p.team_id = t.team_id
            WHERE p.status = 'ACT'
            LIMIT 50
        """)
        st.dataframe(df, use_container_width=True, height=200)

# ===========================
# PAGE 2 — TEAMS EXPLORER
# ===========================

elif page == "🧩 Teams Explorer":
    st.markdown('<div class="page-header"><h1>🧩 Teams Explorer</h1><p>Browse and filter all NCAA Football teams</p></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    conf_df = run_query("SELECT DISTINCT name FROM conferences ORDER BY name")
    div_df  = run_query("SELECT DISTINCT name FROM divisions  ORDER BY name")
    conf_opts = ["All"] + list(conf_df["name"]) if not conf_df.empty else ["All"]
    div_opts  = ["All"] + list(div_df["name"])  if not div_df.empty  else ["All"]

    with col1: sel_conf = st.selectbox("Conference", conf_opts)
    with col2: sel_div  = st.selectbox("Division",   div_opts)
    with col3: search   = st.text_input("Search by team name or alias", "")

    where_clauses, params = [], []
    if sel_conf != "All": where_clauses.append("c.name = %s");  params.append(sel_conf)
    if sel_div  != "All": where_clauses.append("d.name = %s");  params.append(sel_div)
    if search:
        where_clauses.append("(t.name LIKE %s OR t.alias LIKE %s OR t.market LIKE %s)")
        params += [f"%{search}%"] * 3
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    df = run_query(f"""
        SELECT t.market, t.name AS team_name, t.alias, t.founded,
               t.mascot, t.championships_won,
               c.name AS conference, d.name AS division,
               v.name AS venue, v.city, v.state
        FROM teams t
        LEFT JOIN conferences c ON t.conference_id = c.conference_id
        LEFT JOIN divisions   d ON t.division_id   = d.division_id
        LEFT JOIN venues      v ON t.venue_id      = v.venue_id
        {where_sql} ORDER BY t.market
    """, params or None)

    st.markdown(f"**{len(df)} teams found**")
    st.dataframe(df, use_container_width=True, height=420)

    st.markdown("---")
    st.subheader("👕 View Team Roster")
    team_names = run_query("SELECT team_id, CONCAT(market, ' ', name) AS full_name FROM teams ORDER BY market")
    if not team_names.empty:
        sel_team = st.selectbox("Select a team", team_names["full_name"])
        tid = team_names[team_names["full_name"] == sel_team]["team_id"].values[0]
        roster = run_query("""
            SELECT first_name, last_name, position, height, weight, status, eligibility
            FROM players WHERE team_id = %s ORDER BY position, last_name
        """, (tid,))
        st.markdown(f"**{len(roster)} players on roster**")
        st.dataframe(roster, use_container_width=True, height=350)

# ===========================
# PAGE 3 — PLAYERS EXPLORER
# ===========================

elif page == "👥 Players Explorer":
    st.markdown('<div class="page-header"><h1>👥 Players Explorer</h1><p>Search and filter all NCAA Football players</p></div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    pos_df  = run_query("SELECT DISTINCT position   FROM players WHERE position   != '' ORDER BY position")
    stat_df = run_query("SELECT DISTINCT status     FROM players WHERE status     != '' ORDER BY status")
    elig_df = run_query("SELECT DISTINCT eligibility FROM players WHERE eligibility != '' ORDER BY eligibility")
    pos_opts  = ["All"] + list(pos_df["position"])     if not pos_df.empty  else ["All"]
    stat_opts = ["All"] + list(stat_df["status"])      if not stat_df.empty else ["All"]
    elig_opts = ["All"] + list(elig_df["eligibility"]) if not elig_df.empty else ["All"]

    with col1: sel_pos  = st.selectbox("Position",    pos_opts)
    with col2: sel_stat = st.selectbox("Status",      stat_opts)
    with col3: sel_elig = st.selectbox("Eligibility", elig_opts)
    with col4: p_search = st.text_input("Search by name or team", "")

    where_clauses, params = [], []
    if sel_pos  != "All": where_clauses.append("p.position    = %s"); params.append(sel_pos)
    if sel_stat != "All": where_clauses.append("p.status      = %s"); params.append(sel_stat)
    if sel_elig != "All": where_clauses.append("p.eligibility = %s"); params.append(sel_elig)
    if p_search:
        where_clauses.append("(p.first_name LIKE %s OR p.last_name LIKE %s OR t.name LIKE %s)")
        params += [f"%{p_search}%"] * 3
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    df = run_query(f"""
        SELECT p.first_name, p.last_name, p.position, p.height,
               p.weight, p.status, p.eligibility, p.birth_place, t.name AS team
        FROM players p
        LEFT JOIN teams t ON p.team_id = t.team_id
        {where_sql} ORDER BY p.last_name LIMIT 500
    """, params or None)

    st.markdown(f"**{len(df)} players found** (max 500 shown)")
    st.dataframe(df, use_container_width=True, height=480)

# ===========================
# PAGE 4 — SEASON VIEWER
# ===========================

elif page == "📅 Season Viewer":
    st.markdown('<div class="page-header"><h1>📅 Season & Schedule Viewer</h1><p>View all available seasons and related rankings</p></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    year_df = run_query("SELECT DISTINCT year FROM seasons WHERE year IS NOT NULL ORDER BY year DESC")
    year_opts = ["All"] + [str(int(y)) for y in year_df["year"]] if not year_df.empty else ["All"]

    with col1: sel_year = st.selectbox("Filter by Year", year_opts)

    where_clauses, params = [], []
    if sel_year != "All": where_clauses.append("year = %s"); params.append(int(sel_year))
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    df = run_query(f"SELECT season_id, year, type_code FROM seasons {where_sql} ORDER BY year DESC", params or None)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("🏆 Rankings for a Season")
    # Only show seasons that have actual rankings data
    seasons_list = run_query("""
        SELECT DISTINCT s.season_id, s.year FROM seasons s
        WHERE s.year IN (SELECT DISTINCT CAST(season_id AS UNSIGNED) FROM rankings)
        ORDER BY s.year DESC
    """)
    if not seasons_list.empty:
        sel_season = st.selectbox("Select Season", seasons_list["season_id"])
    elif seasons_list.empty:
        st.info("No seasons with rankings data found.")
        sel_season = None
    if sel_season:
        # rankings.season_id = '2025' (just year), seasons.season_id = '2025_REG'
        season_year = sel_season.split("_")[0]
        # Fetch all rankings then filter in Python to avoid SQL type casting issues
        all_rankings = run_query("SELECT season_id, week, poll_name, rank, points, fp_votes, wins, losses FROM rankings")
        if not all_rankings.empty:
            all_rankings["rank"] = pd.to_numeric(all_rankings["rank"], errors="coerce")
            all_rankings["week"] = pd.to_numeric(all_rankings["week"], errors="coerce")
            rank_df = all_rankings[all_rankings["season_id"].astype(str) == str(season_year)]
            rank_df = rank_df.sort_values(["week","rank"])
            if not rank_df.empty:
                rank_df.columns = ["Season","Week","Poll","Rank","Points","FP Votes","Wins","Losses"]
                st.markdown(f"**{len(rank_df)} ranking records found**")
                st.dataframe(rank_df, use_container_width=True)
            else:
                st.info("No rankings data found for this season.")
        else:
            st.info("Rankings table is empty.")

# ===========================
# PAGE 5 — RANKINGS TABLE
# ===========================

elif page == "🏆 Rankings Table":
    st.markdown('<div class="page-header"><h1>🏆 Rankings Table</h1><p>Weekly AP Poll rankings with filters</p></div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    seas_df  = run_query("SELECT DISTINCT season_id FROM rankings ORDER BY season_id DESC")
    week_df  = run_query("SELECT DISTINCT week FROM rankings ORDER BY week")
    seas_opts = ["All"] + list(seas_df["season_id"].astype(str)) if not seas_df.empty else ["All"]
    week_opts = ["All"] + list(week_df["week"].astype(str))      if not week_df.empty else ["All"]

    with col1: sel_season = st.selectbox("Season", seas_opts)
    with col2: sel_week   = st.selectbox("Week",   week_opts)
    with col3: rank_min   = st.number_input("Min Rank", min_value=1, max_value=25, value=1)
    with col4: rank_max   = st.number_input("Max Rank", min_value=1, max_value=25, value=25)
    poll_search = st.text_input("Search by poll name", "")

    # Fetch ALL rankings first, then filter in Python to avoid SQL type issues
    df = run_query("""
        SELECT season_id AS season, week, poll_name,
               rank, previous_rank, points, fp_votes,
               wins, losses, ties
        FROM rankings
        ORDER BY week, rank
    """)

    if not df.empty:
        df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
        df["week"] = pd.to_numeric(df["week"], errors="coerce")
        df = df[df["rank"].between(rank_min, rank_max)]
        if sel_season != "All": df = df[df["season"].astype(str) == str(sel_season)]
        if sel_week   != "All": df = df[df["week"] == float(sel_week)]
        if poll_search: df = df[df["poll_name"].str.contains(poll_search, case=False, na=False)]
        df = df.sort_values(["week", "rank"])
        df.columns = ["Season","Week","Poll","Rank","Prev Rank","Points","FP Votes","Wins","Losses","Ties"]

    st.markdown(f"**{len(df)} records found**")
    st.dataframe(df, use_container_width=True, height=480)

# ===========================
# PAGE 6 — VENUE DIRECTORY
# ===========================

elif page == "🏟 Venue Directory":
    st.markdown('<div class="page-header"><h1>🏟 Venue Directory</h1><p>All NCAA Football stadiums and arenas</p></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    state_df   = run_query("SELECT DISTINCT state     FROM venues WHERE state     != '' ORDER BY state")
    roof_df    = run_query("SELECT DISTINCT roof_type FROM venues WHERE roof_type != '' ORDER BY roof_type")
    surface_df = run_query("SELECT DISTINCT surface   FROM venues WHERE surface   != '' ORDER BY surface")
    state_opts   = ["All"] + list(state_df["state"])      if not state_df.empty   else ["All"]
    roof_opts    = ["All"] + list(roof_df["roof_type"])    if not roof_df.empty    else ["All"]
    surface_opts = ["All"] + list(surface_df["surface"])   if not surface_df.empty else ["All"]

    with col1: sel_state   = st.selectbox("State",     state_opts)
    with col2: sel_roof    = st.selectbox("Roof Type", roof_opts)
    with col3: sel_surface = st.selectbox("Surface",   surface_opts)

    where_clauses, params = [], []
    if sel_state   != "All": where_clauses.append("state     = %s"); params.append(sel_state)
    if sel_roof    != "All": where_clauses.append("roof_type = %s"); params.append(sel_roof)
    if sel_surface != "All": where_clauses.append("surface   = %s"); params.append(sel_surface)
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    df = run_query(f"""
        SELECT name AS venue_name, city, state, country,
               capacity, surface, roof_type, address, zip
        FROM venues {where_sql} ORDER BY state, name
    """, params or None)

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Venues Found", len(df))
    with c2:
        avg = pd.to_numeric(df["capacity"], errors="coerce").mean() if not df.empty else None
        st.metric("Avg Capacity", f"{int(avg):,}" if avg and pd.notna(avg) else "N/A")
    with c3:
        mx = pd.to_numeric(df["capacity"], errors="coerce").max() if not df.empty else None
        st.metric("Largest Stadium", f"{int(mx):,}" if mx and pd.notna(mx) else "N/A")

    st.dataframe(df, use_container_width=True, height=450)

# ===========================
# PAGE 7 — COACHES TABLE
# ===========================

elif page == "🧑‍💼 Coaches Table":
    st.markdown('<div class="page-header"><h1>🧑‍💼 Coaches Table</h1><p>All coaching staff across NCAA Football teams</p></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1: coach_search = st.text_input("Search by coach name", "")
    with col2: team_search  = st.text_input("Search by team name",  "")

    where_clauses, params = [], []
    if coach_search: where_clauses.append("c.full_name LIKE %s"); params.append(f"%{coach_search}%")
    if team_search:
        where_clauses.append("(t.name LIKE %s OR t.market LIKE %s)")
        params += [f"%{team_search}%"] * 2
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    df = run_query(f"""
        SELECT c.full_name AS coach_name, c.position AS role,
               t.market, t.name AS team,
               conf.name AS conference
        FROM coaches c
        LEFT JOIN teams       t    ON c.team_id       = t.team_id
        LEFT JOIN conferences conf ON t.conference_id = conf.conference_id
        {where_sql} ORDER BY t.market, c.position
    """, params or None)

    st.markdown(f"**{len(df)} coaches found**")
    st.dataframe(df, use_container_width=True, height=500)

# ===========================
# PAGE 8 — SQL ANALYSIS
# ===========================

elif page == "📊 SQL Analysis":
    st.markdown('<div class="page-header"><h1>📊 SQL Analysis</h1><p>Analytical queries answering key NCAA Football insights</p></div>', unsafe_allow_html=True)

    st.info("These queries run live against the MariaDB database and answer the 5 analysis questions from the project requirements.")

    # ── Q1 ──────────────────────────────────────────────────
    st.subheader("Q1 — Teams in Top 5 Rankings")
    st.code("""
SELECT t.market, t.name AS team_name, t.alias, c.name AS conference,
       COUNT(r.ranking_id) AS times_in_top5,
       MIN(CAST(r.rank AS UNSIGNED)) AS best_rank
FROM rankings r
JOIN teams t       ON r.team_id       = t.team_id
JOIN conferences c ON t.conference_id = c.conference_id
WHERE CAST(r.rank AS UNSIGNED) <= 5
GROUP BY r.team_id, t.market, t.name, t.alias, c.name
ORDER BY times_in_top5 DESC, best_rank ASC;
    """, language="sql")
    df1 = run_query("""
        SELECT t.market, t.name AS team_name, t.alias,
               c.name AS conference,
               COUNT(r.ranking_id) AS times_in_top5,
               MIN(CAST(r.rank AS UNSIGNED)) AS best_rank,
               SUM(CAST(r.points AS UNSIGNED)) AS total_points
        FROM rankings r
        JOIN teams t       ON r.team_id       = t.team_id
        JOIN conferences c ON t.conference_id = c.conference_id
        WHERE CAST(r.rank AS UNSIGNED) <= 5
        GROUP BY r.team_id, t.market, t.name, t.alias, c.name
        ORDER BY times_in_top5 DESC, best_rank ASC
    """)
    if not df1.empty:
        st.dataframe(df1, use_container_width=True)
    else:
        st.warning("No Top 5 ranking data found. Rankings team_id may not match teams table.")

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
    df2 = run_query("""
        SELECT season_id                    AS Season,
               CAST(rank AS UNSIGNED)       AS Rank_Position,
               CAST(points AS UNSIGNED)     AS Points,
               CAST(fp_votes AS UNSIGNED)   AS First_Place_Votes,
               poll_name                    AS Poll
        FROM rankings
        ORDER BY CAST(season_id AS UNSIGNED) DESC,
                 CAST(rank AS UNSIGNED) ASC
    """)
    if not df2.empty:
        st.dataframe(df2, use_container_width=True)
    else:
        st.warning("No rankings data found.")

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
    df3 = run_query("""
        SELECT CAST(r.rank AS UNSIGNED)     AS Rank_Position,
               r.poll_name                  AS Poll,
               CAST(r.fp_votes AS UNSIGNED) AS First_Place_Votes,
               CAST(r.points AS UNSIGNED)   AS Points,
               r.season_id                  AS Season
        FROM rankings r
        WHERE CAST(r.fp_votes AS UNSIGNED) > 0
        ORDER BY First_Place_Votes DESC
    """)
    if not df3.empty:
        st.dataframe(df3, use_container_width=True)
    else:
        st.warning("No rankings data found.")

    st.markdown("---")


    # ── Q4 ──────────────────────────────────────────────────
    st.subheader("Q4 — Players Appearing in Multiple Seasons")
    st.code("""
SELECT player_id AS Player_ID, team_id AS Team_ID,
       COUNT(stat_id) AS Seasons_Played,
       GROUP_CONCAT(season_id ORDER BY season_id) AS Season_IDs,
       SUM(games_played) AS Total_Games,
       SUM(rushing_yards) AS Total_Rushing_Yds,
       SUM(receiving_yards) AS Total_Receiving_Yds
FROM player_statistics
GROUP BY player_id, team_id
HAVING COUNT(stat_id) > 1
ORDER BY Seasons_Played DESC, Total_Games DESC
LIMIT 20;
    """, language="sql")
    df4 = run_query("""
        SELECT ps.player_id                                         AS Player_ID,
               ps.team_id                                           AS Team_ID,
               COUNT(ps.stat_id)                                    AS Seasons_Played,
               GROUP_CONCAT(ps.season_id ORDER BY ps.season_id)     AS Season_IDs,
               SUM(ps.games_played)                                  AS Total_Games,
               SUM(ps.rushing_yards)                                 AS Total_Rushing_Yds,
               SUM(ps.receiving_yards)                               AS Total_Receiving_Yds,
               SUM(ps.rushing_touchdowns)                            AS Total_Rush_TDs,
               SUM(ps.receiving_touchdowns)                          AS Total_Rec_TDs
        FROM player_statistics ps
        GROUP BY ps.player_id, ps.team_id
        HAVING COUNT(ps.stat_id) > 1
        ORDER BY Seasons_Played DESC, Total_Games DESC
        LIMIT 20
    """)
    if not df4.empty:
        st.markdown(f"**{len(df4)} players found across multiple seasons**")
        st.dataframe(df4, use_container_width=True)
    else:
        st.info("No players found across multiple seasons in current dataset.")

    st.markdown("---")

    # ── Q5 ──────────────────────────────────────────────────
    st.subheader("Q5 — Player Position Distribution")
    st.code("""
SELECT position,
       COUNT(player_id)  AS total_players,
       COUNT(DISTINCT team_id) AS teams_with_position,
       ROUND(COUNT(player_id) * 100.0 /
             (SELECT COUNT(*) FROM players WHERE position != \'\'), 2) AS percentage
FROM players
WHERE position != \'\'
GROUP BY position
ORDER BY total_players DESC;
    """, language="sql")
    df5 = run_query("""
        SELECT position,
               COUNT(player_id)         AS total_players,
               COUNT(DISTINCT team_id)  AS teams_with_position,
               ROUND(COUNT(player_id) * 100.0 /
                     (SELECT COUNT(*) FROM players WHERE position != ''), 2) AS percentage
        FROM players
        WHERE position != ''
        GROUP BY position
        ORDER BY total_players DESC
    """)
    if not df5.empty:
        st.dataframe(df5, use_container_width=True)
    else:
        st.warning("No player position data found.")

    st.markdown("---")

    # ── BONUS Q6 ──────────────────────────────────────────────────
    st.subheader("Bonus — Top 10 Venues by Capacity")
    df6 = run_query("""
        SELECT name AS venue_name, city, state,
               surface, roof_type, capacity
        FROM venues
        WHERE capacity IS NOT NULL AND capacity > 0
        ORDER BY capacity DESC
        LIMIT 10
    """)
    if not df6.empty:
        st.dataframe(df6, use_container_width=True)

    st.markdown("---")

    # ── BONUS Q7 ──────────────────────────────────────────────────
    st.subheader("Bonus — Conference-wise Player Distribution")
    df7 = run_query("""
        SELECT c.name AS conference,
               COUNT(p.player_id)        AS total_players,
               COUNT(DISTINCT p.team_id) AS total_teams,
               ROUND(AVG(p.weight), 1)   AS avg_weight_lbs,
               ROUND(AVG(p.height), 1)   AS avg_height_inches
        FROM players p
        JOIN teams       t ON p.team_id       = t.team_id
        JOIN conferences c ON t.conference_id = c.conference_id
        WHERE p.position != ''
        GROUP BY c.name
        ORDER BY total_players DESC
    """)
    if not df7.empty:
        st.dataframe(df7, use_container_width=True)
