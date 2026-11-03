from kit import table, tables, rng

ID = "e06t3"
NAME = "Slowest Endpoints p90"
LANG = "sql"
MINUTES = 15
TAGS = ["PERCENTILE_CONT", "HAVING", "FILTER", "ROUND numeric"]
DESC = """
<p>The platform team wants to find the slowest API endpoints. You have the table <b>requests</b> with the columns <code>request_id</code>, <code>endpoint</code>, <code>status_code</code> (integer) and <code>latency_ms</code> (integer).</p>
<p>For every endpoint, consider only the requests with a status code lower than <code>500</code> (server errors are analysed elsewhere). Endpoints with fewer than <code>5</code> such requests are not reported.</p>
<p>Your task is to return the columns <code>endpoint</code>, <code>requests</code> (number of considered requests), <code>p90_ms</code> (the 90th percentile of <code>latency_ms</code> with <b>linear interpolation</b>, as computed by <code>PERCENTILE_CONT(0.9)</code>, rounded to 1 decimal) and <code>error_rate_pct</code> (the percentage of <b>all</b> the requests of the endpoint, including server errors, that have a status code of <code>500</code> or more, rounded to 1 decimal). Sort by <code>p90_ms</code> descending, then <code>endpoint</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
SELECT endpoint,
       COUNT(*) FILTER (WHERE status_code < 500) AS requests,
       ROUND((PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY latency_ms) FILTER (WHERE status_code < 500))::numeric, 1) AS p90_ms,
       ROUND(100.0 * COUNT(*) FILTER (WHERE status_code >= 500) / COUNT(*), 1) AS error_rate_pct
FROM requests
GROUP BY endpoint
HAVING COUNT(*) FILTER (WHERE status_code < 500) >= 5
ORDER BY p90_ms DESC, endpoint;
"""
MUTANTS = [
    """
SELECT endpoint, COUNT(*) AS requests, ROUND((PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY latency_ms))::numeric, 1) AS p90_ms,
       ROUND(100.0 * COUNT(*) FILTER (WHERE status_code >= 500) / COUNT(*), 1) AS error_rate_pct
FROM requests GROUP BY endpoint HAVING COUNT(*) >= 5 ORDER BY p90_ms DESC, endpoint;
""",
    """
SELECT endpoint, COUNT(*) FILTER (WHERE status_code < 500) AS requests, ROUND((PERCENTILE_DISC(0.9) WITHIN GROUP (ORDER BY latency_ms) FILTER (WHERE status_code < 500))::numeric, 1) AS p90_ms,
       ROUND(100.0 * COUNT(*) FILTER (WHERE status_code >= 500) / COUNT(*), 1) AS error_rate_pct
FROM requests GROUP BY endpoint HAVING COUNT(*) FILTER (WHERE status_code < 500) >= 5 ORDER BY p90_ms DESC, endpoint;
""",
    """
SELECT endpoint, COUNT(*) AS requests, ROUND((PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY latency_ms))::numeric, 1) AS p90_ms, 0.0 AS error_rate_pct
FROM requests WHERE status_code < 500 GROUP BY endpoint HAVING COUNT(*) >= 5 ORDER BY p90_ms DESC, endpoint;
""",
]
R = "request_id INT, endpoint VARCHAR(30), status_code INT, latency_ms INT"


def tests():
    rows, i = [], 0
    for ep, lats, codes in [("/orders", [100, 120, 130, 150, 900, 160], [200, 200, 201, 200, 503, 200]), ("/search", [50, 60, 70, 80, 90, 1000], [200] * 6),
                            ("/login", [10, 20, 30], [200, 200, 500])]:
        for l, c in zip(lats, codes):
            i += 1
            rows.append([i, ep, c, l])
    t = [tables(requests=table(R, rows)),
         tables(requests=table(R, [[1, "/a", 200, 10], [2, "/a", 404, 20], [3, "/a", 200, 30], [4, "/a", 200, 40], [5, "/a", 500, 5000], [6, "/a", 200, 50],
                                   [7, "/b", 200, 15], [8, "/b", 200, 15], [9, "/b", 200, 15], [10, "/b", 200, 15], [11, "/b", 200, 15]]))]
    r = rng(603)
    for _ in range(7):
        rows = [[i, r.choice(["/a", "/b", "/c", "/d"]), r.choice([200, 200, 200, 404, 500, 503]), r.randint(5, 2000)] for i in range(1, r.randint(25, 60))]
        t.append(tables(requests=table(R, rows)))
    return t
