from kit import table, tables, rng

ID = "e09t3"
NAME = "Worst Routes On-Time Rate"
LANG = "sql"
MINUTES = 15
TAGS = ["FILTER", "HAVING", "RANK", "route = paire ordonnée"]
DESC = """
<p>An airline ranks its routes by punctuality. You have the table <b>flights</b> with the columns <code>flight_id</code>, <code>origin</code>, <code>destination</code>, <code>flight_date</code> (date), <code>delay_min</code> (integer, <code>NULL</code> when the flight was cancelled).</p>
<p>A route is an ordered pair <code>(origin, destination)</code>: <code>CMN → LFW</code> and <code>LFW → CMN</code> are two routes. Cancelled flights count as flights of the route, but they are never on time. A flight is on time when its delay is at most <code>15</code> minutes.</p>
<p>Only routes with at least <code>3</code> flights are ranked. Your task is to return the <b>3 worst ranks</b>: the columns <code>route</code> (text, <code>origin || '-' || destination</code>), <code>flights</code>, <code>on_time_pct</code> (rounded to 1 decimal) and <code>rank</code>, where rank <code>1</code> is the lowest on-time percentage and routes with the same rounded percentage share the same rank, with gaps after ties (<code>RANK()</code>). Return all routes whose rank is at most <code>3</code>, sorted by <code>rank</code>, then <code>route</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH r AS (
  SELECT origin || '-' || destination AS route,
         COUNT(*) AS flights,
         ROUND(100.0 * COUNT(*) FILTER (WHERE delay_min <= 15) / COUNT(*), 1) AS on_time_pct
  FROM flights
  GROUP BY origin, destination
  HAVING COUNT(*) >= 3
),
k AS (SELECT *, RANK() OVER (ORDER BY on_time_pct) AS rank FROM r)
SELECT route, flights, on_time_pct, rank FROM k WHERE rank <= 3 ORDER BY rank, route;
"""
MUTANTS = [
    """
WITH r AS (SELECT origin || '-' || destination AS route, COUNT(*) AS flights, ROUND(100.0 * COUNT(*) FILTER (WHERE delay_min <= 15) / COUNT(delay_min), 1) AS on_time_pct
  FROM flights GROUP BY origin, destination HAVING COUNT(*) >= 3),
k AS (SELECT *, RANK() OVER (ORDER BY on_time_pct) AS rank FROM r)
SELECT route, flights, on_time_pct, rank FROM k WHERE rank <= 3 ORDER BY rank, route;
""",
    """
WITH r AS (SELECT LEAST(origin, destination) || '-' || GREATEST(origin, destination) AS route, COUNT(*) AS flights, ROUND(100.0 * COUNT(*) FILTER (WHERE delay_min <= 15) / COUNT(*), 1) AS on_time_pct
  FROM flights GROUP BY 1 HAVING COUNT(*) >= 3),
k AS (SELECT *, RANK() OVER (ORDER BY on_time_pct) AS rank FROM r)
SELECT route, flights, on_time_pct, rank FROM k WHERE rank <= 3 ORDER BY rank, route;
""",
    """
WITH r AS (SELECT origin || '-' || destination AS route, COUNT(*) AS flights, ROUND(100.0 * COUNT(*) FILTER (WHERE delay_min <= 15) / COUNT(*), 1) AS on_time_pct
  FROM flights GROUP BY origin, destination HAVING COUNT(*) >= 3),
k AS (SELECT *, DENSE_RANK() OVER (ORDER BY on_time_pct) AS rank FROM r)
SELECT route, flights, on_time_pct, rank FROM k WHERE rank <= 3 ORDER BY rank, route;
""",
]
FL = "flight_id INT, origin VARCHAR(3), destination VARCHAR(3), flight_date DATE, delay_min INT"


def tests():
    rows, i = [], 0
    for o, d, delays in [("CMN", "LFW", [0, 20, None, 5]), ("LFW", "CMN", [30, 40, 10]), ("CMN", "DSS", [0, 0, 0]), ("DSS", "ABJ", [16, 16, 0, None]), ("ABJ", "ACC", [99, 99]),
                         ("CMN", "CDG", [0, 60, 0, 60]), ("CDG", "CMN", [1, 2, 3, 4, 100])]:
        for x in delays:
            i += 1
            rows.append([i, o, d, "2026-03-01", x])
    t = [tables(flights=table(FL, rows)),
         tables(flights=table(FL, [[1, "A", "B", "2026-03-01", 0], [2, "A", "B", "2026-03-02", 50], [3, "A", "B", "2026-03-03", None], [4, "B", "A", "2026-03-01", 0],
                                   [5, "B", "A", "2026-03-02", 0], [6, "B", "A", "2026-03-03", 16]]))]
    r = rng(903)
    for _ in range(7):
        rows = []
        for i in range(1, r.randint(10, 40)):
            o, d = r.sample(["CMN", "LFW", "DSS", "ABJ"], 2)
            rows.append([i, o, d, f"2026-03-0{r.randint(1, 9)}", r.choice([None, 0, 5, 15, 16, 30, 120])])
        t.append(tables(flights=table(FL, rows)))
    return t
