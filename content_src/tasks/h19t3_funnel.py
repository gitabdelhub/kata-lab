from kit import table, tables, rng, ts

ID = "h19t3"
NAME = "Ordered Conversion Funnel"
LANG = "sql"
MINUTES = 25
TAGS = ["entonnoir ordonné", "premier événement après un autre", "fenêtre de 7 jours", "pourcentages", "jointures latérales"]
DESC = """
<p>The table <b>events</b> has the columns <code>user_id</code>, <code>event_at</code> (timestamp) and <code>event_name</code> (<code>'view'</code>, <code>'cart'</code>, <code>'purchase'</code> or other names, which are ignored).</p>
<p>The funnel of a user is built from their <b>first</b> <code>'view'</code>:</p>
<ul><li>step 1 <code>view</code>: the user has a view (its time is <code>v</code>);</li>
<li>step 2 <code>cart</code>: the user has a cart event <b>strictly after</b> <code>v</code> and at most 7 days after <code>v</code> (<code>event_at &lt;= v + 7 days</code>); the first such cart has the time <code>c</code>;</li>
<li>step 3 <code>purchase</code>: the user has a purchase <b>strictly after</b> <code>c</code> and at most 7 days after <code>v</code>.</li></ul>
<p>A cart or purchase that happened before the first view does not count, and a user without a view is not in the funnel at all.</p>
<p>Your task is to return 3 rows with the columns <code>step</code> (1, 2, 3), <code>name</code> (<code>view</code>, <code>cart</code>, <code>purchase</code>), <code>users</code>, <code>pct_of_previous</code> (100 times users of this step divided by users of the previous step, rounded to 1 decimal; <code>NULL</code> for step 1 or when the previous step has 0 users) and <code>pct_of_first</code> (same against step 1, <code>NULL</code> when step 1 has 0 users), sorted by <code>step</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH v AS (
  SELECT user_id, MIN(event_at) AS v FROM events WHERE event_name = 'view' GROUP BY user_id
), c AS (
  SELECT v.user_id, v.v, MIN(e.event_at) AS c
  FROM v JOIN events e ON e.user_id = v.user_id AND e.event_name = 'cart'
   AND e.event_at > v.v AND e.event_at <= v.v + INTERVAL '7 days'
  GROUP BY v.user_id, v.v
), p AS (
  SELECT DISTINCT c.user_id
  FROM c JOIN events e ON e.user_id = c.user_id AND e.event_name = 'purchase'
   AND e.event_at > c.c AND e.event_at <= c.v + INTERVAL '7 days'
), s AS (
  SELECT 1 AS step, 'view' AS name, (SELECT COUNT(*) FROM v) AS users
  UNION ALL SELECT 2, 'cart', (SELECT COUNT(*) FROM c)
  UNION ALL SELECT 3, 'purchase', (SELECT COUNT(*) FROM p)
)
SELECT step, name, users,
       ROUND(100.0 * users / NULLIF(LAG(users) OVER (ORDER BY step), 0), 1) AS pct_of_previous,
       CASE WHEN step = 1 THEN NULL ELSE ROUND(100.0 * users / NULLIF(FIRST_VALUE(users) OVER (ORDER BY step), 0), 1) END AS pct_of_first
FROM s
ORDER BY step;
"""
MUTANTS = [
    SOLUTION.replace("AND e.event_at > c.c AND e.event_at <= c.v + INTERVAL '7 days'", "AND e.event_at > c.c AND e.event_at <= c.c + INTERVAL '7 days'"),
    SOLUTION.replace("AND e.event_at > v.v AND e.event_at <= v.v + INTERVAL '7 days'", "AND e.event_at >= v.v AND e.event_at <= v.v + INTERVAL '7 days'"),
    SOLUTION.replace("ROUND(100.0 * users / NULLIF(LAG(users)", "ROUND(100 * users / NULLIF(LAG(users)"),
    SOLUTION.replace("SELECT user_id, MIN(event_at) AS v FROM events WHERE event_name = 'view' GROUP BY user_id", "SELECT user_id, MAX(event_at) AS v FROM events WHERE event_name = 'view' GROUP BY user_id"),
]
T = "user_id INT, event_at TIMESTAMP, event_name TEXT"


def tests():
    D = 1440
    t = [tables(events=table(T, [[1, ts(0), "view"], [1, ts(10), "cart"], [1, ts(20), "purchase"], [2, ts(0), "cart"], [2, ts(5), "view"],
                                 [2, ts(6 * D), "cart"], [2, ts(7 * D + 10), "purchase"], [3, ts(0), "view"], [3, ts(8 * D), "cart"],
                                 [4, ts(0), "view"], [4, ts(0), "cart"], [4, ts(1), "share"], [5, ts(2), "purchase"], [6, ts(0), "view"], [6, ts(30), "view"],
                                 [6, ts(7 * D), "cart"], [6, ts(7 * D), "purchase"]])),
         tables(events=table(T, [[1, ts(0), "cart"], [2, ts(0), "purchase"]]))]
    r = rng(4193)
    for _ in range(8):
        rows = []
        for u in range(1, r.randint(4, 20)):
            for _ in range(r.randint(1, 6)):
                rows.append([u, ts(r.choice([0, 0, 30, 1440, 5000, 10080, 10081, 12000]) + r.randint(0, 3)),
                             r.choice(["view", "view", "cart", "cart", "purchase", "share"])])
        t.append(tables(events=table(T, rows)))
    return t
