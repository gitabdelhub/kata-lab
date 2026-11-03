from kit import table, tables, rng

ID = "e04t3"
NAME = "Monthly Cohort Retention"
LANG = "sql"
MINUTES = 15
TAGS = ["cohorte", "date_trunc", "LEFT JOIN", "division entière", "statut annulé"]
DESC = """
<p>The growth team measures how many new customers order again the month after their first order. You have the table <b>orders</b> with the columns <code>order_id</code>, <code>customer_id</code>, <code>ordered_at</code> (timestamp) and <code>status</code> (<code>'delivered'</code> or <code>'cancelled'</code>). Cancelled orders never count.</p>
<p>The <b>cohort</b> of a customer is the month of their first counted order. A customer is <b>retained</b> if they have at least one counted order in the calendar month just after their cohort month.</p>
<p>Your task is to return, for every cohort, the columns <code>cohort_month</code> (text, <code>'YYYY-MM'</code>), <code>customers</code> (number of customers in the cohort), <code>retained</code> and <code>retention_pct</code> (<code>100 * retained / customers</code>, rounded to 1 decimal), sorted by <code>cohort_month</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH ok AS (
  SELECT customer_id, date_trunc('month', ordered_at)::date AS m FROM orders WHERE status = 'delivered'
),
first AS (SELECT customer_id, MIN(m) AS cohort FROM ok GROUP BY customer_id),
ret AS (
  SELECT f.customer_id, f.cohort,
         EXISTS (SELECT 1 FROM ok WHERE ok.customer_id = f.customer_id AND ok.m = (f.cohort + INTERVAL '1 month')::date) AS kept
  FROM first f
)
SELECT to_char(cohort, 'YYYY-MM') AS cohort_month,
       COUNT(*) AS customers,
       COUNT(*) FILTER (WHERE kept) AS retained,
       ROUND(100.0 * COUNT(*) FILTER (WHERE kept) / COUNT(*), 1) AS retention_pct
FROM ret
GROUP BY cohort
ORDER BY cohort_month;
"""
MUTANTS = [
    """
WITH ok AS (SELECT customer_id, date_trunc('month', ordered_at)::date AS m FROM orders),
first AS (SELECT customer_id, MIN(m) AS cohort FROM ok GROUP BY customer_id),
ret AS (SELECT f.customer_id, f.cohort, EXISTS (SELECT 1 FROM ok WHERE ok.customer_id = f.customer_id AND ok.m = (f.cohort + INTERVAL '1 month')::date) AS kept FROM first f)
SELECT to_char(cohort, 'YYYY-MM') AS cohort_month, COUNT(*) AS customers, COUNT(*) FILTER (WHERE kept) AS retained, ROUND(100.0 * COUNT(*) FILTER (WHERE kept) / COUNT(*), 1) AS retention_pct FROM ret GROUP BY cohort ORDER BY cohort_month;
""",
    """
WITH ok AS (SELECT customer_id, date_trunc('month', ordered_at)::date AS m FROM orders WHERE status = 'delivered'),
first AS (SELECT customer_id, MIN(m) AS cohort FROM ok GROUP BY customer_id),
ret AS (SELECT f.customer_id, f.cohort, EXISTS (SELECT 1 FROM ok WHERE ok.customer_id = f.customer_id AND ok.m > f.cohort) AS kept FROM first f)
SELECT to_char(cohort, 'YYYY-MM') AS cohort_month, COUNT(*) AS customers, COUNT(*) FILTER (WHERE kept) AS retained, ROUND(100.0 * COUNT(*) FILTER (WHERE kept) / COUNT(*), 1) AS retention_pct FROM ret GROUP BY cohort ORDER BY cohort_month;
""",
    """
WITH ok AS (SELECT customer_id, date_trunc('month', ordered_at)::date AS m FROM orders WHERE status = 'delivered'),
first AS (SELECT customer_id, MIN(m) AS cohort FROM ok GROUP BY customer_id),
ret AS (SELECT f.customer_id, f.cohort, EXISTS (SELECT 1 FROM ok WHERE ok.customer_id = f.customer_id AND ok.m = (f.cohort + INTERVAL '1 month')::date) AS kept FROM first f)
SELECT to_char(cohort, 'YYYY-MM') AS cohort_month, COUNT(*) AS customers, COUNT(*) FILTER (WHERE kept) AS retained, ROUND(100 * COUNT(*) FILTER (WHERE kept) / COUNT(*), 1) AS retention_pct FROM ret GROUP BY cohort ORDER BY cohort_month;
""",
]
O = "order_id INT, customer_id INT, ordered_at TIMESTAMP, status VARCHAR(10)"


def tests():
    t = [tables(orders=table(O, [[1, 1, "2026-01-05 10:00:00", "delivered"], [2, 1, "2026-02-01 09:00:00", "delivered"], [3, 2, "2026-01-20 10:00:00", "delivered"],
                                 [4, 2, "2026-03-02 10:00:00", "delivered"], [5, 3, "2026-01-31 23:59:00", "delivered"], [6, 3, "2026-02-28 12:00:00", "cancelled"],
                                 [7, 4, "2026-02-10 10:00:00", "delivered"], [8, 4, "2026-03-31 10:00:00", "delivered"], [9, 5, "2026-01-02 10:00:00", "cancelled"],
                                 [10, 5, "2026-02-03 10:00:00", "delivered"]])),
         tables(orders=table(O, [[1, 9, "2025-12-31 23:00:00", "delivered"], [2, 9, "2026-01-01 01:00:00", "delivered"], [3, 8, "2025-12-15 10:00:00", "delivered"]]))]
    r = rng(403)
    for _ in range(7):
        rows, n = [], 0
        for c in range(1, r.randint(3, 12)):
            for _ in range(r.randint(1, 4)):
                n += 1
                rows.append([n, c, f"2026-{r.randint(1, 4):02d}-{r.randint(1, 28):02d} {r.randint(0, 23):02d}:00:00", r.choice(["delivered", "delivered", "cancelled"])])
        t.append(tables(orders=table(O, rows)))
    return t
