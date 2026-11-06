from kit import table, tables, rng, ts

ID = "h06t3"
NAME = "Hourly Latency Report"
LANG = "sql"
MINUTES = 20
TAGS = ["generate_series", "heures vides", "percentile_cont", "FILTER", "LAG"]
DESC = """
<p>The table <b>requests</b> has the columns <code>req_id</code>, <code>service</code>, <code>ts</code> (timestamp), <code>latency_ms</code> and <code>status</code> (HTTP status code). A request is an <b>error</b> when its status is 500 or more.</p>
<p>Build an hourly report for each service. It must contain <b>every hour</b> from the hour of the first request of the service to the hour of its last request, including hours with no request at all. An hour is written as the timestamp truncated to the hour.</p>
<p>For each service and hour, compute <code>requests</code> (number of requests), <code>errors</code>, <code>p95_ms</code> (the 95th percentile of the latency of the <b>non-error</b> requests, continuous interpolation, rounded to 1 decimal, <code>NULL</code> when there is no such request) and <code>change_pct</code>: the percentage change of <code>p95_ms</code> compared to the previous hour of the same service, computed from the rounded values as <code>100 * (current - previous) / previous</code> and rounded to 1 decimal. <code>change_pct</code> is <code>NULL</code> when one of the two values is <code>NULL</code> or when the previous value is 0.</p>
<p>Your task is to return the columns <code>service</code>, <code>hour</code>, <code>requests</code>, <code>errors</code>, <code>p95_ms</code> and <code>change_pct</code>, sorted by <code>service</code>, then <code>hour</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH b AS (
  SELECT service, date_trunc('hour', MIN(ts)) AS h0, date_trunc('hour', MAX(ts)) AS h1
  FROM requests GROUP BY service
), hrs AS (
  SELECT service, generate_series(h0, h1, INTERVAL '1 hour') AS hour FROM b
), agg AS (
  SELECT service, date_trunc('hour', ts) AS hour, COUNT(*) AS n,
         COUNT(*) FILTER (WHERE status >= 500) AS err,
         percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) FILTER (WHERE status < 500) AS p
  FROM requests GROUP BY service, date_trunc('hour', ts)
), j AS (
  SELECT hrs.service, hrs.hour, COALESCE(n, 0) AS requests, COALESCE(err, 0) AS errors,
         ROUND(p::numeric, 1) AS p95_ms
  FROM hrs LEFT JOIN agg ON agg.service = hrs.service AND agg.hour = hrs.hour
)
SELECT service, hour, requests, errors, p95_ms,
       ROUND(100 * (p95_ms - LAG(p95_ms) OVER w) / NULLIF(LAG(p95_ms) OVER w, 0), 1) AS change_pct
FROM j
WINDOW w AS (PARTITION BY service ORDER BY hour)
ORDER BY service, hour;
"""
MUTANTS = [
    SOLUTION.replace("FROM hrs LEFT JOIN agg ON agg.service = hrs.service AND agg.hour = hrs.hour", "FROM agg AS hrs"),
    SOLUTION.replace("FILTER (WHERE status < 500) AS p", "AS p"),
    SOLUTION.replace("percentile_cont(0.95)", "percentile_disc(0.95)"),
    SOLUTION.replace("COUNT(*) FILTER (WHERE status >= 500) AS err", "COUNT(*) FILTER (WHERE status > 500) AS err"),
]
T = "req_id INT, service TEXT, ts TIMESTAMP, latency_ms INT, status INT"


def tests():
    t = [tables(requests=table(T, [
        [1, "api", ts(0), 100, 200], [2, "api", ts(10), 200, 200], [3, "api", ts(20), 900, 503], [4, "api", ts(30), 300, 200],
        [5, "api", ts(185), 120, 200], [6, "api", ts(190), 80, 404], [7, "auth", ts(5), 50, 500], [8, "auth", ts(70), 40, 200],
        [9, "auth", ts(75), 60, 200]])),
         tables(requests=table(T, [[1, "pay", ts(0), 0, 200], [2, "pay", ts(65), 30, 200], [3, "pay", ts(130), 10, 502], [4, "pay", ts(200), 20, 200]]))]
    r = rng(4063)
    for _ in range(8):
        rows = []
        for i in range(r.randint(8, 45)):
            rows.append([i + 1, r.choice(["api", "auth", "search"]), ts(r.choice([0, 15, 40, 61, 75, 130, 250, 300, 301]) + r.randint(0, 50)),
                         r.choice([10, 25, 40, 80, 120, 300, 1200]), r.choice([200] * 6 + [404, 500, 502, 503])])
        t.append(tables(requests=table(T, rows)))
    return t
