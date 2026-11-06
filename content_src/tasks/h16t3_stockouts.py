from kit import table, tables, rng, day

ID = "h16t3"
NAME = "Stock-out Periods with Missing Snapshots"
LANG = "sql"
MINUTES = 25
TAGS = ["jours manquants", "report de la dernière valeur", "COUNT cumulé", "îlots de dates", "doublons"]
DESC = """
<p>The table <b>snapshots</b> has the columns <code>store_id</code>, <code>sku</code>, <code>snap_date</code> (date) and <code>on_hand</code> (units in stock). Stores do not send a snapshot every day: a missing day means that the stock did not change since the last snapshot of the same store and sku. When a store sent several snapshots for the same day and sku, keep the <b>lowest</b> <code>on_hand</code>.</p>
<p>For each store and sku, rebuild the stock of <b>every day</b> from its first to its last snapshot date (both included), carrying the last known value forward over the missing days.</p>
<p>A <b>stock-out period</b> is a run of consecutive days with a stock of 0 lasting <b>at least 2 days</b>.</p>
<p>Your task is to return the columns <code>store_id</code>, <code>sku</code>, <code>start_day</code>, <code>end_day</code> and <code>days</code>, sorted by <code>store_id</code>, then <code>sku</code>, then <code>start_day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH d AS (
  SELECT store_id, sku, snap_date, MIN(on_hand) AS oh FROM snapshots GROUP BY store_id, sku, snap_date
), b AS (
  SELECT store_id, sku, MIN(snap_date) AS a, MAX(snap_date) AS z FROM d GROUP BY store_id, sku
), days AS (
  SELECT store_id, sku, generate_series(a, z, INTERVAL '1 day')::date AS day FROM b
), j AS (
  SELECT days.store_id, days.sku, days.day, d.oh
  FROM days LEFT JOIN d ON d.store_id = days.store_id AND d.sku = days.sku AND d.snap_date = days.day
), c AS (
  SELECT *, COUNT(oh) OVER (PARTITION BY store_id, sku ORDER BY day) AS grp FROM j
), f AS (
  SELECT *, MAX(oh) OVER (PARTITION BY store_id, sku, grp) AS stock FROM c
), z AS (
  SELECT *, day - (ROW_NUMBER() OVER (PARTITION BY store_id, sku ORDER BY day))::int AS isl
  FROM f WHERE stock = 0
)
SELECT store_id, sku, MIN(day) AS start_day, MAX(day) AS end_day, COUNT(*) AS days
FROM z
GROUP BY store_id, sku, isl
HAVING COUNT(*) >= 2
ORDER BY store_id, sku, start_day;
"""
MUTANTS = [
    SOLUTION.replace("FROM days LEFT JOIN d", "FROM days JOIN d"),
    SOLUTION.replace("MIN(on_hand) AS oh", "MAX(on_hand) AS oh"),
    SOLUTION.replace("HAVING COUNT(*) >= 2", "HAVING COUNT(*) >= 1"),
    SOLUTION.replace("SELECT *, MAX(oh) OVER (PARTITION BY store_id, sku, grp) AS stock FROM c", "SELECT *, COALESCE(oh, 0) AS stock FROM c"),
]
T = "store_id INT, sku TEXT, snap_date DATE, on_hand INT"


def tests():
    t = [tables(snapshots=table(T, [[1, "A", day(0), 5], [1, "A", day(2), 0], [1, "A", day(5), 3], [1, "A", day(6), 0], [1, "A", day(7), 2],
                                    [1, "B", day(0), 0], [1, "B", day(1), 4], [1, "B", day(1), 0], [1, "B", day(3), 1],
                                    [2, "A", day(0), 0]])),
         tables(snapshots=table(T, [[3, "X", day(10), 0], [3, "X", day(14), 0], [3, "X", day(15), 7], [3, "Y", day(10), 1], [3, "Y", day(12), 0]]))]
    r = rng(4163)
    for _ in range(8):
        rows = []
        for s in range(1, r.randint(2, 3)):
            for sku in ["A", "B", "C"][: r.randint(1, 3)]:
                for dd in sorted(r.sample(range(0, 30), r.randint(2, 10))):
                    rows.append([s, sku, day(dd), r.choice([0, 0, 0, 1, 3, 8])])
                    if r.random() < 0.1:
                        rows.append([s, sku, day(dd), r.choice([0, 2])])
        r.shuffle(rows)
        t.append(tables(snapshots=table(T, rows)))
    return t
