# Netflix Analytics — SQL Query Results

Executed 50 queries from `sql/02_queries.sql` against `data/netflix.db`.


## Q1: Total titles, movies, and TV shows on the platform

```sql
SELECT
    COUNT(*) AS total_titles,
    SUM(CASE WHEN type = 'Movie' THEN 1 ELSE 0 END) AS total_movies,
    SUM(CASE WHEN type = 'TV Show' THEN 1 ELSE 0 END) AS total_tv_shows
FROM titles;
```

**Rows returned:** 1

|   total_titles |   total_movies |   total_tv_shows |
|---------------:|---------------:|-----------------:|
|           7786 |           5376 |             2410 |



## Q2: Movie vs TV Show ratio (%)

```sql
SELECT
    type,
    COUNT(*) AS title_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM titles), 2) AS pct_of_catalog
FROM titles
GROUP BY type;
```

**Rows returned:** 2

| type    |   title_count |   pct_of_catalog |
|:--------|--------------:|-----------------:|
| Movie   |          5376 |            69.05 |
| TV Show |          2410 |            30.95 |



## Q3: Which country produces the most Netflix content? (top 10)

```sql
SELECT country_name AS country, COUNT(*) AS total_titles
FROM bridge_country
GROUP BY country_name
ORDER BY total_titles DESC
LIMIT 10;
```

**Rows returned:** 10

| country        |   total_titles |
|:---------------|---------------:|
| United States  |           3297 |
| India          |            990 |
| United Kingdom |            723 |
| Canada         |            412 |
| France         |            349 |
| Japan          |            287 |
| Spain          |            215 |
| South Korea    |            212 |
| Germany        |            199 |
| Mexico         |            154 |



## Q4: Average movie duration by genre

```sql
SELECT
    bg.genre_name AS genre,
    ROUND(AVG(t.duration_minutes), 1) AS avg_duration_minutes,
    COUNT(*) AS movie_count
FROM bridge_genre bg
JOIN titles t ON t.show_id = bg.show_id
WHERE t.type = 'Movie'
GROUP BY bg.genre_name
ORDER BY avg_duration_minutes DESC;
```

**Rows returned:** 20

| genre                |   avg_duration_minutes |   movie_count |
|:---------------------|-----------------------:|--------------:|
| Classic Movies       |                  115.6 |           103 |
| Dramas               |                  113.4 |          2105 |
| Action & Adventure   |                  113.3 |           721 |
| International Movies |                  110.8 |          2436 |
| Romantic Movies      |                  110.7 |           531 |
| Music & Musicals     |                  108.7 |           321 |
| Thrillers            |                  106.9 |           490 |
| Sci-Fi & Fantasy     |                  105.8 |           218 |
| Faith & Spirituality |                  105.2 |            57 |
| Cult Movies          |                  104.7 |            59 |



## Q5: Average number of seasons by genre (TV Shows)

```sql
SELECT
    bg.genre_name AS genre,
    ROUND(AVG(t.duration_seasons), 2) AS avg_seasons,
    COUNT(*) AS show_count
FROM bridge_genre bg
JOIN titles t ON t.show_id = bg.show_id
WHERE t.type = 'TV Show'
GROUP BY bg.genre_name
ORDER BY avg_seasons DESC;
```

**Rows returned:** 22

| genre                        |   avg_seasons |   show_count |
|:-----------------------------|--------------:|-------------:|
| Classic & Cult TV            |          5.89 |           27 |
| TV Sci-Fi & Fantasy          |          2.71 |           76 |
| TV Action & Adventure        |          2.47 |          150 |
| Teen TV Shows                |          2.23 |           60 |
| TV Comedies                  |          2.19 |          525 |
| TV Mysteries                 |          2.18 |           90 |
| TV Thrillers                 |          2.16 |           50 |
| TV Horror                    |          2.12 |           69 |
| Kids' TV                     |          1.95 |          414 |
| Stand-Up Comedy & Talk Shows |          1.87 |           52 |



## Q6: Content count by maturity rating bucket

```sql
SELECT maturity_level, COUNT(*) AS title_count
FROM titles
GROUP BY maturity_level
ORDER BY title_count DESC;
```

**Rows returned:** 5

| maturity_level   |   title_count |
|:-----------------|--------------:|
| Adults           |          3530 |
| Teens            |          2317 |
| Family           |          1053 |
| Kids             |           790 |
| Unrated          |            96 |



## Q7: Longest 10 movies on the platform

```sql
SELECT title, primary_country AS country, release_year, duration_minutes
FROM titles
WHERE type = 'Movie'
ORDER BY duration_minutes DESC
LIMIT 10;
```

**Rows returned:** 10

| title                      | country       |   release_year |   duration_minutes |
|:---------------------------|:--------------|---------------:|-------------------:|
| Black Mirror: Bandersnatch | United States |           2018 |                312 |
| The School of Mischief     | Egypt         |           1973 |                253 |
| No Longer kids             | Egypt         |           1979 |                237 |
| Lock Your Girls In         | Unknown       |           1982 |                233 |
| Raya and Sakina            | Unknown       |           1984 |                230 |
| Sangam                     | India         |           1964 |                228 |
| Lagaan                     | India         |           2001 |                224 |
| Jodhaa Akbar               | India         |           2008 |                214 |
| Kabhi Khushi Kabhie Gham   | India         |           2001 |                209 |
| The Irishman               | United States |           2019 |                209 |



## Q8: TV Shows with the most seasons

```sql
SELECT title, primary_country AS country, release_year, duration_seasons
FROM titles
WHERE type = 'TV Show'
ORDER BY duration_seasons DESC
LIMIT 10;
```

**Rows returned:** 10

| title                  | country       |   release_year |   duration_seasons |
|:-----------------------|:--------------|---------------:|-------------------:|
| Grey's Anatomy         | United States |           2019 |                 16 |
| NCIS                   | United States |           2017 |                 15 |
| Supernatural           | United States |           2019 |                 15 |
| COMEDIANS of the world | United States |           2019 |                 13 |
| Red vs. Blue           | United States |           2015 |                 13 |
| Criminal Minds         | United States |           2017 |                 12 |
| Trailer Park Boys      | Canada        |           2018 |                 12 |
| Cheers                 | United States |           1992 |                 11 |
| Frasier                | United States |           2003 |                 11 |
| Heartland              | Canada        |           2017 |                 11 |



## Q9: Average titles added per month (seasonality at a glance)

```sql
SELECT month_name_added AS month, COUNT(*) AS titles_added
FROM titles
WHERE month_added IS NOT NULL
GROUP BY month_added, month_name_added
ORDER BY month_added;
```

**Rows returned:** 12

| month     |   titles_added |
|:----------|---------------:|
| January   |            757 |
| February  |            472 |
| March     |            669 |
| April     |            601 |
| May       |            543 |
| June      |            542 |
| July      |            600 |
| August    |            618 |
| September |            619 |
| October   |            784 |



## Q10: Distinct genre count and title count per country (catalog diversity)

```sql
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
```

**Rows returned:** 15

| country        |   distinct_genres |   total_titles |
|:---------------|------------------:|---------------:|
| United States  |                42 |           3297 |
| Canada         |                37 |            412 |
| United Kingdom |                37 |            723 |
| France         |                35 |            349 |
| India          |                35 |            990 |
| Australia      |                34 |            144 |
| Japan          |                34 |            287 |
| Germany        |                32 |            199 |
| Spain          |                31 |            215 |
| China          |                30 |            147 |



## Q11: Titles with both director and full genre list (inner join x2)

```sql
SELECT t.title, bd.director_name AS director, bg.genre_name AS genre
FROM titles t
JOIN bridge_director bd ON bd.show_id = t.show_id
JOIN bridge_genre bg ON bg.show_id = t.show_id
WHERE bd.director_name <> 'Unknown'
LIMIT 20;
```

**Rows returned:** 20

| title   | director          | genre                  |
|:--------|:------------------|:-----------------------|
| 7:19    | Jorge Michel Grau | Dramas                 |
| 7:19    | Jorge Michel Grau | International Movies   |
| 23:59   | Gilbert Chan      | Horror Movies          |
| 23:59   | Gilbert Chan      | International Movies   |
| 9       | Shane Acker       | Action & Adventure     |
| 9       | Shane Acker       | Independent Movies     |
| 9       | Shane Acker       | Sci-Fi & Fantasy       |
| 21      | Robert Luketic    | Dramas                 |
| 46      | Serdar Akar       | International TV Shows |
| 46      | Serdar Akar       | TV Dramas              |



## Q12: Countries that have NEVER produced a Documentary (LEFT JOIN + NULL check)

```sql
SELECT DISTINCT bc.country_name AS country
FROM bridge_country bc
LEFT JOIN (
    SELECT bg.show_id FROM bridge_genre bg WHERE bg.genre_name LIKE '%Documentaries%'
) doc ON doc.show_id = bc.show_id
WHERE doc.show_id IS NULL
ORDER BY country;
```

**Rows returned:** 104

| country    |
|:-----------|
| nan        |
| Albania    |
| Algeria    |
| Angola     |
| Argentina  |
| Australia  |
| Austria    |
| Azerbaijan |
| Bahamas    |
| Bangladesh |



## Q13: Self-join — pairs of actors who co-starred in 3+ titles together

```sql
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
```

**Rows returned:** 15

| actor_1            | actor_2        |   titles_together |
|:-------------------|:---------------|------------------:|
| John Paul Tremblay | Robb Wells     |                15 |
| Eric Idle          | John Cleese    |                14 |
| Eric Idle          | Michael Palin  |                14 |
| Eric Idle          | Terry Jones    |                14 |
| John Cleese        | Michael Palin  |                14 |
| John Cleese        | Terry Jones    |                14 |
| Michael Palin      | Terry Jones    |                14 |
| Alessandro Juliani | Vincent Tong   |                13 |
| Eric Idle          | Graham Chapman |                13 |
| Eric Idle          | Terry Gilliam  |                13 |



## Q14: Directors who also appear in the cast bridge table for their own titles (JOIN + INTERSECT-like logic)

```sql
SELECT DISTINCT bd.director_name AS director_actor, t.title
FROM bridge_director bd
JOIN bridge_cast bcast
    ON bcast.show_id = bd.show_id
   AND bcast.cast_name = bd.director_name
JOIN titles t ON t.show_id = bd.show_id
LIMIT 20;
```

**Rows returned:** 20

| director_actor   | title                           |
|:-----------------|:--------------------------------|
| Kunle Afolayan   | Oct-01                          |
| Muharrem Gülmez  | Çarsi Pazar                     |
| Sam Upton        | 12 ROUND GUN                    |
| Ramzy Bedia      | 2 Alone in Paris                |
| Éric Judor       | 2 Alone in Paris                |
| Nagesh Kukunoor  | 3 Deewarein                     |
| David de Vos     | A Champion Heart                |
| Tyler Perry      | A Fall from Grace               |
| Tom Fassaert     | A Family Affair                 |
| Stanley Moore    | A Go! Go! Cory Carson Halloween |



## Q15: Country + genre combined performance (3-way join), US vs India vs UK

```sql
SELECT bc.country_name AS country, bg.genre_name AS genre, COUNT(*) AS title_count
FROM bridge_country bc
JOIN bridge_genre bg ON bg.show_id = bc.show_id
JOIN titles t ON t.show_id = bc.show_id
WHERE bc.country_name IN ('United States', 'India', 'United Kingdom')
GROUP BY bc.country_name, bg.genre_name
ORDER BY country, title_count DESC;
```

**Rows returned:** 114

| country   | genre                  |   title_count |
|:----------|:-----------------------|--------------:|
| India     | International Movies   |           828 |
| India     | Dramas                 |           626 |
| India     | Comedies               |           308 |
| India     | Independent Movies     |           145 |
| India     | Action & Adventure     |           134 |
| India     | Romantic Movies        |           113 |
| India     | Music & Musicals       |            97 |
| India     | Thrillers              |            88 |
| India     | International TV Shows |            60 |
| India     | Horror Movies          |            34 |



## Q16: Top genre per country using a CTE + window function

```sql
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
```

**Rows returned:** 15

| country        | top_genre              |   title_count |
|:---------------|:-----------------------|--------------:|
| India          | International Movies   |           828 |
| United States  | Dramas                 |           716 |
| United Kingdom | British TV Shows       |           212 |
| France         | International Movies   |           191 |
| Japan          | International TV Shows |           139 |
| South Korea    | International TV Shows |           139 |
| Spain          | International Movies   |           130 |
| Egypt          | International Movies   |            95 |
| Germany        | International Movies   |            82 |
| Canada         | Comedies               |            81 |



## Q17: Year-over-year content growth using a CTE

```sql
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
```

**Rows returned:** 73

|   release_year |   titles |   yoy_change |   yoy_pct_change |
|---------------:|---------:|-------------:|-----------------:|
|           1925 |        1 |          nan |            nan   |
|           1942 |        2 |            1 |            100   |
|           1943 |        3 |            1 |             50   |
|           1944 |        3 |            0 |              0   |
|           1945 |        3 |            0 |              0   |
|           1946 |        2 |           -1 |            -33.3 |
|           1947 |        1 |           -1 |            -50   |
|           1954 |        2 |            1 |            100   |
|           1955 |        3 |            1 |             50   |
|           1956 |        2 |           -1 |            -33.3 |



## Q18: Multi-level CTE — countries with above-average genre diversity

```sql
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
```

**Rows returned:** 46

| country        |   genre_count |
|:---------------|--------------:|
| United States  |            42 |
| Canada         |            37 |
| United Kingdom |            37 |
| France         |            35 |
| India          |            35 |
| Australia      |            34 |
| Japan          |            34 |
| Germany        |            32 |
| Spain          |            31 |
| China          |            30 |



## Q19: Fastest-growing genres (CTE comparing first half vs second half of catalog history)

```sql
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
```

**Rows returned:** 10

| genre                        |   earlier_count |   recent_count |   growth |   growth_pct |
|:-----------------------------|----------------:|---------------:|---------:|-------------:|
| Stand-Up Comedy & Talk Shows |               7 |             44 |       37 |        528.6 |
| TV Mysteries                 |              14 |             75 |       61 |        435.7 |
| TV Action & Adventure        |              27 |            114 |       87 |        322.2 |
| TV Horror                    |              17 |             52 |       35 |        205.9 |
| Crime TV Shows               |             104 |            318 |      214 |        205.8 |
| Spanish-Language TV Shows    |              36 |            106 |       70 |        194.4 |
| TV Sci-Fi & Fantasy          |              17 |             50 |       33 |        194.1 |
| Reality TV                   |              58 |            161 |      103 |        177.6 |
| TV Thrillers                 |              14 |             35 |       21 |        150   |
| Teen TV Shows                |              16 |             38 |       22 |        137.5 |



## Q20: Recursive-style CTE alternative — running cumulative titles added by year

```sql
WITH yearly AS (
    SELECT release_year, COUNT(*) AS titles FROM titles GROUP BY release_year
)
SELECT
    release_year,
    titles,
    SUM(titles) OVER (ORDER BY release_year) AS cumulative_titles
FROM yearly
ORDER BY release_year;
```

**Rows returned:** 73

|   release_year |   titles |   cumulative_titles |
|---------------:|---------:|--------------------:|
|           1925 |        1 |                   1 |
|           1942 |        2 |                   3 |
|           1943 |        3 |                   6 |
|           1944 |        3 |                   9 |
|           1945 |        3 |                  12 |
|           1946 |        2 |                  14 |
|           1947 |        1 |                  15 |
|           1954 |        2 |                  17 |
|           1955 |        3 |                  20 |
|           1956 |        2 |                  22 |



## Q21: Top 5 directors per country by title count (ROW_NUMBER + PARTITION BY)

```sql
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
```

**Rows returned:** 15

| country        | director              |   title_count |   rn |
|:---------------|:----------------------|--------------:|-----:|
| India          | Anurag Kashyap        |             9 |    1 |
| India          | David Dhawan          |             9 |    2 |
| India          | Umesh Mehra           |             8 |    3 |
| India          | Dibakar Banerjee      |             7 |    4 |
| India          | Anees Bazmee          |             6 |    5 |
| United Kingdom | Alastair Fothergill   |             4 |    1 |
| United Kingdom | Edward Cotterill      |             4 |    2 |
| United Kingdom | Martin Campbell       |             3 |    3 |
| United Kingdom | Orlando von Einsiedel |             3 |    4 |
| United Kingdom | Terry Gilliam         |             3 |    5 |



## Q22: Overall director ranking by total titles (DENSE_RANK)

```sql
SELECT
    director_name AS director,
    COUNT(*) AS title_count,
    DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS rank_overall
FROM bridge_director
WHERE director_name <> 'Unknown'
GROUP BY director_name
ORDER BY title_count DESC
LIMIT 15;
```

**Rows returned:** 15

| director            |   title_count |   rank_overall |
|:--------------------|--------------:|---------------:|
| Jan Suter           |            21 |              1 |
| Raúl Campos         |            19 |              2 |
| Marcus Raboy        |            16 |              3 |
| Jay Karas           |            15 |              4 |
| Cathy Garcia-Molina |            13 |              5 |
| Youssef Chahine     |            12 |              6 |
| Martin Scorsese     |            12 |              6 |
| Jay Chapman         |            12 |              6 |
| Steven Spielberg    |            10 |              7 |
| Shannon Hartman     |             9 |              8 |



## Q23: Overall actor ranking by total titles (DENSE_RANK)

```sql
SELECT
    cast_name AS actor,
    COUNT(*) AS title_count,
    DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS rank_overall
FROM bridge_cast
WHERE cast_name <> 'Unknown'
GROUP BY cast_name
ORDER BY title_count DESC
LIMIT 15;
```

**Rows returned:** 15

| actor            |   title_count |   rank_overall |
|:-----------------|--------------:|---------------:|
| Anupam Kher      |            42 |              1 |
| Shah Rukh Khan   |            35 |              2 |
| Om Puri          |            30 |              3 |
| Naseeruddin Shah |            30 |              3 |
| Takahiro Sakurai |            29 |              4 |
| Akshay Kumar     |            29 |              4 |
| Yuki Kaji        |            27 |              5 |
| Paresh Rawal     |            27 |              5 |
| Boman Irani      |            27 |              5 |
| Amitabh Bachchan |            27 |              5 |



## Q24: Percentile ranking of movie durations (NTILE quartiles)

```sql
SELECT
    title,
    duration_minutes,
    NTILE(4) OVER (ORDER BY duration_minutes) AS duration_quartile
FROM titles
WHERE type = 'Movie' AND duration_minutes IS NOT NULL
ORDER BY duration_minutes DESC
LIMIT 20;
```

**Rows returned:** 20

| title                      |   duration_minutes |   duration_quartile |
|:---------------------------|-------------------:|--------------------:|
| Black Mirror: Bandersnatch |                312 |                   4 |
| The School of Mischief     |                253 |                   4 |
| No Longer kids             |                237 |                   4 |
| Lock Your Girls In         |                233 |                   4 |
| Raya and Sakina            |                230 |                   4 |
| Sangam                     |                228 |                   4 |
| Lagaan                     |                224 |                   4 |
| Jodhaa Akbar               |                214 |                   4 |
| Kabhi Khushi Kabhie Gham   |                209 |                   4 |
| The Irishman               |                209 |                   4 |



## Q25: Each title's rank within its own release year by duration (PARTITION BY release_year)

```sql
SELECT
    title, release_year, duration_minutes,
    RANK() OVER (PARTITION BY release_year ORDER BY duration_minutes DESC) AS rank_in_year
FROM titles
WHERE type = 'Movie' AND duration_minutes IS NOT NULL AND release_year >= 2019
ORDER BY release_year, rank_in_year
LIMIT 30;
```

**Rows returned:** 30

| title                        |   release_year |   duration_minutes |   rank_in_year |
|:-----------------------------|---------------:|-------------------:|---------------:|
| The Irishman                 |           2019 |                209 |              1 |
| This Earth of Mankind        |           2019 |                180 |              2 |
| Super Deluxe                 |           2019 |                176 |              3 |
| Saaho                        |           2019 |                172 |              4 |
| Kabir Singh                  |           2019 |                171 |              5 |
| Panipat - The Great Betrayal |           2019 |                171 |              5 |
| Petta                        |           2019 |                170 |              7 |
| Petta (Telugu Version)       |           2019 |                170 |              7 |
| Oh! Baby                     |           2019 |                157 |              9 |
| A Sun                        |           2019 |                156 |             10 |



## Q26: Difference between a title's release_year and the prior title's release_year per country (LAG)

```sql
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
```

**Rows returned:** 25

| title       |   release_year |   years_since_prior_release |
|:------------|---------------:|----------------------------:|
| Ujala       |           1959 |                         nan |
| Singapore   |           1960 |                           1 |
| Professor   |           1962 |                           2 |
| Sangam      |           1964 |                           2 |
| Amrapali    |           1966 |                           2 |
| Prince      |           1969 |                           3 |
| Elaan       |           1971 |                           2 |
| Lal Patthar |           1971 |                           0 |
| Bawarchi    |           1972 |                           1 |
| Koshish     |           1972 |                           0 |



## Q27: Genre's share of its country's total catalog (window SUM as denominator)

```sql
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
```

**Rows returned:** 42

| genre                    |   cnt |   pct_of_country_catalog |
|:-------------------------|------:|-------------------------:|
| Dramas                   |   716 |                    11.88 |
| Comedies                 |   588 |                     9.76 |
| Documentaries            |   478 |                     7.93 |
| Independent Movies       |   358 |                     5.94 |
| Children & Family Movies |   348 |                     5.78 |
| Action & Adventure       |   315 |                     5.23 |
| Thrillers                |   251 |                     4.17 |
| TV Comedies              |   238 |                     3.95 |
| TV Dramas                |   221 |                     3.67 |
| Stand-Up Comedy          |   212 |                     3.52 |



## Q28: First and last title added per country (FIRST_VALUE / LAST_VALUE)

```sql
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
```

**Rows returned:** 5

| country        | first_title_added    | most_recent_title_added   |
|:---------------|:---------------------|:--------------------------|
| India          | Catching the Sun     | Delhi Belly               |
| Japan          | Atelier              | Kuroko's Basketball       |
| South Korea    | Dramaworld           | What Happened to Mr. Cha? |
| United Kingdom | The 4400             | A Monster Calls           |
| United States  | To and From New York | A Monster Calls           |



## Q29: Bucket movies into short/medium/long using CASE

```sql
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
```

**Rows returned:** 20

| title   |   duration_minutes | length_bucket         |
|:--------|-------------------:|:----------------------|
| 7:19    |                 93 | Standard (60-120 min) |
| 23:59   |                 78 | Standard (60-120 min) |
| 9       |                 80 | Standard (60-120 min) |
| 21      |                123 | Long (>120 min)       |
| 122     |                 95 | Standard (60-120 min) |
| 187     |                119 | Standard (60-120 min) |
| 706     |                118 | Standard (60-120 min) |
| 1920    |                143 | Long (>120 min)       |
| 1922    |                103 | Standard (60-120 min) |
| 2, 215  |                 89 | Standard (60-120 min) |



## Q30: Count of movies per length bucket (CASE inside aggregate)

```sql
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
```

**Rows returned:** 3

| length_bucket         |   movie_count |
|:----------------------|--------------:|
| Standard (60-120 min) |          3945 |
| Long (>120 min)       |          1011 |
| Short (<60 min)       |           420 |



## Q31: Decade classification of release_year (CASE)

```sql
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
```

**Rows returned:** 6

| decade   |   title_count |
|:---------|--------------:|
| 1980s    |           106 |
| 1990s    |           225 |
| 2000s    |           728 |
| 2010s    |          5710 |
| 2020s    |           899 |
| Pre-1980 |           118 |



## Q32: Flag binge-worthy TV shows (CASE + threshold)

```sql
SELECT
    title, duration_seasons,
    CASE WHEN duration_seasons >= 5 THEN 'Long-Running' ELSE 'Limited/Standard' END AS show_category
FROM titles
WHERE type = 'TV Show' AND duration_seasons IS NOT NULL
ORDER BY duration_seasons DESC
LIMIT 20;
```

**Rows returned:** 20

| title                  |   duration_seasons | show_category   |
|:-----------------------|-------------------:|:----------------|
| Grey's Anatomy         |                 16 | Long-Running    |
| NCIS                   |                 15 | Long-Running    |
| Supernatural           |                 15 | Long-Running    |
| COMEDIANS of the world |                 13 | Long-Running    |
| Red vs. Blue           |                 13 | Long-Running    |
| Criminal Minds         |                 12 | Long-Running    |
| Trailer Park Boys      |                 12 | Long-Running    |
| Cheers                 |                 11 | Long-Running    |
| Frasier                |                 11 | Long-Running    |
| Heartland              |                 11 | Long-Running    |



## Q33: Family-friendly vs mature flag with aggregate (CASE + GROUP BY)

```sql
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
```

**Rows returned:** 15

| country        |   family_friendly_titles |   mature_titles |   total_titles |
|:---------------|-------------------------:|----------------:|---------------:|
| United States  |                      781 |            1368 |           2883 |
| India          |                      171 |             242 |            956 |
| United Kingdom |                      151 |             294 |            577 |
| Canada         |                       96 |             117 |            259 |
| Japan          |                       67 |              86 |            237 |
| France         |                       39 |             121 |            196 |
| South Korea    |                       33 |              87 |            194 |
| Spain          |                       15 |             133 |            168 |
| Mexico         |                       13 |              90 |            123 |
| Australia      |                       38 |              49 |            108 |



## Q34: Titles longer than the average movie duration (scalar subquery)

```sql
SELECT title, duration_minutes
FROM titles
WHERE type = 'Movie'
  AND duration_minutes > (SELECT AVG(duration_minutes) FROM titles WHERE type = 'Movie')
ORDER BY duration_minutes DESC
LIMIT 15;
```

**Rows returned:** 15

| title                      |   duration_minutes |
|:---------------------------|-------------------:|
| Black Mirror: Bandersnatch |                312 |
| The School of Mischief     |                253 |
| No Longer kids             |                237 |
| Lock Your Girls In         |                233 |
| Raya and Sakina            |                230 |
| Sangam                     |                228 |
| Lagaan                     |                224 |
| Jodhaa Akbar               |                214 |
| Kabhi Khushi Kabhie Gham   |                209 |
| The Irishman               |                209 |



## Q35: Countries producing more titles than the global average per-country count (subquery in WHERE)

```sql
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
```

**Rows returned:** 22

| country        |   title_count |
|:---------------|--------------:|
| United States  |          3297 |
| India          |           990 |
| United Kingdom |           723 |
| Canada         |           412 |
| France         |           349 |
| Japan          |           287 |
| Spain          |           215 |
| South Korea    |           212 |
| Germany        |           199 |
| Mexico         |           154 |



## Q36: Directors whose titles all belong to a single genre (correlated subquery)

```sql
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
```

**Rows returned:** 15

| director         |
|:-----------------|
| Stanley Moore    |
| Alex Woo         |
| Raúl Campos      |
| Jan Suter        |
| Edward Cotterill |
| Ezekiel Norton   |
| Shannon Hartman  |
| Jay Chapman      |
| Momoko Kamiya    |
| Joey So          |



## Q37: Genre with the single longest average movie duration (subquery to find the max)

```sql
SELECT genre, avg_movie_duration
FROM vw_genre_summary
WHERE avg_movie_duration = (SELECT MAX(avg_movie_duration) FROM vw_genre_summary);
```

**Rows returned:** 1

| genre          |   avg_movie_duration |
|:---------------|---------------------:|
| Classic Movies |                115.6 |



## Q38: Titles added in the same month/year as Netflix's biggest content drop (subquery for the peak month)

```sql
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
```

**Rows returned:** 20

| title                               | type    | date_added_parsed   |
|:------------------------------------|:--------|:--------------------|
| 187                                 | Movie   | 2019-11-01          |
| 100 Things to do Before High School | Movie   | 2019-11-02          |
| 100% Hotter                         | TV Show | 2019-11-01          |
| 16 Blocks                           | Movie   | 2019-11-01          |
| A Fairly Odd Summer                 | Movie   | 2019-11-02          |
| A Holiday Engagement                | Movie   | 2019-11-04          |
| A Remarkable Tale                   | Movie   | 2019-11-01          |
| A Single Man                        | Movie   | 2019-11-11          |
| A Year In Space                     | TV Show | 2019-11-01          |
| Ad Vitam                            | TV Show | 2019-11-01          |



## Q39: Average days between a title's release and its addition to Netflix (date math)

```sql
SELECT
    title, release_year, date_added_parsed,
    CAST((julianday(date_added_parsed) - julianday(release_year || '-01-01')) AS INT) AS days_release_to_add
FROM titles
WHERE date_added_parsed IS NOT NULL
ORDER BY days_release_to_add DESC
LIMIT 15;
```

**Rows returned:** 15

| title                                         |   release_year | date_added_parsed   |   days_release_to_add |
|:----------------------------------------------|---------------:|:--------------------|----------------------:|
| Pioneers: First Women Filmmakers*             |           1925 | 2018-12-30          |                 34331 |
| Prelude to War                                |           1942 | 2017-03-31          |                 27483 |
| The Battle of Midway                          |           1942 | 2017-03-31          |                 27483 |
| Undercover: How to Operate Behind Enemy Lines |           1943 | 2017-03-31          |                 27118 |
| Why We Fight: The Battle of Russia            |           1943 | 2017-03-31          |                 27118 |
| WWII: Report from the Aleutians               |           1943 | 2017-03-31          |                 27118 |
| The Memphis Belle: A Story of a               |           1944 | 2017-03-31          |                 26753 |
| Flying Fortress                               |                |                     |                       |
| The Negro Soldier                             |           1944 | 2017-03-31          |                 26753 |
| Tunisian Victory                              |           1944 | 2017-03-31          |                 26753 |
| Know Your Enemy - Japan                       |           1945 | 2017-03-31          |                 26387 |



## Q40: Content added by day-of-week (seasonality / release-day strategy)

```sql
SELECT day_of_week_added, COUNT(*) AS titles_added
FROM titles
WHERE day_of_week_added IS NOT NULL
GROUP BY day_of_week_added
ORDER BY titles_added DESC;
```

**Rows returned:** 7

| day_of_week_added   |   titles_added |
|:--------------------|---------------:|
| Friday              |           2286 |
| Thursday            |           1147 |
| Tuesday             |           1070 |
| Wednesday           |           1020 |
| Monday              |            814 |
| Saturday            |            731 |
| Sunday              |            708 |



## Q41: Quarter-over-quarter content additions (date function + window)

```sql
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
```

**Rows returned:** 41

|   year_added |   quarter_added |   titles |   qoq_change |
|-------------:|----------------:|---------:|-------------:|
|         2008 |               1 |        2 |          nan |
|         2009 |               2 |        1 |           -1 |
|         2009 |               4 |        1 |            0 |
|         2010 |               4 |        1 |            0 |
|         2011 |               2 |        1 |            0 |
|         2011 |               3 |        1 |            0 |
|         2011 |               4 |       11 |           10 |
|         2012 |               1 |        1 |          -10 |
|         2012 |               4 |        2 |            1 |
|         2013 |               1 |        1 |           -1 |



## Q42: Gap (in years) between original release and Netflix addition, bucketed

```sql
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
```

**Rows returned:** 4

| catalog_age_bucket            |   title_count |
|:------------------------------|--------------:|
| Same year or Netflix original |          2837 |
| 1-2 years later               |          2129 |
| 5+ years later                |          1810 |
| 3-5 years later               |          1000 |



## Q43: Most active year_added overall, with month breakdown (date functions + RANK)

```sql
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
```

**Rows returned:** 18

|   year_added | month_name_added   |   titles_added |   month_rank_in_year |
|-------------:|:-------------------|---------------:|---------------------:|
|         2008 | January            |              1 |                    1 |
|         2008 | February           |              1 |                    1 |
|         2009 | May                |              1 |                    1 |
|         2009 | November           |              1 |                    1 |
|         2010 | November           |              1 |                    1 |
|         2011 | October            |             11 |                    1 |
|         2012 | February           |              1 |                    1 |
|         2012 | November           |              1 |                    1 |
|         2012 | December           |              1 |                    1 |
|         2013 | October            |              3 |                    1 |



## Q44: Executive snapshot from vw_country_summary — top 10 markets by total footprint

```sql
SELECT * FROM vw_country_summary
ORDER BY total_titles DESC
LIMIT 10;
```

**Rows returned:** 10

| country        |   total_titles |   movie_count |   tv_show_count |   avg_movie_duration |   earliest_title_year |   latest_title_year |
|:---------------|---------------:|--------------:|----------------:|---------------------:|----------------------:|--------------------:|
| United States  |           3297 |          2431 |             866 |                 92.4 |                  1942 |                2021 |
| India          |            990 |           915 |              75 |                126.3 |                  1959 |                2021 |
| United Kingdom |            723 |           467 |             256 |                 97.2 |                  1944 |                2021 |
| Canada         |            412 |           286 |             126 |                 90.2 |                  1979 |                2021 |
| France         |            349 |           265 |              84 |                 99.9 |                  1955 |                2020 |
| Japan          |            287 |           103 |             184 |                 96.9 |                  1979 |                2020 |
| Spain          |            215 |           158 |              57 |                101.2 |                  1993 |                2021 |
| South Korea    |            212 |            55 |             157 |                109.7 |                  2004 |                2021 |
| Germany        |            199 |           157 |              42 |                101.5 |                  1997 |                2020 |
| Mexico         |            154 |           101 |              53 |                 89.2 |                  1979 |                2021 |



## Q45: Cross-view query — genre summary joined with director rankings to spot

```sql
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
```

**Rows returned:** 20

| director            |   director_title_count | genre                |   genre_total_titles |
|:--------------------|-----------------------:|:---------------------|---------------------:|
| Cathy Garcia-Molina |                     37 | International Movies |                 2436 |
| Cathy Garcia-Molina |                     37 | Dramas               |                 2105 |
| Cathy Garcia-Molina |                     37 | Comedies             |                 1471 |
| Cathy Garcia-Molina |                     37 | Romantic Movies      |                  531 |
| Youssef Chahine     |                     33 | International Movies |                 2436 |
| Youssef Chahine     |                     33 | Dramas               |                 2105 |
| Youssef Chahine     |                     33 | Action & Adventure   |                  721 |
| Youssef Chahine     |                     33 | Romantic Movies      |                  531 |
| Youssef Chahine     |                     33 | Classic Movies       |                  103 |
| David Dhawan        |                     27 | International Movies |                 2436 |



## Q46: Top 3 countries by content growth between 2015-2018 vs 2019-2021 (CTE + RANK)

```sql
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
```

**Rows returned:** 10

| country   |   p1_count |   p2_count |   growth |   growth_rank |
|:----------|-----------:|-----------:|---------:|--------------:|
| Brazil    |         37 |         41 |        4 |             1 |
| Norway    |         10 |          9 |       -1 |             2 |
| Hungary   |          5 |          3 |       -2 |             3 |
| Iceland   |          6 |          3 |       -3 |             4 |
| Romania   |          6 |          3 |       -3 |             4 |
| Uruguay   |          8 |          5 |       -3 |             4 |
| Austria   |          7 |          3 |       -4 |             7 |
| Jordan    |          5 |          1 |       -4 |             7 |
| Poland    |         14 |         10 |       -4 |             7 |
| Serbia    |          5 |          1 |       -4 |             7 |



## Q47: Underrepresented genres — low title count but present in many countries (diversification candidates)

```sql
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
```

**Rows returned:** 12

| genre                 |   total_titles |   countries_present_in |
|:----------------------|---------------:|-----------------------:|
| Horror Movies         |            306 |                     45 |
| Crime TV Shows        |            396 |                     44 |
| Sports Movies         |            187 |                     42 |
| Sci-Fi & Fantasy      |            217 |                     40 |
| Music & Musicals      |            298 |                     34 |
| Romantic TV Shows     |            281 |                     33 |
| Kids' TV              |            344 |                     29 |
| TV Action & Adventure |            141 |                     27 |
| Docuseries            |            314 |                     26 |
| TV Mysteries          |             89 |                     24 |



## Q48: Rating distribution skew per country — share of mature (Adults) content (window function for share)

```sql
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
```

**Rows returned:** 25

| country   | maturity_level   |   cnt |   pct_within_country |
|:----------|:-----------------|------:|---------------------:|
| India     | Teens            |   551 |                 55.7 |
| India     | Adults           |   251 |                 25.4 |
| India     | Family           |   147 |                 14.8 |
| India     | Kids             |    32 |                  3.2 |
| India     | Unrated          |     9 |                  0.9 |
| Japan     | Adults           |   101 |                 35.2 |
| Japan     | Teens            |    92 |                 32.1 |
| Japan     | Family           |    57 |                 19.9 |
| Japan     | Kids             |    36 |                 12.5 |
| Japan     | Unrated          |     1 |                  0.3 |



## Q49: Titles released and added in the same calendar year ("day-and-date" originals) by year (CASE + aggregate)

```sql
SELECT
    release_year,
    SUM(CASE WHEN year_added = release_year THEN 1 ELSE 0 END) AS same_year_release_and_add,
    COUNT(*) AS total_titles_that_year,
    ROUND(100.0 * SUM(CASE WHEN year_added = release_year THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_originals_like
FROM titles
WHERE year_added IS NOT NULL AND release_year >= 2015
GROUP BY release_year
ORDER BY release_year;
```

**Rows returned:** 7

|   release_year |   same_year_release_and_add |   total_titles_that_year |   pct_originals_like |
|---------------:|----------------------------:|-------------------------:|---------------------:|
|           2015 |                          57 |                      539 |                 10.6 |
|           2016 |                         193 |                      881 |                 21.9 |
|           2017 |                         388 |                     1012 |                 38.3 |
|           2018 |                         572 |                     1120 |                 51.1 |
|           2019 |                         709 |                      996 |                 71.2 |
|           2020 |                         851 |                      868 |                 98   |
|           2021 |                          30 |                       31 |                 96.8 |



## Q50: Top 10 single-country titles (num_countries = 1) directors with international (multi-country) reach (subquery + join)

```sql
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
```

**Rows returned:** 10

| director         |   total_titles |   multi_country_titles |
|:-----------------|---------------:|-----------------------:|
| Youssef Chahine  |             12 |                      5 |
| Ishi Rudell      |              5 |                      5 |
| Wilson Yip       |              5 |                      5 |
| Martin Scorsese  |             12 |                      4 |
| Steven Spielberg |             10 |                      4 |
| Don Michael Paul |              7 |                      4 |
| Martin Campbell  |              4 |                      4 |
| Johnnie To       |              8 |                      3 |
| Umesh Mehra      |              8 |                      3 |
| McG              |              7 |                      3 |

