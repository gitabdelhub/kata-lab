from kit import table, tables, rng

ID = "e01t3"
NAME = "Driver Payout Drops"
LANG = "sql"
MINUTES = 15
TAGS = ["LAG", "PARTITION BY", "division entière", "ROUND numeric"]
DESC = """
<p>Drivers are paid every week. A sudden drop of the weekly payout often means that a driver is about to leave the platform, so the retention team wants a list of these drops.</p>
<p>You have the table <b>payouts</b>, which describes the weekly payouts of drivers. It has the following columns:</p>
<ul><li><code>driver_id</code> - the ID of the driver;</li><li><code>week_start</code> - the Monday of the week (date);</li><li><code>amount</code> - the payout of that week (numeric). A driver has at most one row per week, and weeks where a driver did not work have no row.</li></ul>
<p>For each row, the <b>previous active week</b> is the latest earlier week of the same driver that has a row, even if it is several weeks before. The <b>drop</b> is <code>(previous amount - amount) / previous amount</code>, in percent.</p>
<p>Your task is to return the rows where the drop is strictly greater than <code>30</code> percent, with <code>driver_id</code>, <code>week_start</code>, <code>previous_amount</code>, <code>amount</code> and <code>drop_pct</code> rounded to 1 decimal. Rows with no previous active week, or with a previous amount of <code>0</code>, are never returned. Sort by <code>driver_id</code>, then <code>week_start</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH w AS (
  SELECT driver_id, week_start, amount,
         LAG(amount) OVER (PARTITION BY driver_id ORDER BY week_start) AS previous_amount
  FROM payouts
)
SELECT driver_id, week_start, previous_amount, amount,
       ROUND(100.0 * (previous_amount - amount) / previous_amount, 1) AS drop_pct
FROM w
WHERE previous_amount > 0
  AND 100.0 * (previous_amount - amount) / previous_amount > 30
ORDER BY driver_id, week_start;
"""
MUTANTS = [
    """
WITH w AS (SELECT driver_id, week_start, amount, LAG(amount) OVER (ORDER BY week_start) AS previous_amount FROM payouts)
SELECT driver_id, week_start, previous_amount, amount, ROUND(100.0 * (previous_amount - amount) / previous_amount, 1) AS drop_pct
FROM w WHERE previous_amount > 0 AND 100.0 * (previous_amount - amount) / previous_amount > 30 ORDER BY driver_id, week_start;
""",
    """
SELECT c.driver_id, c.week_start, p.amount AS previous_amount, c.amount, ROUND(100.0 * (p.amount - c.amount) / p.amount, 1) AS drop_pct
FROM payouts c JOIN payouts p ON p.driver_id = c.driver_id AND p.week_start = c.week_start - 7
WHERE p.amount > 0 AND 100.0 * (p.amount - c.amount) / p.amount > 30 ORDER BY c.driver_id, c.week_start;
""",
    """
WITH w AS (SELECT driver_id, week_start, amount, LAG(amount) OVER (PARTITION BY driver_id ORDER BY week_start) AS previous_amount FROM payouts)
SELECT driver_id, week_start, previous_amount, amount, ROUND(100.0 * (previous_amount - amount) / previous_amount, 1) AS drop_pct
FROM w WHERE previous_amount > 0 AND 100.0 * (previous_amount - amount) / previous_amount >= 30 ORDER BY driver_id, week_start;
""",
]
C = "driver_id INT, week_start DATE, amount NUMERIC(10,2)"


def tests():
    t = [tables(payouts=table(C, [[1, "2026-03-02", 1000], [1, "2026-03-09", 600], [2, "2026-03-02", 800], [2, "2026-03-16", 700],
                                  [2, "2026-03-23", 300], [3, "2026-03-09", 0], [3, "2026-03-16", 100]])),
         tables(payouts=table(C, [[5, "2026-01-05", 100], [5, "2026-01-12", 70], [5, "2026-02-02", 40], [6, "2026-01-05", 50]]))]
    r = rng(32)
    import datetime as dt
    for k in range(7):
        rows = []
        for d in range(1, 4 + k):
            day = dt.date(2026, 1, 5)
            for _ in range(r.randint(1, 8)):
                day += dt.timedelta(days=7 * r.choice([1, 1, 1, 2, 3]))
                rows.append([d, day.isoformat(), r.choice([0, 100, 70, 69, 71, 300, 450, 1000, round(r.uniform(50, 900), 2)])])
        r.shuffle(rows)
        t.append(tables(payouts=table(C, rows)))
    return t
