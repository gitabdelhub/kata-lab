from kit import table, tables, rng

ID = "e00t2"
NAME = "Monthly Customer Retention"
LANG = "sql"
MINUTES = 15
TAGS = ["date_trunc", "LAG", "division entière", "NULLIF"]
DESC = """
<p>An online shop wants to follow how many customers come back from one month to the next.</p>
<p>You have the table <b>orders</b>, which describes every order. It has the following columns:</p>
<ul><li><code>order_id</code> - the ID of the order;</li><li><code>customer_id</code> - the ID of the customer;</li><li><code>ordered_on</code> - the date of the order;</li><li><code>amount</code> - the amount of the order.</li></ul>
<p>A customer is <b>active</b> in a month if they placed at least one order during that calendar month. A customer is <b>returning</b> in a month if they are active in that month <b>and</b> in the previous calendar month.</p>
<p>Your task is to return one row for every month that has at least one order, with:</p>
<ol><li><code>month</code> - the first day of the month (date);</li><li><code>active</code> - the number of active customers;</li><li><code>returning</code> - the number of returning customers;</li><li><code>retention_pct</code> - <code>returning</code> divided by the number of active customers of the previous calendar month, in percent, rounded to 1 decimal. It is null when the previous calendar month has no active customer.</li></ol>
<p>Sort by <code>month</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>March has no order, so in April <code>retention_pct</code> is null, and no customer is returning.</p>
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH active AS (
  SELECT DISTINCT customer_id, date_trunc('month', ordered_on)::date AS month
  FROM orders
), counts AS (
  SELECT month, COUNT(*) AS active FROM active GROUP BY month
), ret AS (
  SELECT a.month, COUNT(*) AS returning
  FROM active a
  JOIN active p ON p.customer_id = a.customer_id
               AND p.month = (a.month - INTERVAL '1 month')::date
  GROUP BY a.month
)
SELECT c.month,
       c.active,
       COALESCE(r.returning, 0) AS returning,
       ROUND(100.0 * COALESCE(r.returning, 0) / NULLIF(prev.active, 0), 1) AS retention_pct
FROM counts c
LEFT JOIN ret r ON r.month = c.month
LEFT JOIN counts prev ON prev.month = (c.month - INTERVAL '1 month')::date
ORDER BY c.month;
"""
MUTANTS = [
    """
WITH active AS (SELECT DISTINCT customer_id, date_trunc('month', ordered_on)::date AS month FROM orders),
counts AS (SELECT month, COUNT(*) AS active FROM active GROUP BY month),
ret AS (SELECT a.month, COUNT(*) AS returning FROM active a JOIN active p ON p.customer_id = a.customer_id AND p.month = (a.month - INTERVAL '1 month')::date GROUP BY a.month),
lagged AS (SELECT month, active, LAG(active) OVER (ORDER BY month) AS prev_active FROM counts)
SELECT l.month, l.active, COALESCE(r.returning, 0) AS returning, ROUND(100.0 * COALESCE(r.returning, 0) / NULLIF(l.prev_active, 0), 1) AS retention_pct
FROM lagged l LEFT JOIN ret r ON r.month = l.month ORDER BY l.month;
""",
    """
WITH active AS (SELECT DISTINCT customer_id, date_trunc('month', ordered_on)::date AS month FROM orders),
counts AS (SELECT month, COUNT(*) AS active FROM active GROUP BY month),
ret AS (SELECT a.month, COUNT(*) AS returning FROM active a JOIN active p ON p.customer_id = a.customer_id AND p.month = (a.month - INTERVAL '1 month')::date GROUP BY a.month)
SELECT c.month, c.active, COALESCE(r.returning, 0) AS returning, ROUND(100 * COALESCE(r.returning, 0) / NULLIF(prev.active, 0), 1) AS retention_pct
FROM counts c LEFT JOIN ret r ON r.month = c.month LEFT JOIN counts prev ON prev.month = (c.month - INTERVAL '1 month')::date ORDER BY c.month;
""",
]
C = "order_id INT, customer_id INT, ordered_on DATE, amount NUMERIC(10,2)"


def tests():
    t = [tables(orders=table(C, [[1, 1, "2026-01-05", 20], [2, 2, "2026-01-20", 35], [3, 1, "2026-01-25", 10], [4, 1, "2026-02-02", 50],
                                 [5, 3, "2026-02-14", 12], [6, 3, "2026-04-01", 8], [7, 2, "2026-04-30", 40]])),
         tables(orders=table(C, [[1, 7, "2026-12-31", 5], [2, 7, "2027-01-01", 5], [3, 8, "2027-01-02", 5]]))]
    r = rng(21)
    for k in range(6):
        rows = []
        for i in range(25 + 10 * k):
            m = r.choice([1, 2, 3, 3, 5, 6]) if k % 2 else r.randint(1, 4)
            rows.append([i + 1, r.randint(1, 8 + k), f"2026-{m:02d}-{r.randint(1, 28):02d}", round(r.uniform(5, 99), 2)])
        t.append(tables(orders=table(C, rows)))
    return t
