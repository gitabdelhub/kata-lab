from kit import table, tables, rng

ID = "e16t3"
NAME = "Typical Reorder Interval"
LANG = "sql"
MINUTES = 15
TAGS = ["LAG", "écart en jours", "PERCENTILE_CONT", "un seul achat par jour"]
DESC = """
<p>The CRM team wants to know how often customers come back. You have the table <b>purchases</b> with the columns <code>purchase_id</code>, <code>customer_id</code> and <code>purchased_at</code> (timestamp).</p>
<p>Several purchases on the same calendar day count as <b>one</b> visit. The <b>interval</b> between two consecutive visits of a customer is the number of days between their dates.</p>
<p>Your task is to return, for every customer with at least <code>3</code> visits, the columns <code>customer_id</code>, <code>visits</code>, <code>median_interval_days</code> (the median of the intervals, computed with <code>PERCENTILE_CONT(0.5)</code>, rounded to 1 decimal) and <code>max_interval_days</code>, sorted by <code>median_interval_days</code>, then <code>customer_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH v AS (SELECT DISTINCT customer_id, purchased_at::date AS d FROM purchases),
g AS (SELECT customer_id, d, d - LAG(d) OVER (PARTITION BY customer_id ORDER BY d) AS gap FROM v)
SELECT customer_id,
       COUNT(*) AS visits,
       ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gap))::numeric, 1) AS median_interval_days,
       MAX(gap) AS max_interval_days
FROM g
GROUP BY customer_id
HAVING COUNT(*) >= 3
ORDER BY median_interval_days, customer_id;
"""
MUTANTS = [
    """
WITH g AS (SELECT customer_id, purchased_at::date AS d, purchased_at::date - LAG(purchased_at::date) OVER (PARTITION BY customer_id ORDER BY purchased_at) AS gap FROM purchases)
SELECT customer_id, COUNT(*) AS visits, ROUND((PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gap))::numeric, 1) AS median_interval_days, MAX(gap) AS max_interval_days
FROM g GROUP BY customer_id HAVING COUNT(*) >= 3 ORDER BY median_interval_days, customer_id;
""",
    """
WITH v AS (SELECT DISTINCT customer_id, purchased_at::date AS d FROM purchases),
g AS (SELECT customer_id, d, d - LAG(d) OVER (PARTITION BY customer_id ORDER BY d) AS gap FROM v)
SELECT customer_id, COUNT(*) AS visits, ROUND(AVG(gap), 1) AS median_interval_days, MAX(gap) AS max_interval_days
FROM g GROUP BY customer_id HAVING COUNT(*) >= 3 ORDER BY median_interval_days, customer_id;
""",
]
P = "purchase_id INT, customer_id INT, purchased_at TIMESTAMP"


def tests():
    t = [tables(purchases=table(P, [[1, 1, "2026-03-01 10:00:00"], [2, 1, "2026-03-01 18:00:00"], [3, 1, "2026-03-04 09:00:00"], [4, 1, "2026-03-14 09:00:00"],
                                    [5, 2, "2026-03-01 09:00:00"], [6, 2, "2026-03-03 09:00:00"], [7, 2, "2026-03-05 09:00:00"], [8, 2, "2026-03-15 09:00:00"],
                                    [9, 3, "2026-03-01 09:00:00"], [10, 3, "2026-03-02 09:00:00"]])),
         tables(purchases=table(P, [[1, 9, "2026-02-27 23:59:00"], [2, 9, "2026-02-28 00:01:00"], [3, 9, "2026-03-01 12:00:00"], [4, 9, "2026-03-01 13:00:00"]]))]
    r = rng(1603)
    for _ in range(7):
        rows, n = [], 0
        for c in range(1, r.randint(3, 8)):
            for d in r.sample(range(1, 28), r.randint(1, 7)):
                for _ in range(r.choice([1, 1, 2])):
                    n += 1
                    rows.append([n, c, f"2026-03-{d:02d} {r.randint(0, 23):02d}:00:00"])
        t.append(tables(purchases=table(P, rows)))
    return t
