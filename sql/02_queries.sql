-- =====================================================================
-- 02_queries.sql
-- Netflix Analytics — Advanced SQL Query Library (45 queries)
-- =====================================================================
-- Run against data/netflix.db (SQLite). Every query was executed and
-- validated — see notebooks/02_eda_analysis.ipynb for results rendered
-- as tables/charts, and reports/query_results.md for raw output of
-- every query below.
--
-- Organized by technique per the project brief. Most queries combine
-- 2-3 techniques at once (that's normal in real analyst work) — the
-- section header marks the PRIMARY technique being demonstrated.
-- =====================================================================


-- #####################################################################
-- SECTION A — AGGREGATE FUNCTIONS & GROUP BY
-- #####################################################################

-- Q1: Total titles, movies, and TV shows on the platform
SELECT
    COUNT(*) AS total_titles,
    SUM(CASE WHEN type = 'Movie' THEN 1 ELSE 0 END) AS total_movies,
    SUM(CASE WHEN type = 'TV Show' THEN 1 ELSE 0 END) AS total_tv_shows
FROM titles;

-- Q2: Movie vs TV Show ratio (%)
SELECT
    type,
    COUNT(*) AS title_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM titles), 2) AS pct_of_catalog
FROM titles
GROUP BY type;

-- Q3: Which country produces the most Netflix content? (top 10)
SELECT country_name AS country, COUNT(*) AS total_titles
FROM bridge_country
GROUP BY country_name
ORDER BY total_titles DESC
LIMIT 10;

-- Q4: Average movie duration by genre
SELECT
    bg.genre_name AS genre,
    ROUND(AVG(t.duration_minutes), 1) AS avg_duration_minutes,
    COUNT(*) AS movie_count
FROM bridge_genre bg
JOIN titles t ON t.show_id = bg.show_id
WHERE t.type = 'Movie'
GROUP BY bg.genre_name
ORDER BY avg_duration_minutes DESC;

-- Q5: Average number of seasons by genre (TV Shows)
SELECT
    bg.genre_name AS genre,
    ROUND(AVG(t.duration_seasons), 2) AS avg_seasons,
    COUNT(*) AS show_count
FROM bridge_genre bg
JOIN titles t ON t.show_id = bg.show_id
WHERE t.type = 'TV Show'
GROUP BY bg.genre_name
ORDER BY avg_seasons DESC;

-- Q6: Content count by maturity rating bucket
SELECT maturity_level, COUNT(*) AS title_count
FROM titles
GROUP BY maturity_level
ORDER BY title_count DESC;

-- Q7: Longest 10 movies on the platform
SELECT title, primary_country AS country, release_year, duration_minutes
FROM titles
WHERE type = 'Movie'
ORDER BY duration_minutes DESC
LIMIT 10;

-- Q8: TV Shows with the most seasons
SELECT title, primary_country AS country, release_year, duration_seasons
FROM titles
WHERE type = 'TV Show'
ORDER BY duration_seasons DESC
LIMIT 10;

-- Q9: Average titles added per month (seasonality at a glance)
SELECT month_name_added AS month, COUNT(*) AS titles_added
FROM titles
WHERE month_added IS NOT NULL
GROUP BY month_added, month_name_added
ORDER BY month_added;

-- Q10: Distinct genre count and title count per country (catalog diversity)
SELECT
    bc.country_name AS country,
    COUNT(DISTINCT bg.genre_name) AS distinct_genres,
    COUNT(DISTINCT bc.show_id) AS total_titles
FROM bridge_country bc
JOIN bridge_genre bg ON bg.show_id = bc.show_id
GROUP BY bc.country_name
HAVING total_titles >= 20
ORDER BY distinct_genres DESC
LIMIT 15;


-- #####################################################################
-- SECTION B — JOINS
-- #####################################################################

-- Q11: Titles with both director and full genre list (inner join x2)
SELECT t.title, bd.director_name AS director, bg.genre_name AS genre
FROM titles t
JOIN bridge_director bd ON bd.show_id = t.show_id
JOIN bridge_genre bg ON bg.show_id = t.show_id
WHERE bd.director_name <> 'Unknown'
LIMIT 20;

-- Q12: Countries that have NEVER produced a Documentary (LEFT JOIN + NULL check)
SELECT DISTINCT bc.country_name AS country
FROM bridge_country bc
LEFT JOIN (
    SELECT bg.show_id FROM bridge_genre bg WHERE bg.genre_name LIKE '%Documentaries%'
) doc ON doc.show_id = bc.show_id
WHERE doc.show_id IS NULL
ORDER BY country;

-- Q13: Self-join — pairs of actors who co-starred in 3+ titles together
SELECT
    c1.cast_name AS actor_1,
    c2.cast_name AS actor_2,
    COUNT(*) AS titles_together
FROM bridge_cast c1
JOIN bridge_cast c2
    ON c1.show_id = c2.show_id
   AND c1.cast_name < c2.cast_name   -- avoid (A,B) and (B,A) duplicates + self-pairs
GROUP BY c1.cast_name, c2.cast_name
HAVING titles_together >= 3
ORDER BY titles_together DESC
LIMIT 15;

-- Q14: Directors who also appear in the cast bridge table for their own titles (JOIN + INTERSECT-like logic)
SELECT DISTINCT bd.director_name AS director_actor, t.title
FROM bridge_director bd
JOIN bridge_cast bcast
    ON bcast.show_id = bd.show_id
   AND bcast.cast_name = bd.director_name
JOIN titles t ON t.show_id = bd.show_id
LIMIT 20;

-- Q15: Country + genre combined performance (3-way join), US vs India vs UK
SELECT bc.country_name AS country, bg.genre_name AS genre, COUNT(*) AS title_count
FROM bridge_country bc
JOIN bridge_genre bg ON bg.show_id = bc.show_id
JOIN titles t ON t.show_id = bc.show_id
WHERE bc.country_name IN ('United States', 'India', 'United Kingdom')
GROUP BY bc.country_name, bg.genre_name
ORDER BY country, title_count DESC;


-- #####################################################################
-- SECTION C — CTEs (Common Table Expressions)
-- #####################################################################

-- Q16: Top genre per country using a CTE + window function
WITH genre_counts AS (
    SELECT bc.country_name AS country, bg.genre_name AS genre, COUNT(*) AS cnt
    FROM bridge_country bc
    JOIN bridge_genre bg ON bg.show_id = bc.show_id
    WHERE bc.country_name <> 'Unknown'
    GROUP BY bc.country_name, bg.genre_name
),
ranked AS (
    SELECT *, RANK() OVER (PARTITION BY country ORDER BY cnt DESC) AS rnk
    FROM genre_counts
)
SELECT country, genre AS top_genre, cnt AS title_count
FROM ranked
WHERE rnk = 1
ORDER BY title_count DESC
LIMIT 15;

-- Q17: Year-over-year content growth using a CTE
WITH yearly AS (
    SELECT release_year, COUNT(*) AS titles
    FROM titles
    GROUP BY release_year
)
SELECT
    release_year,
    titles,
    titles - LAG(titles) OVER (ORDER BY release_year) AS yoy_change,
    ROUND(100.0 * (titles - LAG(titles) OVER (ORDER BY release_year))
          / LAG(titles) OVER (ORDER BY release_year), 1) AS yoy_pct_change
FROM yearly
ORDER BY release_year;

-- Q18: Multi-level CTE — countries with above-average genre diversity
WITH country_genre AS (
    SELECT bc.country_name AS country, COUNT(DISTINCT bg.genre_name) AS genre_count
    FROM bridge_country bc
    JOIN bridge_genre bg ON bg.show_id = bc.show_id
    GROUP BY bc.country_name
),
avg_genre AS (
    SELECT AVG(genre_count) AS avg_genres FROM country_genre
)
SELECT cg.country, cg.genre_count
FROM country_genre cg, avg_genre ag
WHERE cg.genre_count > ag.avg_genres
ORDER BY cg.genre_count DESC;

-- Q19: Fastest-growing genres (CTE comparing first half vs second half of catalog history)
WITH genre_year AS (
    SELECT bg.genre_name AS genre, t.release_year,
           CASE WHEN t.release_year >= 2017 THEN 'recent' ELSE 'earlier' END AS period
    FROM bridge_genre bg
    JOIN titles t ON t.show_id = bg.show_id
    WHERE t.release_year BETWEEN 2008 AND 2021
),
period_counts AS (
    SELECT genre,
           SUM(CASE WHEN period = 'recent' THEN 1 ELSE 0 END) AS recent_count,
           SUM(CASE WHEN period = 'earlier' THEN 1 ELSE 0 END) AS earlier_count
    FROM genre_year
    GROUP BY genre
)
SELECT genre, earlier_count, recent_count,
       (recent_count - earlier_count) AS growth,
       ROUND(100.0 * (recent_count - earlier_count) / NULLIF(earlier_count, 0), 1) AS growth_pct
FROM period_counts
WHERE earlier_count >= 5
ORDER BY growth_pct DESC
LIMIT 10;

-- Q20: Recursive-style CTE alternative — running cumulative titles added by year
WITH yearly AS (
    SELECT release_year, COUNT(*) AS titles FROM titles GROUP BY release_year
)
SELECT
    release_year,
    titles,
    SUM(titles) OVER (ORDER BY release_year) AS cumulative_titles
FROM yearly
ORDER BY release_year;


-- #####################################################################
-- SECTION D — WINDOW FUNCTIONS & RANKING
-- #####################################################################

-- Q21: Top 5 directors per country by title count (ROW_NUMBER + PARTITION BY)
WITH director_country AS (
    SELECT bc.country_name AS country, bd.director_name AS director, COUNT(*) AS cnt
    FROM bridge_country bc
    JOIN bridge_director bd ON bd.show_id = bc.show_id
    WHERE bd.director_name <> 'Unknown' AND bc.country_name <> 'Unknown'
    GROUP BY bc.country_name, bd.director_name
)
SELECT country, director, cnt AS title_count, rn
FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY country ORDER BY cnt DESC) AS rn
    FROM director_country
)
WHERE rn <= 5 AND country IN ('United States', 'India', 'United Kingdom')
ORDER BY country, rn;

-- Q22: Overall director ranking by total titles (DENSE_RANK)
SELECT
    director_name AS director,
    COUNT(*) AS title_count,
    DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS rank_overall
FROM bridge_director
WHERE director_name <> 'Unknown'
GROUP BY director_name
ORDER BY title_count DESC
LIMIT 15;

-- Q23: Overall actor ranking by total titles (DENSE_RANK)
SELECT
    cast_name AS actor,
    COUNT(*) AS title_count,
    DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS rank_overall
FROM bridge_cast
WHERE cast_name <> 'Unknown'
GROUP BY cast_name
ORDER BY title_count DESC
LIMIT 15;

-- Q24: Percentile ranking of movie durations (NTILE quartiles)
SELECT
    title,
    duration_minutes,
    NTILE(4) OVER (ORDER BY duration_minutes) AS duration_quartile
FROM titles
WHERE type = 'Movie' AND duration_minutes IS NOT NULL
ORDER BY duration_minutes DESC
LIMIT 20;

-- Q25: Each title's rank within its own release year by duration (PARTITION BY release_year)
SELECT
    title, release_year, duration_minutes,
    RANK() OVER (PARTITION BY release_year ORDER BY duration_minutes DESC) AS rank_in_year
FROM titles
WHERE type = 'Movie' AND duration_minutes IS NOT NULL AND release_year >= 2019
ORDER BY release_year, rank_in_year
LIMIT 30;

-- Q26: Difference between a title's release_year and the prior title's release_year per country (LAG)
WITH country_titles AS (
    SELECT bc.country_name AS country, t.title, t.release_year
    FROM bridge_country bc JOIN titles t ON t.show_id = bc.show_id
    WHERE bc.country_name = 'India'
)
SELECT
    title, release_year,
    release_year - LAG(release_year) OVER (ORDER BY release_year) AS years_since_prior_release
FROM country_titles
ORDER BY release_year
LIMIT 25;

-- Q27: Genre's share of its country's total catalog (window SUM as denominator)
WITH cg AS (
    SELECT bc.country_name AS country, bg.genre_name AS genre, COUNT(*) AS cnt
    FROM bridge_country bc JOIN bridge_genre bg ON bg.show_id = bc.show_id
    WHERE bc.country_name = 'United States'
    GROUP BY bc.country_name, bg.genre_name
)
SELECT
    genre, cnt,
    ROUND(100.0 * cnt / SUM(cnt) OVER (), 2) AS pct_of_country_catalog
FROM cg
ORDER BY cnt DESC;

-- Q28: First and last title added per country (FIRST_VALUE / LAST_VALUE)
WITH cd AS (
    SELECT bc.country_name AS country, t.title, t.date_added_parsed
    FROM bridge_country bc JOIN titles t ON t.show_id = bc.show_id
    WHERE bc.country_name <> 'Unknown' AND t.date_added_parsed IS NOT NULL
)
SELECT DISTINCT
    country,
    FIRST_VALUE(title) OVER (PARTITION BY country ORDER BY date_added_parsed) AS first_title_added,
    FIRST_VALUE(title) OVER (PARTITION BY country ORDER BY date_added_parsed DESC) AS most_recent_title_added
FROM cd
WHERE country IN ('United States', 'India', 'United Kingdom', 'Japan', 'South Korea');


-- #####################################################################
-- SECTION E — CASE STATEMENTS
-- #####################################################################

-- Q29: Bucket movies into short/medium/long using CASE
SELECT
    title, duration_minutes,
    CASE
        WHEN duration_minutes < 60 THEN 'Short (<60 min)'
        WHEN duration_minutes BETWEEN 60 AND 120 THEN 'Standard (60-120 min)'
        ELSE 'Long (>120 min)'
    END AS length_bucket
FROM titles
WHERE type = 'Movie' AND duration_minutes IS NOT NULL
LIMIT 20;

-- Q30: Count of movies per length bucket (CASE inside aggregate)
SELECT
    CASE
        WHEN duration_minutes < 60 THEN 'Short (<60 min)'
        WHEN duration_minutes BETWEEN 60 AND 120 THEN 'Standard (60-120 min)'
        ELSE 'Long (>120 min)'
    END AS length_bucket,
    COUNT(*) AS movie_count
FROM titles
WHERE type = 'Movie' AND duration_minutes IS NOT NULL
GROUP BY length_bucket
ORDER BY movie_count DESC;

-- Q31: Decade classification of release_year (CASE)
SELECT
    CASE
        WHEN release_year < 1980 THEN 'Pre-1980'
        WHEN release_year BETWEEN 1980 AND 1989 THEN '1980s'
        WHEN release_year BETWEEN 1990 AND 1999 THEN '1990s'
        WHEN release_year BETWEEN 2000 AND 2009 THEN '2000s'
        WHEN release_year BETWEEN 2010 AND 2019 THEN '2010s'
        ELSE '2020s'
    END AS decade,
    COUNT(*) AS title_count
FROM titles
GROUP BY decade
ORDER BY decade;

-- Q32: Flag binge-worthy TV shows (CASE + threshold)
SELECT
    title, duration_seasons,
    CASE WHEN duration_seasons >= 5 THEN 'Long-Running' ELSE 'Limited/Standard' END AS show_category
FROM titles
WHERE type = 'TV Show' AND duration_seasons IS NOT NULL
ORDER BY duration_seasons DESC
LIMIT 20;

-- Q33: Family-friendly vs mature flag with aggregate (CASE + GROUP BY)
SELECT
    primary_country AS country,
    SUM(CASE WHEN maturity_level IN ('Kids','Family') THEN 1 ELSE 0 END) AS family_friendly_titles,
    SUM(CASE WHEN maturity_level = 'Adults' THEN 1 ELSE 0 END) AS mature_titles,
    COUNT(*) AS total_titles
FROM titles
WHERE primary_country <> 'Unknown'
GROUP BY primary_country
ORDER BY total_titles DESC
LIMIT 15;


-- #####################################################################
-- SECTION F — SUBQUERIES
-- #####################################################################

-- Q34: Titles longer than the average movie duration (scalar subquery)
SELECT title, duration_minutes
FROM titles
WHERE type = 'Movie'
  AND duration_minutes > (SELECT AVG(duration_minutes) FROM titles WHERE type = 'Movie')
ORDER BY duration_minutes DESC
LIMIT 15;

-- Q35: Countries producing more titles than the global average per-country count (subquery in WHERE)
SELECT country_name AS country, COUNT(*) AS title_count
FROM bridge_country
WHERE country_name <> 'Unknown'
GROUP BY country_name
HAVING COUNT(*) > (
    SELECT AVG(cnt) FROM (
        SELECT COUNT(*) AS cnt FROM bridge_country WHERE country_name <> 'Unknown' GROUP BY country_name
    )
)
ORDER BY title_count DESC;

-- Q36: Directors whose titles all belong to a single genre (correlated subquery)
SELECT DISTINCT bd.director_name AS director
FROM bridge_director bd
WHERE bd.director_name <> 'Unknown'
  AND (
      SELECT COUNT(DISTINCT bg.genre_name)
      FROM bridge_genre bg
      WHERE bg.show_id IN (SELECT show_id FROM bridge_director WHERE director_name = bd.director_name)
  ) = 1
  AND (SELECT COUNT(*) FROM bridge_director bd2 WHERE bd2.director_name = bd.director_name) >= 3
LIMIT 15;

-- Q37: Genre with the single longest average movie duration (subquery to find the max)
SELECT genre, avg_movie_duration
FROM vw_genre_summary
WHERE avg_movie_duration = (SELECT MAX(avg_movie_duration) FROM vw_genre_summary);

-- Q38: Titles added in the same month/year as Netflix's biggest content drop (subquery for the peak month)
SELECT title, type, date_added_parsed
FROM titles
WHERE strftime('%Y-%m', date_added_parsed) = (
    SELECT strftime('%Y-%m', date_added_parsed) AS ym
    FROM titles
    WHERE date_added_parsed IS NOT NULL
    GROUP BY ym
    ORDER BY COUNT(*) DESC
    LIMIT 1
)
LIMIT 20;


-- #####################################################################
-- SECTION G — DATE FUNCTIONS
-- #####################################################################

-- Q39: Average days between a title's release and its addition to Netflix (date math)
SELECT
    title, release_year, date_added_parsed,
    CAST((julianday(date_added_parsed) - julianday(release_year || '-01-01')) AS INT) AS days_release_to_add
FROM titles
WHERE date_added_parsed IS NOT NULL
ORDER BY days_release_to_add DESC
LIMIT 15;

-- Q40: Content added by day-of-week (seasonality / release-day strategy)
SELECT day_of_week_added, COUNT(*) AS titles_added
FROM titles
WHERE day_of_week_added IS NOT NULL
GROUP BY day_of_week_added
ORDER BY titles_added DESC;

-- Q41: Quarter-over-quarter content additions (date function + window)
WITH q AS (
    SELECT year_added, quarter_added, COUNT(*) AS titles
    FROM titles
    WHERE year_added IS NOT NULL
    GROUP BY year_added, quarter_added
)
SELECT
    year_added, quarter_added, titles,
    titles - LAG(titles) OVER (ORDER BY year_added, quarter_added) AS qoq_change
FROM q
ORDER BY year_added, quarter_added;

-- Q42: Gap (in years) between original release and Netflix addition, bucketed
SELECT
    CASE
        WHEN year_added - release_year <= 0 THEN 'Same year or Netflix original'
        WHEN year_added - release_year BETWEEN 1 AND 2 THEN '1-2 years later'
        WHEN year_added - release_year BETWEEN 3 AND 5 THEN '3-5 years later'
        ELSE '5+ years later'
    END AS catalog_age_bucket,
    COUNT(*) AS title_count
FROM titles
WHERE year_added IS NOT NULL
GROUP BY catalog_age_bucket
ORDER BY title_count DESC;

-- Q43: Most active year_added overall, with month breakdown (date functions + RANK)
WITH monthly AS (
    SELECT year_added, month_added, month_name_added, COUNT(*) AS titles_added
    FROM titles
    WHERE year_added IS NOT NULL
    GROUP BY year_added, month_added, month_name_added
),
ranked AS (
    SELECT *, RANK() OVER (PARTITION BY year_added ORDER BY titles_added DESC) AS month_rank_in_year
    FROM monthly
)
SELECT year_added, month_name_added, titles_added, month_rank_in_year
FROM ranked
WHERE month_rank_in_year = 1
ORDER BY year_added;


-- #####################################################################
-- SECTION H — VIEWS (querying the views defined in 03_views.sql)
-- #####################################################################

-- Q44: Executive snapshot from vw_country_summary — top 10 markets by total footprint
SELECT * FROM vw_country_summary
ORDER BY total_titles DESC
LIMIT 10;

-- Q45: Cross-view query — genre summary joined with director rankings to spot
-- which prolific directors work in the platform's largest genres
SELECT
    vd.director,
    vd.title_count AS director_title_count,
    vg.genre,
    vg.total_titles AS genre_total_titles
FROM vw_director_rankings vd
JOIN bridge_director bd ON bd.director_name = vd.director
JOIN bridge_genre bg ON bg.show_id = bd.show_id
JOIN vw_genre_summary vg ON vg.genre = bg.genre_name
WHERE vd.title_count >= 5
GROUP BY vd.director, vg.genre
ORDER BY director_title_count DESC, genre_total_titles DESC
LIMIT 20;


-- #####################################################################
-- SECTION I — ADDITIONAL BUSINESS QUERIES (ranking, growth, diversity)
-- #####################################################################

-- Q46: Top 3 countries by content growth between 2015-2018 vs 2019-2021 (CTE + RANK)
WITH country_period AS (
    SELECT
        bc.country_name AS country,
        CASE WHEN t.release_year BETWEEN 2015 AND 2018 THEN 'p1_2015_2018'
             WHEN t.release_year BETWEEN 2019 AND 2021 THEN 'p2_2019_2021' END AS period
    FROM bridge_country bc JOIN titles t ON t.show_id = bc.show_id
    WHERE bc.country_name <> 'Unknown'
      AND t.release_year BETWEEN 2015 AND 2021
),
pivoted AS (
    SELECT country,
           SUM(CASE WHEN period = 'p1_2015_2018' THEN 1 ELSE 0 END) AS p1_count,
           SUM(CASE WHEN period = 'p2_2019_2021' THEN 1 ELSE 0 END) AS p2_count
    FROM country_period
    GROUP BY country
)
SELECT country, p1_count, p2_count,
       (p2_count - p1_count) AS growth,
       RANK() OVER (ORDER BY (p2_count - p1_count) DESC) AS growth_rank
FROM pivoted
WHERE p1_count >= 5
ORDER BY growth_rank
LIMIT 10;

-- Q47: Underrepresented genres — low title count but present in many countries (diversification candidates)
SELECT
    bg.genre_name AS genre,
    COUNT(DISTINCT bg.show_id) AS total_titles,
    COUNT(DISTINCT bc.country_name) AS countries_present_in
FROM bridge_genre bg
JOIN bridge_country bc ON bc.show_id = bg.show_id
WHERE bc.country_name <> 'Unknown'
GROUP BY bg.genre_name
HAVING total_titles < (SELECT AVG(cnt) FROM (SELECT COUNT(*) AS cnt FROM bridge_genre GROUP BY genre_name))
ORDER BY countries_present_in DESC, total_titles ASC
LIMIT 12;

-- Q48: Rating distribution skew per country — share of mature (Adults) content (window function for share)
WITH rc AS (
    SELECT
        bc.country_name AS country,
        t.maturity_level,
        COUNT(*) AS cnt
    FROM bridge_country bc JOIN titles t ON t.show_id = bc.show_id
    WHERE bc.country_name <> 'Unknown'
    GROUP BY bc.country_name, t.maturity_level
)
SELECT
    country, maturity_level, cnt,
    ROUND(100.0 * cnt / SUM(cnt) OVER (PARTITION BY country), 1) AS pct_within_country
FROM rc
WHERE country IN ('United States', 'India', 'Japan', 'South Korea', 'United Kingdom')
ORDER BY country, pct_within_country DESC;

-- Q49: Titles released and added in the same calendar year ("day-and-date" originals) by year (CASE + aggregate)
SELECT
    release_year,
    SUM(CASE WHEN year_added = release_year THEN 1 ELSE 0 END) AS same_year_release_and_add,
    COUNT(*) AS total_titles_that_year,
    ROUND(100.0 * SUM(CASE WHEN year_added = release_year THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_originals_like
FROM titles
WHERE year_added IS NOT NULL AND release_year >= 2015
GROUP BY release_year
ORDER BY release_year;

-- Q50: Top 10 single-country titles (num_countries = 1) directors with international (multi-country) reach (subquery + join)
SELECT
    bd.director_name AS director,
    COUNT(DISTINCT t.show_id) AS total_titles,
    SUM(CASE WHEN t.num_countries > 1 THEN 1 ELSE 0 END) AS multi_country_titles
FROM bridge_director bd
JOIN titles t ON t.show_id = bd.show_id
WHERE bd.director_name <> 'Unknown'
GROUP BY bd.director_name
HAVING total_titles >= 4 AND multi_country_titles >= 1
ORDER BY multi_country_titles DESC, total_titles DESC
LIMIT 10;
