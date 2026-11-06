from kit import table, tables, rng, ts

ID = "h17t3"
NAME = "Peak Concurrent Streams"
LANG = "sql"
MINUTES = 25
TAGS = ["événements +1 / -1", "somme cumulée", "ordre des égalités", "sessions sans fin", "UNION ALL"]
DESC = """
<p>The table <b>sessions</b> has the columns <code>session_id</code>, <code>user_id</code>, <code>started_at</code> and <code>ended_at</code> (timestamps). A session is active from <code>started_at</code> (included) to <code>ended_at</code> (excluded): a session that ends exactly when another one starts does <b>not</b> overlap it. A session with <code>ended_at</code> = <code>NULL</code> is still running and never ends. Sessions can cross midnight.</p>
<p>The number of concurrent sessions changes only when a session starts or ends. For each day on which at least one session <b>started</b>, we want the highest number of concurrent sessions reached at a moment when a session of that day started, and the first moment it was reached that day.</p>
<p>Your task is to return the columns <code>day</code> (date), <code>peak</code>, <code>peak_at</code> (timestamp) and <code>sessions_started</code> (number of sessions that started that day), sorted by <code>day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH ev AS (
  SELECT started_at AS t, 1 AS d FROM sessions
  UNION ALL
  SELECT ended_at, -1 FROM sessions WHERE ended_at IS NOT NULL
), r AS (
  SELECT t, d, SUM(d) OVER (ORDER BY t, d ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS c FROM ev
), s AS (
  SELECT t::date AS day, t, c FROM r WHERE d = 1
), m AS (
  SELECT day, MAX(c) AS peak, COUNT(*) AS started FROM s GROUP BY day
)
SELECT m.day, m.peak, MIN(s.t) AS peak_at, m.started AS sessions_started
FROM m JOIN s ON s.day = m.day AND s.c = m.peak
GROUP BY m.day, m.peak, m.started
ORDER BY m.day;
"""
MUTANTS = [
    SOLUTION.replace("ORDER BY t, d ROWS", "ORDER BY t, d DESC ROWS"),
    SOLUTION.replace("SELECT ended_at, -1 FROM sessions WHERE ended_at IS NOT NULL", "SELECT COALESCE(ended_at, started_at), -1 FROM sessions"),
    SOLUTION.replace("MIN(s.t) AS peak_at", "MAX(s.t) AS peak_at"),
    SOLUTION.replace("SELECT t::date AS day, t, c FROM r WHERE d = 1", "SELECT t::date AS day, t, c FROM r"),
]
T = "session_id INT, user_id INT, started_at TIMESTAMP, ended_at TIMESTAMP"


def tests():
    t = [tables(sessions=table(T, [[1, 1, ts(0), ts(60)], [2, 2, ts(30), ts(90)], [3, 3, ts(60), ts(120)], [4, 4, ts(60), None],
                                   [5, 5, ts(100), ts(110)], [6, 1, ts(950), ts(1000)], [7, 2, ts(990), ts(1500)], [8, 3, ts(1450), ts(1460)]])),
         tables(sessions=table(T, [[1, 1, ts(0), ts(10)], [2, 1, ts(10), ts(20)], [3, 1, ts(20), ts(30)]]))]
    r = rng(4173)
    for _ in range(8):
        rows = []
        for i in range(r.randint(4, 30)):
            s = r.choice([0, 10, 10, 30, 60, 900, 960, 1440, 1500, 2000]) + r.choice([0, 0, 5])
            e = None if r.random() < 0.1 else s + r.choice([0, 10, 20, 50, 600])
            rows.append([i + 1, r.randint(1, 6), ts(s), None if e is None else ts(e)])
        t.append(tables(sessions=table(T, rows)))
    return t
