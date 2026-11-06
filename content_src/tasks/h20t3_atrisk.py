from kit import table, tables, rng, day

ID = "h20t3"
NAME = "Customers at Risk"
LANG = "sql"
MINUTES = 25
TAGS = ["écarts entre commandes", "médiane (percentile_cont)", "plusieurs commandes le même jour", "date de référence", "HAVING"]
DESC = """
<p>The table <b>orders</b> has the columns <code>order_id</code>, <code>customer_id</code>, <code>ordered_on</code> (date) and <code>status</code>. Orders with the status <code>'cancelled'</code> do not count. Several orders of a customer on the same day count as <b>one</b> ordering day.</p>
<p>For a customer, the <b>gaps</b> are the numbers of days between two consecutive ordering days. Only customers with at least 3 ordering days are analysed. Their <b>usual gap</b> is the median of their gaps (continuous median, <code>percentile_cont(0.5)</code>).</p>
<p>The report is made on the reference date <code>2026-12-31</code>. A customer is <b>at risk</b> when the number of days from their last ordering day to the reference date is strictly greater than twice their usual gap.</p>
<p>Your task is to return the customers at risk with the columns <code>customer_id</code>, <code>ordering_days</code>, <code>usual_gap</code> (rounded to 1 decimal), <code>days_since_last</code> and <code>ratio</code> (<code>days_since_last / usual_gap</code>, rounded to 2 decimals), sorted by <code>ratio</code> from the highest, then <code>customer_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH d AS (
  SELECT DISTINCT customer_id, ordered_on FROM orders WHERE status <> 'cancelled'
), g AS (
  SELECT customer_id, ordered_on,
         ordered_on - LAG(ordered_on) OVER (PARTITION BY customer_id ORDER BY ordered_on) AS gap
  FROM d
), s AS (
  SELECT customer_id, COUNT(*) AS ordering_days,
         percentile_cont(0.5) WITHIN GROUP (ORDER BY gap) AS usual,
         DATE '2026-12-31' - MAX(ordered_on) AS days_since_last
  FROM g
  GROUP BY customer_id
  HAVING COUNT(*) >= 3
)
SELECT customer_id, ordering_days, ROUND(usual::numeric, 1) AS usual_gap, days_since_last,
       ROUND((days_since_last / usual)::numeric, 2) AS ratio
FROM s
WHERE days_since_last > 2 * usual
ORDER BY ratio DESC, customer_id;
"""
MUTANTS = [
    SOLUTION.replace("SELECT DISTINCT customer_id, ordered_on FROM orders WHERE status <> 'cancelled'", "SELECT customer_id, ordered_on FROM orders WHERE status <> 'cancelled'"),
    SOLUTION.replace("percentile_cont(0.5)", "percentile_disc(0.5)"),
    SOLUTION.replace("WHERE days_since_last > 2 * usual", "WHERE days_since_last >= 2 * usual"),
    SOLUTION.replace("FROM orders WHERE status <> 'cancelled'", "FROM orders"),
]
T = "order_id INT, customer_id INT, ordered_on DATE, status TEXT"


def tests():
    t = [tables(orders=table(T, [[1, 1, "2026-11-01", "paid"], [2, 1, "2026-11-11", "paid"], [3, 1, "2026-11-21", "paid"], [4, 1, "2026-11-21", "paid"],
                                 [5, 2, "2026-01-01", "paid"], [6, 2, "2026-03-01", "paid"], [7, 2, "2026-04-01", "paid"], [8, 2, "2026-04-02", "paid"],
                                 [9, 3, "2026-12-01", "paid"], [10, 3, "2026-12-30", "cancelled"], [11, 3, "2026-12-11", "paid"], [12, 3, "2026-12-21", "paid"],
                                 [13, 4, "2026-12-01", "paid"], [14, 4, "2026-12-10", "paid"]])),
         tables(orders=table(T, [[1, 7, "2026-12-01", "paid"], [2, 7, "2026-12-03", "paid"], [3, 7, "2026-12-05", "paid"], [4, 7, "2026-12-07", "paid"],
                                 [5, 8, "2026-12-01", "paid"], [6, 8, "2026-12-05", "paid"], [7, 8, "2026-12-11", "paid"],
                                 [8, 9, "2026-12-11", "paid"], [9, 9, "2026-12-16", "paid"], [10, 9, "2026-12-21", "paid"]]))]
    r = rng(4203)
    for _ in range(8):
        rows, n = [], 0
        for c in range(1, r.randint(3, 10)):
            for _ in range(r.randint(2, 8)):
                n += 1
                rows.append([n, c, day(r.randint(200, 360)), r.choice(["paid", "paid", "paid", "cancelled"])])
        t.append(tables(orders=table(T, rows)))
    return t
