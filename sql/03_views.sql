-- =====================================================================
-- 03_views.sql
-- Reusable views — built once, queried everywhere (dashboard, Power BI
-- DirectQuery, ad-hoc analysis). Demonstrates the "Views" requirement
-- from Phase 4 and doubles as the semantic layer for Phase 6.
-- =====================================================================

DROP VIEW IF EXISTS vw_country_summary;
CREATE VIEW vw_country_summary AS
SELECT
    bc.country_name                                       AS country,
    COUNT(*)                                              AS total_titles,
    SUM(CASE WHEN t.type = 'Movie' THEN 1 ELSE 0 END)      AS movie_count,
    SUM(CASE WHEN t.type = 'TV Show' THEN 1 ELSE 0 END)    AS tv_show_count,
    ROUND(AVG(t.duration_minutes), 1)                      AS avg_movie_duration,
    MIN(t.release_year)                                    AS earliest_title_year,
    MAX(t.release_year)                                    AS latest_title_year
FROM bridge_country bc
JOIN titles t ON t.show_id = bc.show_id
WHERE bc.country_name <> 'Unknown'
GROUP BY bc.country_name;

DROP VIEW IF EXISTS vw_genre_summary;
CREATE VIEW vw_genre_summary AS
SELECT
    bg.genre_name                                          AS genre,
    COUNT(*)                                                AS total_titles,
    SUM(CASE WHEN t.type = 'Movie' THEN 1 ELSE 0 END)       AS movie_count,
    SUM(CASE WHEN t.type = 'TV Show' THEN 1 ELSE 0 END)     AS tv_show_count,
    ROUND(AVG(t.duration_minutes), 1)                       AS avg_movie_duration
FROM bridge_genre bg
JOIN titles t ON t.show_id = bg.show_id
GROUP BY bg.genre_name;

DROP VIEW IF EXISTS vw_yearly_additions;
CREATE VIEW vw_yearly_additions AS
SELECT
    year_added,
    type,
    COUNT(*) AS titles_added
FROM titles
WHERE year_added IS NOT NULL
GROUP BY year_added, type;

DROP VIEW IF EXISTS vw_director_rankings;
CREATE VIEW vw_director_rankings AS
SELECT
    bd.director_name                                        AS director,
    COUNT(*)                                                AS title_count,
    SUM(CASE WHEN t.type = 'Movie' THEN 1 ELSE 0 END)       AS movie_count,
    SUM(CASE WHEN t.type = 'TV Show' THEN 1 ELSE 0 END)     AS tv_show_count,
    GROUP_CONCAT(DISTINCT bg.genre_name)                     AS genres
FROM bridge_director bd
JOIN titles t ON t.show_id = bd.show_id
LEFT JOIN bridge_genre bg ON bg.show_id = bd.show_id
WHERE bd.director_name <> 'Unknown'
GROUP BY bd.director_name;

DROP VIEW IF EXISTS vw_actor_rankings;
CREATE VIEW vw_actor_rankings AS
SELECT
    bcast.cast_name                                         AS actor,
    COUNT(*)                                                AS title_count,
    SUM(CASE WHEN t.type = 'Movie' THEN 1 ELSE 0 END)       AS movie_count,
    SUM(CASE WHEN t.type = 'TV Show' THEN 1 ELSE 0 END)     AS tv_show_count
FROM bridge_cast bcast
JOIN titles t ON t.show_id = bcast.show_id
WHERE bcast.cast_name <> 'Unknown'
GROUP BY bcast.cast_name;

DROP VIEW IF EXISTS vw_rating_by_country;
CREATE VIEW vw_rating_by_country AS
SELECT
    bc.country_name AS country,
    t.rating,
    COUNT(*) AS title_count
FROM bridge_country bc
JOIN titles t ON t.show_id = bc.show_id
WHERE bc.country_name <> 'Unknown' AND t.rating IS NOT NULL
GROUP BY bc.country_name, t.rating;

DROP VIEW IF EXISTS vw_monthly_release_trend;
CREATE VIEW vw_monthly_release_trend AS
SELECT
    month_added,
    month_name_added,
    COUNT(*) AS titles_added
FROM titles
WHERE month_added IS NOT NULL
GROUP BY month_added, month_name_added;
