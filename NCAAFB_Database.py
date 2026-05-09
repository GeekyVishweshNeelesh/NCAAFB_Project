"""
NCAAFB Database Setup Script
-----------------------------
Drops and recreates all tables, then bulk-inserts from local CSV files.
Column names verified against actual CSV headers.
"""

import pandas as pd
import pymysql
from tqdm import tqdm

# ===========================
# CONFIG
# ===========================

DB_CONFIG = {
    "host": "localhost",
    "user": "vishwesh",
    "password": "Vish1408",
    "port": 3306
}

DB_NAME = "ncaafb"

DATA_DIR = "/home/vishwesh/Documents/GUVI_Course_Projects/NCAAFB_Project"

# ===========================
# CONNECT
# ===========================

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✅ Connected to MariaDB")
except pymysql.Error as e:
    print(f"❌ Connection failed: {e}")
    raise SystemExit(1)

# ===========================
# CREATE DATABASE & SELECT IT
# ===========================

try:
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute(f"USE `{DB_NAME}`")
    print(f"✅ Using database: {DB_NAME}")
except pymysql.Error as e:
    print(f"❌ Failed to create/select database: {e}")
    conn.close()
    raise SystemExit(1)

# ===========================
# DROP OLD TABLES
# (children first to respect FK constraints)
# ===========================

DROP_ORDER = [
    "player_statistics",
    "rankings",
    "coaches",
    "players",
    "seasons",
    "teams",
    "venues",
    "divisions",
    "conferences",
]

try:
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table_name in DROP_ORDER:
        cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        print(f"  🗑  Dropped (if existed): {table_name}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    print("✅ Old tables cleared\n")
except pymysql.Error as e:
    print(f"❌ Drop failed: {e}")
    conn.close()
    raise SystemExit(1)

# ===========================
# CREATE TABLES
# ===========================

TABLE_DEFINITIONS = {

    "conferences": """
        CREATE TABLE IF NOT EXISTS conferences (
            conference_id  VARCHAR(50)  PRIMARY KEY,
            name           VARCHAR(150),
            alias          VARCHAR(50)
        )
    """,

    "divisions": """
        CREATE TABLE IF NOT EXISTS divisions (
            division_id  VARCHAR(50)  PRIMARY KEY,
            name         VARCHAR(150),
            alias        VARCHAR(50)
        )
    """,

    "venues": """
        CREATE TABLE IF NOT EXISTS venues (
            venue_id   VARCHAR(50)   PRIMARY KEY,
            name       VARCHAR(150),
            city       VARCHAR(100),
            state      VARCHAR(100),
            country    VARCHAR(100),
            zip        VARCHAR(20),
            address    VARCHAR(255),
            capacity   INT,
            surface    VARCHAR(100),
            roof_type  VARCHAR(50),
            latitude   DECIMAL(10,6),
            longitude  DECIMAL(10,6)
        )
    """,

    "teams": """
        CREATE TABLE IF NOT EXISTS teams (
            team_id           VARCHAR(50)  PRIMARY KEY,
            market            VARCHAR(100),
            name              VARCHAR(100),
            alias             VARCHAR(50),
            founded           INT,
            mascot            VARCHAR(100),
            fight_song        VARCHAR(150),
            championships_won INT          DEFAULT 0,
            conference_id     VARCHAR(50),
            division_id       VARCHAR(50),
            venue_id          VARCHAR(50),
            FOREIGN KEY (conference_id) REFERENCES conferences(conference_id),
            FOREIGN KEY (division_id)   REFERENCES divisions(division_id),
            FOREIGN KEY (venue_id)      REFERENCES venues(venue_id)
        )
    """,

    "seasons": """
        CREATE TABLE IF NOT EXISTS seasons (
            season_id  VARCHAR(50)  PRIMARY KEY,
            year       INT,
            start_date DATE         NULL,
            end_date   DATE         NULL,
            status     VARCHAR(50),
            type_code  VARCHAR(20)
        )
    """,

    "players": """
        CREATE TABLE IF NOT EXISTS players (
            player_id   VARCHAR(50)  PRIMARY KEY,
            first_name  VARCHAR(100),
            last_name   VARCHAR(100),
            full_name   VARCHAR(200),
            abbr_name   VARCHAR(100),
            birth_place VARCHAR(150),
            position    VARCHAR(50),
            height      INT,
            weight      INT,
            status      VARCHAR(50),
            eligibility VARCHAR(50),
            team_id     VARCHAR(50),
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        )
    """,

    "coaches": """
        CREATE TABLE IF NOT EXISTS coaches (
            coach_id  VARCHAR(50)  PRIMARY KEY,
            full_name VARCHAR(150),
            position  VARCHAR(100),
            team_id   VARCHAR(50),
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        )
    """,

    "rankings": """
        CREATE TABLE IF NOT EXISTS rankings (
            ranking_id     VARCHAR(50)  PRIMARY KEY,
            poll_id        VARCHAR(50),
            poll_name      VARCHAR(100),
            season_id      VARCHAR(50),
            week           VARCHAR(10),
            effective_time VARCHAR(50),
            team_id        VARCHAR(50),
            rank           INT,
            previous_rank  VARCHAR(10),
            points         INT,
            fp_votes       INT,
            wins           VARCHAR(10),
            losses         VARCHAR(10),
            ties           VARCHAR(10)
        )
    """,

    "player_statistics": """
        CREATE TABLE IF NOT EXISTS player_statistics (
            stat_id              INT  AUTO_INCREMENT PRIMARY KEY,
            player_id            VARCHAR(50),
            team_id              VARCHAR(50),
            season_id            VARCHAR(50),
            games_played         INT,
            games_started        INT,
            rushing_yards        INT,
            rushing_touchdowns   INT,
            receiving_yards      INT,
            receiving_touchdowns INT,
            kick_return_yards    INT,
            fumbles              INT
        )
    """,
}

try:
    for table_name, ddl in TABLE_DEFINITIONS.items():
        cursor.execute(ddl)
        print(f"  ✔ Table created: {table_name}")
    conn.commit()
    print("✅ All tables created\n")
except pymysql.Error as e:
    print(f"❌ Table creation failed: {e}")
    conn.close()
    raise SystemExit(1)

# ===========================
# LOAD CSV FILES
# ===========================

def load_csv(filename, fill_value=""):
    """Load a CSV from DATA_DIR, filling NaN with fill_value."""
    path = DATA_DIR + "/" + filename
    return pd.read_csv(path).fillna(fill_value)

try:
    conferences = load_csv("3.conferences.csv")
    divisions   = load_csv("8.divisions.csv")
    venues      = load_csv("2.venues.csv")
    teams       = load_csv("1.teams.csv")
    seasons     = load_csv("6.seasons.csv")
    players     = load_csv("4.players.csv")
    coaches     = load_csv("5.coaches.csv")
    rankings    = load_csv("7.rankings.csv",          fill_value=0)
    stats       = load_csv("9.player_statistics.csv", fill_value=0)
    print("✅ All CSVs loaded\n")
except Exception as e:
    print(f"❌ Failed to load CSV: {e}")
    conn.close()
    raise SystemExit(1)

# ===========================
# SAFE INSERT FUNCTION
# ===========================

def safe_insert(query, df, cols, name, use_progress=False):
    """
    Insert rows from a DataFrame into a MariaDB table.
    Rebuilds the INSERT query to match only columns that exist in the CSV.
    Converts empty strings to None so they store as NULL in MariaDB.
    """
    print(f"📥 Inserting {name}...")

    available_cols = [c for c in cols if c in df.columns]
    missing_cols   = [c for c in cols if c not in df.columns]

    if missing_cols:
        print(f"  ⚠️  Columns not in CSV (will be NULL): {missing_cols}")

    if not available_cols:
        print(f"  ❌ No matching columns for {name}. Skipping.\n")
        return

    # Rebuild INSERT with only available columns
    table_part  = query.strip().split("(")[0].strip()
    col_clause  = ", ".join(available_cols)
    val_clause  = ", ".join(["%s"] * len(available_cols))
    final_query = f"{table_part} ({col_clause}) VALUES ({val_clause})"

    # Empty string → None → NULL in MariaDB
    records = []
    for row in df[available_cols].itertuples(index=False, name=None):
        cleaned = tuple(None if v == "" else v for v in row)
        records.append(cleaned)

    try:
        iterator = tqdm(records, desc=name) if use_progress else records
        for row in iterator:
            cursor.execute(final_query, row)
        conn.commit()
        print(f"  ✔ {len(records)} rows inserted into {name}\n")
    except Exception as e:
        conn.rollback()
        print(f"  ❌ Insert failed for {name}: {e}\n")
        raise

# ===========================
# INSERT DATA (parents before children)
# ===========================

try:
    safe_insert(
        "INSERT IGNORE INTO conferences (conference_id, name, alias) VALUES (%s,%s,%s)",
        conferences,
        ["conference_id", "name", "alias"],
        "Conferences"
    )

    safe_insert(
        "INSERT IGNORE INTO divisions (division_id, name, alias) VALUES (%s,%s,%s)",
        divisions,
        ["division_id", "name", "alias"],
        "Divisions"
    )

    safe_insert(
        """INSERT IGNORE INTO venues
           (venue_id, name, city, state, country, zip, address,
            capacity, surface, roof_type, latitude, longitude)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        venues,
        ["venue_id", "name", "city", "state", "country", "zip",
         "address", "capacity", "surface", "roof_type", "latitude", "longitude"],
        "Venues"
    )

    safe_insert(
        """INSERT IGNORE INTO teams
           (team_id, market, name, alias, founded, mascot, fight_song,
            championships_won, conference_id, division_id, venue_id)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        teams,
        ["team_id", "market", "name", "alias", "founded", "mascot",
         "fight_song", "championships_won", "conference_id", "division_id", "venue_id"],
        "Teams"
    )

    safe_insert(
        "INSERT IGNORE INTO seasons (season_id, year, start_date, end_date, status, type_code) VALUES (%s,%s,%s,%s,%s,%s)",
        seasons,
        ["season_id", "year", "start_date", "end_date", "status", "type_code"],
        "Seasons"
    )

    safe_insert(
        """INSERT IGNORE INTO players
           (player_id, first_name, last_name, full_name, abbr_name, birth_place,
            position, height, weight, status, eligibility, team_id)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        players,
        ["player_id", "first_name", "last_name", "full_name", "abbr_name",
         "birth_place", "position", "height", "weight", "status", "eligibility", "team_id"],
        "Players",
        use_progress=True
    )

    safe_insert(
        "INSERT IGNORE INTO coaches (coach_id, full_name, position, team_id) VALUES (%s,%s,%s,%s)",
        coaches,
        ["coach_id", "full_name", "position", "team_id"],
        "Coaches"
    )

    safe_insert(
        """INSERT IGNORE INTO rankings
           (ranking_id, poll_id, poll_name, season_id, week, effective_time,
            team_id, rank, previous_rank, points, fp_votes, wins, losses, ties)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rankings,
        ["ranking_id", "poll_id", "poll_name", "season_id", "week", "effective_time",
         "team_id", "rank", "previous_rank", "points", "fp_votes", "wins", "losses", "ties"],
        "Rankings"
    )

    safe_insert(
        """INSERT IGNORE INTO player_statistics
           (player_id, team_id, season_id, games_played, games_started,
            rushing_yards, rushing_touchdowns, receiving_yards,
            receiving_touchdowns, kick_return_yards, fumbles)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        stats,
        ["player_id", "team_id", "season_id", "games_played", "games_started",
         "rushing_yards", "rushing_touchdowns", "receiving_yards",
         "receiving_touchdowns", "kick_return_yards", "fumbles"],
        "Player Stats",
        use_progress=True
    )

    print("🎉 SUCCESS: Database fully loaded without errors!")

except Exception as e:
    print(f"\n❌ Fatal error: {e}")

finally:
    cursor.close()
    conn.close()
    print("🔒 Connection closed.")

# ===========================
# EXPORT TO CSV
# ===========================

print("\n📤 Exporting tables to CSV...\n")

import os

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Reconnect with DictCursor for clean DataFrame export
export_conn = pymysql.connect(
    host=DB_CONFIG["host"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    port=DB_CONFIG["port"],
    database=DB_NAME,
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)

EXPORTS = [
    (
        "conferences.csv",
        "SELECT * FROM conferences ORDER BY name"
    ),
    (
        "divisions.csv",
        "SELECT * FROM divisions ORDER BY name"
    ),
    (
        "venues.csv",
        "SELECT * FROM venues ORDER BY state, name"
    ),
    (
        "teams.csv",
        """SELECT t.*,
               c.name  AS conference_name,
               d.name  AS division_name,
               v.name  AS venue_name,
               v.city  AS venue_city,
               v.state AS venue_state
           FROM teams t
           LEFT JOIN conferences c ON t.conference_id = c.conference_id
           LEFT JOIN divisions   d ON t.division_id   = d.division_id
           LEFT JOIN venues      v ON t.venue_id      = v.venue_id
           ORDER BY t.market"""
    ),
    (
        "seasons.csv",
        "SELECT * FROM seasons ORDER BY year DESC"
    ),
    (
        "players.csv",
        """SELECT p.*,
               t.name   AS team_name,
               t.market AS team_market
           FROM players p
           LEFT JOIN teams t ON p.team_id = t.team_id
           ORDER BY p.last_name"""
    ),
    (
        "coaches.csv",
        """SELECT c.*,
               t.name    AS team_name,
               t.market  AS team_market,
               conf.name AS conference_name
           FROM coaches c
           LEFT JOIN teams       t    ON c.team_id       = t.team_id
           LEFT JOIN conferences conf ON t.conference_id = conf.conference_id
           ORDER BY t.market, c.position"""
    ),
    (
        "rankings.csv",
        """SELECT r.*,
               t.name   AS team_name,
               t.market AS team_market,
               t.alias  AS team_alias
           FROM rankings r
           LEFT JOIN teams t ON r.team_id = t.team_id
           ORDER BY r.week, r.rank"""
    ),
    (
        "player_statistics.csv",
        """SELECT ps.*,
               p.first_name, p.last_name, p.position,
               t.name   AS team_name,
               t.market AS team_market
           FROM player_statistics ps
           LEFT JOIN players p ON ps.player_id = p.player_id
           LEFT JOIN teams   t ON ps.team_id   = t.team_id
           ORDER BY ps.season_id, t.name"""
    ),
]

try:
    with export_conn.cursor() as exp_cursor:
        for filename, query in EXPORTS:
            print(f"  📥 Exporting {filename}...")
            exp_cursor.execute(query)
            rows = exp_cursor.fetchall()
            df = pd.DataFrame(rows)
            filepath = os.path.join(OUTPUT_DIR, filename)
            df.to_csv(filepath, index=False)
            size_kb = os.path.getsize(filepath) / 1024
            print(f"     ✔ {len(df)} rows → {filepath}  ({size_kb:.1f} KB)")

    print(f"\n✅ All CSVs saved to '{OUTPUT_DIR}/' — ready for GitHub & Streamlit Cloud!")

except Exception as e:
    print(f"\n❌ Export failed: {e}")

finally:
    export_conn.close()
    print("🔒 Export connection closed.")
