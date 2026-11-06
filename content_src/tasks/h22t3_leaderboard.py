from kit import table, tables, rng, day

ID = "h22t3"
NAME = "Weekly Leaderboard Movers"
LANG = "sql"
MINUTES = 25
TAGS = ["DENSE_RANK", "égalités", "comparaison semaine précédente", "texte calculé (+2, -1, =, NEW)", "top N avec ex aequo"]
DESC = """
<p>The table <b>scores</b> has the columns <code>player</code>, <code>played_on</code> (date) and <code>points</code>. A week starts on Monday (<code>date_trunc('week', played_on)</code>, as a date). The weekly score of a player is the sum of their points in that week.</p>
<p>Each week, players are ranked by weekly score with <code>DENSE_RANK</code> (highest score = rank 1, equal scores share a rank). Only players with at least one row in the week are ranked that week.</p>
<p>The leaderboard of a week shows the players with a rank from 1 to 3 (so it can show more than 3 players). For each of them, <code>move</code> compares with the <b>calendar week just before</b>: <code>'NEW'</code> if the player was not ranked that week, <code>'='</code> if the rank is the same, else the number of places gained with a sign, like <code>'+2'</code> (better rank) or <code>'-1'</code> (worse rank).</p>
<p>Your task is to return the columns <code>week</code>, <code>rnk</code>, <code>player</code>, <code>score</code> and <code>move</code>, sorted by <code>week</code>, then <code>rnk</code>, then <code>player</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH w AS (
  SELECT date_trunc('week', played_on)::date AS week, player, SUM(points) AS score
  FROM scores GROUP BY 1, 2
), r AS (
  SELECT *, DENSE_RANK() OVER (PARTITION BY week ORDER BY score DESC) AS rnk FROM w
)
SELECT r.week, r.rnk, r.player, r.score,
       CASE WHEN p.rnk IS NULL THEN 'NEW'
            WHEN p.rnk = r.rnk THEN '='
            WHEN p.rnk > r.rnk THEN '+' || (p.rnk - r.rnk)
            ELSE '-' || (r.rnk - p.rnk) END AS move
FROM r
LEFT JOIN r p ON p.player = r.player AND p.week = r.week - 7
WHERE r.rnk <= 3
ORDER BY r.week, r.rnk, r.player;
"""
MUTANTS = [
    SOLUTION.replace("DENSE_RANK()", "RANK()"),
    SOLUTION.replace("LEFT JOIN r p ON p.player = r.player AND p.week = r.week - 7\nWHERE r.rnk <= 3", "LEFT JOIN r p ON p.player = r.player AND p.week = (SELECT MAX(x.week) FROM r x WHERE x.week < r.week)\nWHERE r.rnk <= 3"),
    SOLUTION.replace("WITH w AS (\n  SELECT date_trunc('week', played_on)::date AS week, player, SUM(points) AS score\n  FROM scores GROUP BY 1, 2\n), r AS (\n  SELECT *, DENSE_RANK() OVER (PARTITION BY week ORDER BY score DESC) AS rnk FROM w\n)",
                     "WITH w AS (\n  SELECT date_trunc('week', played_on)::date AS week, player, SUM(points) AS score\n  FROM scores GROUP BY 1, 2\n), r AS (\n  SELECT *, DENSE_RANK() OVER (PARTITION BY week ORDER BY score DESC) AS rnk FROM w\n), r2 AS (SELECT * FROM r WHERE rnk <= 3)").replace("LEFT JOIN r p ON", "LEFT JOIN r2 p ON"),
    SOLUTION.replace("WHEN p.rnk > r.rnk THEN '+' || (p.rnk - r.rnk)\n            ELSE '-' || (r.rnk - p.rnk) END", "WHEN p.rnk < r.rnk THEN '+' || (r.rnk - p.rnk)\n            ELSE '-' || (p.rnk - r.rnk) END"),
]
T = "player TEXT, played_on DATE, points INT"


def tests():
    t = [tables(scores=table(T, [["ana", "2026-03-02", 50], ["ana", "2026-03-04", 10], ["ben", "2026-03-03", 60], ["cyd", "2026-03-05", 40],
                                 ["dan", "2026-03-06", 30], ["eve", "2026-03-08", 20],
                                 ["ana", "2026-03-09", 20], ["ben", "2026-03-10", 70], ["cyd", "2026-03-11", 90], ["dan", "2026-03-12", 70],
                                 ["fay", "2026-03-15", 20], ["ana", "2026-03-23", 5], ["fay", "2026-03-24", 5]])),
         tables(scores=table(T, [["x", "2026-01-05", 1], ["y", "2026-01-05", 1], ["z", "2026-01-06", 0], ["w", "2026-01-07", -3],
                                 ["w", "2026-01-12", 9], ["x", "2026-01-13", 1], ["z", "2026-01-14", 1]]))]
    r = rng(4223)
    for _ in range(8):
        rows = []
        for _ in range(r.randint(6, 50)):
            rows.append([r.choice(["ana", "ben", "cyd", "dan", "eve", "fay"]), day(r.randint(0, 40), "2026-03-02"), r.choice([0, 5, 10, 10, 20, 35])])
        t.append(tables(scores=table(T, rows)))
    return t
