from kit import table, tables, rng

ID = "e17t3"
NAME = "Merge Subscription Periods"
LANG = "sql"
MINUTES = 15
TAGS = ["intervalles qui se chevauchent", "îlots", "MAX cumulé", "dates de fin NULL"]
DESC = """
<p>The table <b>subscriptions</b> has the columns <code>sub_id</code>, <code>customer_id</code>, <code>start_date</code> and <code>end_date</code> (dates). A subscription covers every day from <code>start_date</code> to <code>end_date</code>, both included. An <code>end_date</code> that is <code>NULL</code> means the subscription is still active: treat it as <code>2026-12-31</code>.</p>
<p>Subscriptions of a customer can overlap or follow each other. Two periods are merged when they overlap or when one starts the day right after the other ends.</p>
<p>Your task is to return the merged periods with the columns <code>customer_id</code>, <code>period_start</code>, <code>period_end</code> and <code>days</code> (number of days covered, both ends included), sorted by <code>customer_id</code>, then <code>period_start</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH s AS (
  SELECT customer_id, start_date, COALESCE(end_date, DATE '2026-12-31') AS end_date FROM subscriptions
), m AS (
  SELECT *, MAX(end_date) OVER (PARTITION BY customer_id ORDER BY start_date, end_date
                                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_end
  FROM s
), g AS (
  SELECT *, SUM(CASE WHEN prev_end IS NULL OR start_date > prev_end + 1 THEN 1 ELSE 0 END)
              OVER (PARTITION BY customer_id ORDER BY start_date, end_date) AS grp
  FROM m
)
SELECT customer_id, MIN(start_date) AS period_start, MAX(end_date) AS period_end,
       MAX(end_date) - MIN(start_date) + 1 AS days
FROM g
GROUP BY customer_id, grp
ORDER BY customer_id, period_start;
"""
MUTANTS = [
    """
WITH s AS (SELECT customer_id, start_date, COALESCE(end_date, DATE '2026-12-31') AS end_date FROM subscriptions),
m AS (SELECT *, LAG(end_date) OVER (PARTITION BY customer_id ORDER BY start_date, end_date) AS prev_end FROM s),
g AS (SELECT *, SUM(CASE WHEN prev_end IS NULL OR start_date > prev_end + 1 THEN 1 ELSE 0 END) OVER (PARTITION BY customer_id ORDER BY start_date, end_date) AS grp FROM m)
SELECT customer_id, MIN(start_date) AS period_start, MAX(end_date) AS period_end, MAX(end_date) - MIN(start_date) + 1 AS days FROM g GROUP BY customer_id, grp ORDER BY customer_id, period_start;
""",
    """
WITH s AS (SELECT customer_id, start_date, COALESCE(end_date, DATE '2026-12-31') AS end_date FROM subscriptions),
m AS (SELECT *, MAX(end_date) OVER (PARTITION BY customer_id ORDER BY start_date, end_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_end FROM s),
g AS (SELECT *, SUM(CASE WHEN prev_end IS NULL OR start_date > prev_end THEN 1 ELSE 0 END) OVER (PARTITION BY customer_id ORDER BY start_date, end_date) AS grp FROM m)
SELECT customer_id, MIN(start_date) AS period_start, MAX(end_date) AS period_end, MAX(end_date) - MIN(start_date) + 1 AS days FROM g GROUP BY customer_id, grp ORDER BY customer_id, period_start;
""",
    """
WITH s AS (SELECT customer_id, start_date, end_date FROM subscriptions),
m AS (SELECT *, MAX(end_date) OVER (PARTITION BY customer_id ORDER BY start_date, end_date ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_end FROM s),
g AS (SELECT *, SUM(CASE WHEN prev_end IS NULL OR start_date > prev_end + 1 THEN 1 ELSE 0 END) OVER (PARTITION BY customer_id ORDER BY start_date, end_date) AS grp FROM m)
SELECT customer_id, MIN(start_date) AS period_start, MAX(end_date) AS period_end, MAX(end_date) - MIN(start_date) + 1 AS days FROM g GROUP BY customer_id, grp ORDER BY customer_id, period_start;
""",
]
T = "sub_id INT, customer_id INT, start_date DATE, end_date DATE"


def tests():
    t = [tables(subscriptions=table(T, [[1, 1, "2026-01-01", "2026-03-31"], [2, 1, "2026-02-01", "2026-02-15"], [3, 1, "2026-04-01", "2026-04-30"],
                                        [4, 1, "2026-06-01", None], [5, 2, "2026-01-10", "2026-01-20"], [6, 2, "2026-01-22", "2026-01-25"]])),
         tables(subscriptions=table(T, [[1, 5, "2026-05-01", "2026-05-01"], [2, 5, "2026-05-02", "2026-05-02"], [3, 5, "2026-05-01", "2026-05-01"]]))]
    r = rng(1703)
    for _ in range(7):
        rows, n = [], 0
        for c in range(1, r.randint(2, 5)):
            for _ in range(r.randint(1, 5)):
                n += 1
                s = r.randint(1, 300)
                e = s + r.randint(0, 40)
                import datetime as dt
                d0 = dt.date(2026, 1, 1)
                rows.append([n, c, str(d0 + dt.timedelta(s)), None if r.random() < 0.1 else str(d0 + dt.timedelta(min(e, 364)))])
        t.append(tables(subscriptions=table(T, rows)))
    return t
