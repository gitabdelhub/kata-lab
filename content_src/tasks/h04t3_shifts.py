from kit import table, tables, rng, ts

ID = "h04t3"
NAME = "Courier Shifts and Idle Time"
LANG = "sql"
MINUTES = 20
TAGS = ["îlots à deux niveaux", "MAX cumulé", "intervalles qui se chevauchent", "division"]
DESC = """
<p>The table <b>deliveries</b> has the columns <code>delivery_id</code>, <code>courier_id</code>, <code>picked_at</code>, <code>dropped_at</code> (timestamps) and <code>cancelled</code> (boolean). Cancelled deliveries and deliveries with no <code>dropped_at</code> (lost parcels) are ignored everywhere.</p>
<p>The deliveries of a courier are grouped into <b>shifts</b>. Sort the deliveries of a courier by <code>picked_at</code> (then <code>dropped_at</code>). A delivery starts a new shift when its <code>picked_at</code> is <b>more than 30 minutes</b> after the latest <code>dropped_at</code> seen so far for that courier; a gap of exactly 30 minutes stays in the same shift. Shifts are numbered 1, 2, 3... per courier in time order.</p>
<p>A courier can carry several parcels at once, so deliveries can overlap. The <b>busy time</b> of a shift is the number of minutes during which the courier carried at least one parcel: overlapping minutes count once. The <b>idle percentage</b> is <code>100 * (shift length - busy time) / shift length</code>, where the shift length goes from the first <code>picked_at</code> to the last <code>dropped_at</code> of the shift. When the shift length is 0, the idle percentage is 0.</p>
<p>Your task is to return the columns <code>courier_id</code>, <code>shift_no</code>, <code>shift_start</code>, <code>shift_end</code>, <code>deliveries</code>, <code>busy_minutes</code> (integer) and <code>idle_pct</code> (rounded to 1 decimal), sorted by <code>courier_id</code>, then <code>shift_no</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH d AS (
  SELECT courier_id, picked_at AS s, dropped_at AS e
  FROM deliveries
  WHERE NOT cancelled AND dropped_at IS NOT NULL
), m AS (
  SELECT *, MAX(e) OVER (PARTITION BY courier_id ORDER BY s, e
                         ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING) AS prev_end
  FROM d
), g AS (
  SELECT *,
    SUM(CASE WHEN prev_end IS NULL OR s > prev_end + INTERVAL '30 minutes' THEN 1 ELSE 0 END)
      OVER (PARTITION BY courier_id ORDER BY s, e) AS shift_no,
    SUM(CASE WHEN prev_end IS NULL OR s > prev_end THEN 1 ELSE 0 END)
      OVER (PARTITION BY courier_id ORDER BY s, e) AS blk
  FROM m
), b AS (
  SELECT courier_id, shift_no, blk, MIN(s) AS bs, MAX(e) AS be, COUNT(*) AS n
  FROM g GROUP BY courier_id, shift_no, blk
), sh AS (
  SELECT courier_id, shift_no, MIN(bs) AS shift_start, MAX(be) AS shift_end, SUM(n) AS deliveries,
         SUM(EXTRACT(EPOCH FROM be - bs)) / 60 AS busy,
         EXTRACT(EPOCH FROM MAX(be) - MIN(bs)) / 60 AS len
  FROM b GROUP BY courier_id, shift_no
)
SELECT courier_id, shift_no, shift_start, shift_end, deliveries::int AS deliveries, busy::int AS busy_minutes,
       CASE WHEN len = 0 THEN 0 ELSE ROUND(100 * (len - busy) / len, 1) END AS idle_pct
FROM sh
ORDER BY courier_id, shift_no;
"""
MUTANTS = [
    # LAG au lieu du MAX cumulé : une livraison longue englobante est oubliée
    SOLUTION.replace("MAX(e) OVER (PARTITION BY courier_id ORDER BY s, e\n                         ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)", "LAG(e) OVER (PARTITION BY courier_id ORDER BY s, e)"),
    # temps occupé = somme des durées (les chevauchements comptent deux fois)
    SOLUTION.replace("SUM(CASE WHEN prev_end IS NULL OR s > prev_end THEN 1 ELSE 0 END)\n      OVER (PARTITION BY courier_id ORDER BY s, e) AS blk", "ROW_NUMBER() OVER (PARTITION BY courier_id ORDER BY s, e) AS blk"),
    # annulées non filtrées
    SOLUTION.replace("WHERE NOT cancelled AND dropped_at IS NOT NULL", "WHERE dropped_at IS NOT NULL"),
    # 30 minutes pile = nouveau shift (>= au lieu de >)
    SOLUTION.replace("s > prev_end + INTERVAL '30 minutes'", "s >= prev_end + INTERVAL '30 minutes'"),
    # division entière sur des minutes entières
    SOLUTION.replace("ROUND(100 * (len - busy) / len, 1)", "ROUND(100 * (len::int - busy::int) / len::int, 1)"),
]
T = "delivery_id INT, courier_id INT, picked_at TIMESTAMP, dropped_at TIMESTAMP, cancelled BOOLEAN"


def tests():
    t = [tables(deliveries=table(T, [
        [1, 7, ts(0), ts(20), False], [2, 7, ts(10), ts(35), False], [3, 7, ts(65), ts(80), False],
        [4, 7, ts(200), ts(230), False], [5, 7, ts(205), ts(215), True], [6, 7, ts(300), None, False],
        [7, 9, ts(0), ts(120), False], [8, 9, ts(30), ts(40), False], [9, 9, ts(130), ts(140), False]])),
         tables(deliveries=table(T, [[1, 3, ts(0), ts(0), False], [2, 3, ts(90), ts(100), False], [3, 3, ts(130), ts(131), False],
                                     [4, 4, ts(10), ts(50), True]]))]
    r = rng(4043)
    for k in range(8):
        rows, n = [], 0
        for c in range(1, r.randint(2, 4)):
            m = r.randint(0, 60)
            for _ in range(r.randint(2, 9)):
                n += 1
                m += r.choice([0, 5, 10, 25, 30, 31, 45, 120])
                dur = r.choice([0, 10, 15, 30, 60, 90])
                rows.append([n, c, ts(m), None if r.random() < 0.08 else ts(m + dur), r.random() < 0.12])
        t.append(tables(deliveries=table(T, rows)))
    return t
