-- ============================================================
-- NCAAFB Data Explorer — Analytical SQL Queries
-- Database: ncaafb (MariaDB)
-- ============================================================
-- Run: mysql -u YOUR_USERNAME -p ncaafb < queries.sql
-- ============================================================


-- ============================================================
-- Q1. Which teams have maintained Top 5 rankings?
-- ============================================================
SELECT '===========================================' AS '';
SELECT 'Q1: Teams in Top 5 Rankings' AS '';
SELECT '===========================================' AS '';

SELECT
    t.market                                    AS Market,
    t.name                                      AS Team,
    t.alias                                     AS Alias,
    c.name                                      AS Conference,
    COUNT(r.ranking_id)                         AS Times_In_Top5,
    MIN(CAST(r.rank AS UNSIGNED))               AS Best_Rank,
    SUM(CAST(r.points AS UNSIGNED))             AS Total_Points
FROM rankings r
JOIN teams t        ON r.team_id       = t.team_id
JOIN conferences c  ON t.conference_id = c.conference_id
WHERE CAST(r.rank AS UNSIGNED) <= 5
GROUP BY r.team_id, t.market, t.name, t.alias, c.name
ORDER BY Times_In_Top5 DESC, Best_Rank ASC;


-- ============================================================
-- Q2. Ranking points per team position by season
-- ============================================================
SELECT '===========================================' AS '';
SELECT 'Q2: Ranking Points Per Team Position (Season 2025)' AS '';
SELECT '===========================================' AS '';

SELECT
    season_id                                           AS Season,
    CAST(rank AS UNSIGNED)                              AS Rank_Position,
    CAST(points AS UNSIGNED)                            AS Points,
    CAST(fp_votes AS UNSIGNED)                          AS First_Place_Votes,
    poll_name                                           AS Poll
FROM rankings
ORDER BY CAST(season_id AS UNSIGNED) DESC,
         CAST(rank AS UNSIGNED) ASC;


-- ============================================================
-- Q3. First-place votes per rank position
-- ============================================================
SELECT '===========================================' AS '';
SELECT 'Q3: First-Place Votes Per Rank Position' AS '';
SELECT '===========================================' AS '';

SELECT
    CAST(rank AS UNSIGNED)                              AS Rank_Position,
    poll_name                                           AS Poll,
    CAST(fp_votes AS UNSIGNED)                          AS First_Place_Votes,
    CAST(points AS UNSIGNED)                            AS Points,
    season_id                                           AS Season
FROM rankings
WHERE CAST(fp_votes AS UNSIGNED) > 0
ORDER BY First_Place_Votes DESC;


-- ============================================================
-- Q4. Players appearing in multiple seasons for same team
-- ============================================================
SELECT '===========================================' AS '';
SELECT 'Q4: Players Across Multiple Seasons' AS '';
SELECT '===========================================' AS '';

SELECT
    ps.player_id                                        AS Player_ID,
    ps.team_id                                          AS Team_ID,
    COUNT(ps.stat_id)                                   AS Seasons_Played,
    GROUP_CONCAT(ps.season_id ORDER BY ps.season_id)    AS Season_IDs,
    SUM(ps.games_played)                                AS Total_Games,
    SUM(ps.rushing_yards)                               AS Total_Rushing_Yds,
    SUM(ps.receiving_yards)                             AS Total_Receiving_Yds,
    SUM(ps.rushing_touchdowns)                          AS Total_Rush_TDs,
    SUM(ps.receiving_touchdowns)                        AS Total_Rec_TDs
FROM player_statistics ps
GROUP BY ps.player_id, ps.team_id
HAVING COUNT(ps.stat_id) > 1
ORDER BY Seasons_Played DESC, Total_Games DESC
LIMIT 20;


-- ============================================================
-- Q5. Most common player positions and distribution
-- ============================================================
SELECT '===========================================' AS '';
SELECT 'Q5: Player Position Distribution' AS '';
SELECT '===========================================' AS '';

SELECT
    position                                            AS Position,
    COUNT(player_id)                                    AS Total_Players,
    COUNT(DISTINCT team_id)                             AS Teams_With_Position,
    ROUND(COUNT(player_id) * 100.0 /
          (SELECT COUNT(*) FROM players
           WHERE position != ''), 2)                    AS Percentage
FROM players
WHERE position != ''
GROUP BY position
ORDER BY Total_Players DESC;


-- ============================================================
-- BONUS Q6. Top 10 venues by seating capacity
-- ============================================================
SELECT '===========================================' AS '';
SELECT 'Bonus Q6: Top 10 Venues by Capacity' AS '';
SELECT '===========================================' AS '';

SELECT
    name                                                AS Venue,
    city                                                AS City,
    state                                               AS State,
    surface                                             AS Surface,
    roof_type                                           AS Roof_Type,
    capacity                                            AS Capacity
FROM venues
WHERE capacity IS NOT NULL AND capacity > 0
ORDER BY capacity DESC
LIMIT 10;


-- ============================================================
-- BONUS Q7. Conference-wise player count and averages
-- ============================================================
SELECT '===========================================' AS '';
SELECT 'Bonus Q7: Conference-wise Player Distribution' AS '';
SELECT '===========================================' AS '';

SELECT
    c.name                                              AS Conference,
    COUNT(p.player_id)                                  AS Total_Players,
    COUNT(DISTINCT p.team_id)                           AS Total_Teams,
    ROUND(AVG(p.weight), 1)                             AS Avg_Weight_lbs,
    ROUND(AVG(p.height), 1)                             AS Avg_Height_inches
FROM players p
JOIN teams       t ON p.team_id       = t.team_id
JOIN conferences c ON t.conference_id = c.conference_id
WHERE p.position != ''
GROUP BY c.name
ORDER BY Total_Players DESC;

SELECT '===========================================' AS '';
SELECT 'All queries executed successfully.' AS '';
SELECT '===========================================' AS '';
