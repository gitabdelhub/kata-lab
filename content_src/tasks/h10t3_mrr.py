from kit import table, tables, rng

ID = "h10t3"
NAME = "MRR Movements"
LANG = "sql"
MINUTES = 25
TAGS = ["grille client × mois", "generate_series", "LAG", "MAX cumulé", "plusieurs lignes par mois"]
DESC = """
<p>The table <b>mrr</b> has the columns <code>customer_id</code>, <code>month</code> (date, always the first day of a month) and <code>amount</code> (numeric). A customer can have several rows for the same month (one per product): the MRR of a customer in a month is the sum of its rows. A customer with no row in a month has an MRR of 0 that month.</p>
<p>Finance wants the MRR movements of every month from the first month present in the table to the last one (months without any row included). For a customer, compare the MRR of the month (<code>cur</code>) with the MRR of the previous month (<code>prev</code>, 0 before the first month of the report):</p>
<ul><li><b>new</b>: <code>cur &gt; 0</code>, <code>prev = 0</code> and the customer never had MRR before this month. Value: <code>cur</code>.</li>
<li><b>reactivation</b>: <code>cur &gt; 0</code>, <code>prev = 0</code> but the customer had MRR in an earlier month. Value: <code>cur</code>.</li>
<li><b>expansion</b>: <code>prev &gt; 0</code> and <code>cur &gt; prev</code>. Value: <code>cur - prev</code>.</li>
<li><b>contraction</b>: <code>cur &gt; 0</code> and <code>cur &lt; prev</code>. Value: <code>cur - prev</code> (negative).</li>
<li><b>churn</b>: <code>prev &gt; 0</code> and <code>cur = 0</code>. Value: <code>-prev</code> (negative).</li></ul>
<p>Your task is to return one row per month with the columns <code>month</code>, <code>new_mrr</code>, <code>expansion_mrr</code>, <code>contraction_mrr</code>, <code>churn_mrr</code>, <code>reactivation_mrr</code> and <code>net_change</code> (sum of the five), sorted by <code>month</code>. A movement with no customer is 0.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH months AS (
  SELECT generate_series(MIN(month), MAX(month), INTERVAL '1 month')::date AS m FROM mrr
), s AS (
  SELECT customer_id, month, SUM(amount) AS amount FROM mrr GROUP BY customer_id, month
), grid AS (
  SELECT c.customer_id, months.m
  FROM (SELECT DISTINCT customer_id FROM mrr) c CROSS JOIN months
), x AS (
  SELECT grid.customer_id, grid.m, COALESCE(s.amount, 0) AS cur
  FROM grid LEFT JOIN s ON s.customer_id = grid.customer_id AND s.month = grid.m
), y AS (
  SELECT *, LAG(cur, 1, 0) OVER (PARTITION BY customer_id ORDER BY m) AS prev,
         COALESCE(MAX(cur) OVER (PARTITION BY customer_id ORDER BY m
                                 ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0) AS before
  FROM x
), z AS (
  SELECT m,
    CASE WHEN cur > 0 AND prev = 0 AND before = 0 THEN cur ELSE 0 END AS nw,
    CASE WHEN prev > 0 AND cur > prev THEN cur - prev ELSE 0 END AS ex,
    CASE WHEN cur > 0 AND cur < prev THEN cur - prev ELSE 0 END AS co,
    CASE WHEN prev > 0 AND cur = 0 THEN -prev ELSE 0 END AS ch,
    CASE WHEN cur > 0 AND prev = 0 AND before > 0 THEN cur ELSE 0 END AS re
  FROM y
)
SELECT m AS month, SUM(nw) AS new_mrr, SUM(ex) AS expansion_mrr, SUM(co) AS contraction_mrr,
       SUM(ch) AS churn_mrr, SUM(re) AS reactivation_mrr, SUM(nw + ex + co + ch + re) AS net_change
FROM z
GROUP BY m
ORDER BY m;
"""
MUTANTS = [
    SOLUTION.replace("SELECT customer_id, month, SUM(amount) AS amount FROM mrr GROUP BY customer_id, month", "SELECT customer_id, month, MAX(amount) AS amount FROM mrr GROUP BY customer_id, month"),
    SOLUTION.replace("CASE WHEN cur > 0 AND prev = 0 AND before = 0 THEN cur ELSE 0 END", "CASE WHEN cur > 0 AND prev = 0 THEN cur ELSE 0 END"),
    SOLUTION.replace("ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING", "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW"),
    SOLUTION.replace("""  SELECT generate_series(MIN(month), MAX(month), INTERVAL '1 month')::date AS m FROM mrr""", """  SELECT DISTINCT month AS m FROM mrr"""),
]
T = "customer_id INT, month DATE, amount NUMERIC(10,2)"


def tests():
    t = [tables(mrr=table(T, [
        [1, "2026-01-01", 100], [1, "2026-02-01", 150], [1, "2026-03-01", 50], [1, "2026-03-01", 20],
        [2, "2026-01-01", 80], [2, "2026-03-01", 90], [3, "2026-02-01", 40], [3, "2026-04-01", 40]])),
         tables(mrr=table(T, [[5, "2026-01-01", 10], [6, "2026-04-01", 25], [5, "2026-04-01", 10]]))]
    r = rng(4103)
    for _ in range(8):
        rows = []
        for c in range(1, r.randint(3, 8)):
            for mo in range(1, 9):
                if r.random() < 0.55:
                    for _ in range(r.choice([1, 1, 1, 2])):
                        rows.append([c, f"2026-{mo:02d}-01", r.choice([20, 40, 50, 100, 120])])
        if not rows:
            rows.append([1, "2026-01-01", 10])
        t.append(tables(mrr=table(T, rows)))
    return t
