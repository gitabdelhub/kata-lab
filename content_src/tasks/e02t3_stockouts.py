from kit import table, tables, rng

ID = "e02t3"
NAME = "Longest Stockout Streak"
LANG = "sql"
MINUTES = 20
TAGS = ["gaps and islands", "ROW_NUMBER", "dates", "PARTITION BY"]
DESC = """
<p>The supply team wants to find the products that stayed out of stock for the longest time.</p>
<p>You have the table <b>daily_stock</b>. It has the following columns:</p>
<ul><li><code>sku</code> - the product code;</li><li><code>day</code> - the date of the stock count (date);</li><li><code>qty</code> - the stock at the end of the day (integer). It is null when the count failed.</li></ul>
<p>There is at most one row per <code>sku</code> and <code>day</code>. Some days are missing.</p>
<p>A <b>stockout day</b> is a row with <code>qty = 0</code>. A <b>stockout streak</b> is a group of stockout days of the same SKU on <b>consecutive calendar days</b>. A missing day, a day with a null quantity, or a day with a positive quantity ends the streak.</p>
<p>Your task is to return, for each SKU that has at least one stockout day, its longest streak with <code>sku</code>, <code>streak_start</code>, <code>streak_end</code> and <code>days</code> (the number of days of the streak). If a SKU has several streaks of the same length, return the earliest one. Sort by <code>days</code> descending, then <code>sku</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>For <code>B</code>, the stockout days of 3 and 5 March are not consecutive, because 4 March is missing, so its longest streaks have <code>1</code> day and the earliest is kept.</p>
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH z AS (
  SELECT sku, day,
         day - (ROW_NUMBER() OVER (PARTITION BY sku ORDER BY day))::int AS grp
  FROM daily_stock
  WHERE qty = 0
), streaks AS (
  SELECT sku, MIN(day) AS streak_start, MAX(day) AS streak_end, COUNT(*) AS days
  FROM z
  GROUP BY sku, grp
), ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY sku ORDER BY days DESC, streak_start) AS rn
  FROM streaks
)
SELECT sku, streak_start, streak_end, days
FROM ranked
WHERE rn = 1
ORDER BY days DESC, sku;
"""
MUTANTS = [
    """
WITH z AS (SELECT sku, day, qty, ROW_NUMBER() OVER (PARTITION BY sku ORDER BY day) - ROW_NUMBER() OVER (PARTITION BY sku, (qty = 0) ORDER BY day) AS grp FROM daily_stock),
s AS (SELECT sku, MIN(day) AS streak_start, MAX(day) AS streak_end, COUNT(*) AS days FROM z WHERE qty = 0 GROUP BY sku, grp),
r AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY sku ORDER BY days DESC, streak_start) AS rn FROM s)
SELECT sku, streak_start, streak_end, days FROM r WHERE rn = 1 ORDER BY days DESC, sku;
""",
    """
WITH z AS (SELECT sku, day, day - (ROW_NUMBER() OVER (PARTITION BY sku ORDER BY day))::int AS grp FROM daily_stock WHERE qty = 0),
s AS (SELECT sku, MIN(day) AS streak_start, MAX(day) AS streak_end, COUNT(*) AS days FROM z GROUP BY sku, grp),
r AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY sku ORDER BY days DESC, streak_start DESC) AS rn FROM s)
SELECT sku, streak_start, streak_end, days FROM r WHERE rn = 1 ORDER BY days DESC, sku;
""",
    """
SELECT sku, MIN(day) AS streak_start, MAX(day) AS streak_end, COUNT(*) AS days FROM daily_stock WHERE qty = 0 GROUP BY sku ORDER BY days DESC, sku;
""",
]
C = "sku TEXT, day DATE, qty INT"


def tests():
    t = [tables(daily_stock=table(C, [["A", "2026-03-01", 5], ["A", "2026-03-02", 0], ["A", "2026-03-03", 0], ["A", "2026-03-04", 0], ["A", "2026-03-05", 2],
                                      ["A", "2026-03-06", 0], ["B", "2026-03-03", 0], ["B", "2026-03-05", 0], ["C", "2026-03-01", 4]])),
         tables(daily_stock=table(C, [["X", "2026-02-27", 0], ["X", "2026-02-28", 0], ["X", "2026-03-01", 0], ["X", "2026-03-02", None], ["X", "2026-03-03", 0],
                                      ["Y", "2026-03-10", 0], ["Y", "2026-03-11", 0], ["Y", "2026-03-12", 0]]))]
    r = rng(42)
    import datetime as dt
    for k in range(7):
        rows = []
        for sku in ["S1", "S2", "S3", "S4", "S5"][: 2 + k % 4]:
            d = dt.date(2026, 2, 20)
            for _ in range(r.randint(3, 14)):
                d += dt.timedelta(days=r.choice([1, 1, 1, 1, 2]))
                rows.append([sku, d.isoformat(), r.choice([0, 0, 0, None, 3, 10])])
        r.shuffle(rows)
        t.append(tables(daily_stock=table(C, rows)))
    return t
