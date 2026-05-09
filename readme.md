# 🏈 NCAAFB Data Explorer

A sports analytics platform for NCAA Football data built using **Python**, **MariaDB**, and **Streamlit**.

Built as part of the GUVI HCL Project.

---

## 📌 Project Overview

This project extracts NCAA Football data from the **Sportradar NCAAFB API**, stores it in a relational **MariaDB** database, and visualizes it through an interactive **Streamlit** dashboard.

**Key Features:**
- 9-table normalized relational schema with FK constraints
- 533 teams, 43,394 players, 292 venues, 84 conferences across 3 seasons
- 7-page interactive Streamlit dashboard
- Analytical SQL queries for rankings, player stats, and team performance
- Deployable on Streamlit Cloud (CSV-based version)

---

## 🗂️ Project Structure

```
NCAAFB_Project/
├── data/                        # Raw CSV data files
│   ├── 1_teams.csv
│   ├── 2_venues.csv
│   ├── 3_conferences.csv
│   ├── 4_players.csv
│   ├── 5_coaches.csv
│   ├── 6_seasons.csv
│   ├── 7_rankings.csv
│   ├── 8_divisions.csv
│   └── 9_player_statistics.csv
├── NCAAFB_Database.py           # Creates MariaDB schema and loads data
├── NCAAFB_App.py                # Streamlit app (reads from MariaDB)
├── NCAAFB_App_Cloud.py          # Streamlit app (reads from CSV - Streamlit Cloud)
├── queries.sql                  # Standalone analytical SQL queries
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## ⚙️ Prerequisites

- Python 3.9+
- MariaDB 10.5+ installed and running
- pip / pipenv

---

## 🚀 Setup Instructions

### Step 1 — Clone the Repository

```bash
git clone https://github.com/GeekyVishweshNeelesh/NCAAFB_Project.git
cd NCAAFB_Project
```

### Step 2 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Set Up MariaDB

Start MariaDB and create a user:

```sql
sudo systemctl start mariadb
mysql -u root -p

-- Inside MariaDB shell:
CREATE USER 'your_username'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON *.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 4 — Configure Database Credentials

Open `NCAAFB_Database.py` and update the `DB_CONFIG` block:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "your_username",       # ← change this
    "password": "your_password",   # ← change this
    "port": 3306
}
```

Do the same in `NCAAFB_App.py`:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "your_username",       # ← change this
    "password": "your_password",   # ← change this
    "port": 3306,
    "database": "ncaafb",
    ...
}
```

### Step 5 — Load the Database

```bash
python NCAAFB_Database.py
```

Expected output:
```
✅ Connected to MariaDB
✅ Using database: ncaafb
✅ All tables created
✅ All CSVs loaded
📥 Inserting Conferences... ✔ 84 rows
📥 Inserting Divisions...   ✔ 6 rows
📥 Inserting Venues...      ✔ 292 rows
📥 Inserting Teams...       ✔ 533 rows
📥 Inserting Seasons...     ✔ 3 rows
📥 Inserting Players...     ✔ 43394 rows
📥 Inserting Coaches...     ✔ 321 rows
📥 Inserting Rankings...    ✔ 25 rows
📥 Inserting Player Stats...✔ 1353 rows
🎉 SUCCESS: Database fully loaded without errors!
```

### Step 6 — Run the Streamlit App (Local / MariaDB Version)

```bash
streamlit run NCAAFB_App.py
```

Open your browser at: **http://localhost:8501**

---

## ☁️ Streamlit Cloud Deployment

The cloud version reads directly from the CSV files in the `data/` folder — no database needed.

### Deploy on Streamlit Cloud:

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set **Main file path** to: `NCAAFB_App_Cloud.py`
6. Click **Deploy**

### Run Cloud Version Locally:

```bash
streamlit run NCAAFB_App_Cloud.py
```

---

## 🗄️ Database Schema

| Table | Description | Rows |
|---|---|---|
| `conferences` | NCAA conferences (SEC, Big Ten, etc.) | 84 |
| `divisions` | Conference divisions (I-A, I-AA, etc.) | 6 |
| `venues` | Stadium details with capacity and location | 292 |
| `teams` | All NCAA football teams | 533 |
| `seasons` | Season years and status | 3 |
| `players` | Player profiles and attributes | 43,394 |
| `coaches` | Head coaches per team | 321 |
| `rankings` | AP Poll weekly rankings | 25 |
| `player_statistics` | Season stats per player | 1,353 |

### Relationships:
- `teams` → `conferences`, `divisions`, `venues`
- `players` → `teams`
- `coaches` → `teams`
- `rankings` → references season year and team
- `player_statistics` → references player and team

---

## 📊 Analytical SQL Queries

Run the standalone queries file against your loaded database:

```bash
mysql -u your_username -p ncaafb < queries.sql
```

**Queries included:**
1. Teams maintaining Top 5 rankings
2. Ranking points per team position by season
3. First-place votes per rank position
4. Players appearing across multiple seasons
5. Player position distribution across teams
6. *(Bonus)* Top 10 venues by seating capacity
7. *(Bonus)* Conference-wise player distribution

---

## 📱 Streamlit App Pages

| Page | Description |
|---|---|
| 🏠 Home Dashboard | Summary metrics, teams overview, active players |
| 🧩 Teams Explorer | Filter by conference/division, view rosters |
| 👥 Players Explorer | Filter by position/status/eligibility |
| 📅 Season Viewer | Season list and rankings per season |
| 🏆 Rankings Table | AP Poll weekly rankings with filters |
| 🏟 Venue Directory | Stadiums filtered by state/surface/roof type |
| 🧑‍💼 Coaches Table | All coaching staff with search |
| 📊 SQL Analysis | Live analytical query results |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.9+ | Core scripting |
| MariaDB | Relational database |
| pymysql | Python-MariaDB connector |
| pandas | Data manipulation |
| Streamlit | Interactive dashboard |
| Sportradar API | Data source |
| tqdm | Progress bars |

---

## 👤 Author

**Vishwesh Neelesh**
GUVI HCL Project — Sports Analytics on NCAAFB Data
GitHub: [GeekyVishweshNeelesh](https://github.com/GeekyVishweshNeelesh)
