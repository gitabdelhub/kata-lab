from kit import table, tables, rng

ID = "e18t3"
NAME = "Monthly Growth with Empty Months"
LANG = "sql"
MINUTES = 15
TAGS = ["generate_series", "mois sans vente", "LAG", "division par zéro"]
DESC = """
<p>The table <b>orders</b> has the columns <code>order_id</code>, <code>region</code>, <code>ordered_at</code> (timestamp) and <code>amount</code> (numeric).</p>
<p>Finance wants, for each region, one row for <b>every</b> month from the first month with an order in this region to the last month with an order in this region, including months without orders (revenue <code>0</code>).</p>
<p>Your task is to return the columns <code>region</code>, <code>month</code> (date of the first day of the month), <code>revenue</code> (sum of <code>amount</code>, rounded to 2 decimals) and <code>growth_pct</code>: the change from the previous month of the same region in percent, rounded to 1 decimal, <code>NULL</code> for the first month and when the previous month revenue is <code>0</code>. Sort by <code>region</code>, then <code>month</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH b AS (
  SELECT region, MIN(date_trunc('month', ordered_at))::date AS f, MAX(date_trunc('month', ordered_at))::date AS l
  FROM orders GROUP BY region
), m AS (
  SELECT region, gs::date AS month FROM b, generate_series(f, l, interval '1 month') AS gs
), r AS (
  SELECT m.region, m.month, COALESCE(SUM(o.amount), 0) AS revenue
  FROM m LEFT JOIN orders o ON o.region = m.region AND date_trunc('month', o.ordered_at)::date = m.month
  GROUP BY m.region, m.month
)
SELECT region, month, ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * (revenue - LAG(revenue) OVER w) / NULLIF(LAG(revenue) OVER w, 0), 1) AS growth_pct
FROM r
WINDOW w AS (PARTITION BY region ORDER BY month)
ORDER BY region, month;
"""
MUTANTS = [
    """
WITH r AS (SELECT region, date_trunc('month', ordered_at)::date AS month, SUM(amount) AS revenue FROM orders GROUP BY 1, 2)
SELECT region, month, ROUND(revenue, 2) AS revenue, ROUND(100.0 * (revenue - LAG(revenue) OVER w) / NULLIF(LAG(revenue) OVER w, 0), 1) AS growth_pct
FROM r WINDOW w AS (PARTITION BY region ORDER BY month) ORDER BY region, month;
""",
    """
WITH b AS (SELECT MIN(date_trunc('month', ordered_at))::date AS f, MAX(date_trunc('month', ordered_at))::date AS l FROM orders),
m AS (SELECT DISTINCT o.region, gs::date AS month FROM b, orders o, generate_series(f, l, interval '1 month') AS gs),
r AS (SELECT m.region, m.month, COALESCE(SUM(o.amount), 0) AS revenue FROM m LEFT JOIN orders o ON o.region = m.region AND date_trunc('month', o.ordered_at)::date = m.month GROUP BY m.region, m.month)
SELECT region, month, ROUND(revenue, 2) AS revenue, ROUND(100.0 * (revenue - LAG(revenue) OVER w) / NULLIF(LAG(revenue) OVER w, 0), 1) AS growth_pct
FROM r WINDOW w AS (PARTITION BY region ORDER BY month) ORDER BY region, month;
""",
    """
WITH b AS (SELECT region, MIN(date_trunc('month', ordered_at))::date AS f, MAX(date_trunc('month', ordered_at))::date AS l FROM orders GROUP BY region),
m AS (SELECT region, gs::date AS month FROM b, generate_series(f, l, interval '1 month') AS gs),
r AS (SELECT m.region, m.month, COALESCE(SUM(o.amount), 0) AS revenue FROM m LEFT JOIN orders o ON o.region = m.region AND date_trunc('month', o.ordered_at)::date = m.month GROUP BY m.region, m.month)
SELECT region, month, ROUND(revenue, 2) AS revenue, ROUND(100.0 * (revenue - LAG(revenue) OVER w) / NULLIF(revenue, 0), 1) AS growth_pct
FROM r WINDOW w AS (PARTITION BY region ORDER BY month) ORDER BY region, month;
""",
]
O = "order_id INT, region TEXT, ordered_at TIMESTAMP, amount NUMERIC(10,2)"


def tests():
    t = [tables(orders=table(O, [[1, "north", "2026-01-15 10:00:00", 100.00], [2, "north", "2026-01-20 10:00:00", 50.00], [3, "north", "2026-02-02 10:00:00", 120.00],
                                 [4, "north", "2026-04-30 23:00:00", 60.00], [5, "south", "2026-02-10 09:00:00", 80.00], [6, "south", "2026-03-01 00:00:00", 0.00],
                                 [7, "south", "2026-04-11 12:00:00", 40.00]])),
         tables(orders=table(O, [[1, "x", "2025-12-31 23:59:00", 10.00], [2, "x", "2026-01-01 00:00:00", 13.33]]))]
    r = rng(1803)
    for _ in range(7):
        rows = []
        for n in range(1, r.randint(4, 20)):
            rows.append([n, r.choice(["north", "south", "east"]), f"2026-{r.randint(1, 8):02d}-{r.randint(1, 28):02d} 12:00:00", r.choice([0, 10, 25.5, 99.99, 140])])
        t.append(tables(orders=table(O, rows)))
    return t
