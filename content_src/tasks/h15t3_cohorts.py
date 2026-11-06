from kit import table, tables, rng, ts

ID = "h15t3"
NAME = "Weekly Retention Matrix"
LANG = "sql"
MINUTES = 25
TAGS = ["cohortes", "date_trunc week", "division entière", "NULL quand non observable", "FILTER"]
DESC = """
<p>The table <b>events</b> has the columns <code>user_id</code> and <code>event_at</code> (timestamp). A week starts on Monday (the week of a timestamp is <code>date_trunc('week', ...)</code>, as a date).</p>
<p>The <b>cohort</b> of a user is the week of their first event. For a cohort and a week offset <code>k</code> (0 to 4), the retention is the percentage of the users of the cohort who have at least one event in the week <code>cohort_week + 7 * k</code> days, rounded to 1 decimal. Week 0 is therefore always 100.0.</p>
<p>The data stops at the week of the latest event of the table. A week offset that falls <b>after</b> that week cannot be observed yet: its retention is <code>NULL</code>, not 0.</p>
<p>Your task is to return one row per cohort with the columns <code>cohort_week</code>, <code>cohort_size</code>, <code>w0</code>, <code>w1</code>, <code>w2</code>, <code>w3</code> and <code>w4</code>, sorted by <code>cohort_week</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH f AS (
  SELECT user_id, date_trunc('week', MIN(event_at))::date AS cw FROM events GROUP BY user_id
), a AS (
  SELECT DISTINCT e.user_id, f.cw, (date_trunc('week', e.event_at)::date - f.cw) / 7 AS k
  FROM events e JOIN f ON f.user_id = e.user_id
), lw AS (
  SELECT date_trunc('week', MAX(event_at))::date AS lw FROM events
), s AS (
  SELECT cw, COUNT(*) AS size FROM f GROUP BY cw
), c AS (
  SELECT a.cw, a.k, COUNT(*) AS users FROM a GROUP BY a.cw, a.k
)
SELECT s.cw AS cohort_week, s.size AS cohort_size,
  ROUND(100.0 * COALESCE(MAX(users) FILTER (WHERE k = 0), 0) / s.size, 1) AS w0,
  CASE WHEN s.cw + 7 <= lw THEN ROUND(100.0 * COALESCE(MAX(users) FILTER (WHERE k = 1), 0) / s.size, 1) END AS w1,
  CASE WHEN s.cw + 14 <= lw THEN ROUND(100.0 * COALESCE(MAX(users) FILTER (WHERE k = 2), 0) / s.size, 1) END AS w2,
  CASE WHEN s.cw + 21 <= lw THEN ROUND(100.0 * COALESCE(MAX(users) FILTER (WHERE k = 3), 0) / s.size, 1) END AS w3,
  CASE WHEN s.cw + 28 <= lw THEN ROUND(100.0 * COALESCE(MAX(users) FILTER (WHERE k = 4), 0) / s.size, 1) END AS w4
FROM s JOIN c ON c.cw = s.cw CROSS JOIN lw
GROUP BY s.cw, s.size, lw
ORDER BY s.cw;
"""
MUTANTS = [
    SOLUTION.replace("ROUND(100.0 * COALESCE(MAX(users) FILTER (WHERE k = 1), 0) / s.size, 1)", "ROUND(100 * COALESCE(MAX(users) FILTER (WHERE k = 1), 0) / s.size, 1)"),
    SOLUTION.replace("CASE WHEN s.cw + 21 <= lw THEN ", "CASE WHEN true THEN "),
    SOLUTION.replace("SELECT DISTINCT e.user_id, f.cw", "SELECT e.user_id, f.cw"),
    SOLUTION.replace("date_trunc('week', MIN(event_at))::date AS cw", "date_trunc('week', MIN(event_at))::date - 1 AS cw"),
]
T = "user_id INT, event_at TIMESTAMP"


def tests():
    # ts(0) = lundi 2 mars 2026, 08:00
    t = [tables(events=table(T, [[1, ts(0)], [1, ts(60)], [1, ts(7 * 1440)], [2, ts(2 * 1440)], [2, ts(15 * 1440)], [3, ts(6 * 1440 + 900)],
                                 [4, ts(8 * 1440)], [4, ts(22 * 1440)], [5, ts(9 * 1440)]])),
         tables(events=table(T, [[9, ts(-1)], [9, ts(0)], [8, ts(0)], [8, ts(35 * 1440)]]))]
    r = rng(4153)
    for _ in range(8):
        rows = []
        for u in range(1, r.randint(4, 15)):
            start = r.randint(0, 25) * 1440 + r.randint(0, 1000)
            for _ in range(r.randint(1, 6)):
                rows.append([u, ts(start + r.choice([0, 1, 3, 7, 8, 14, 21, 28, 30]) * 1440)])
        t.append(tables(events=table(T, rows)))
    return t
