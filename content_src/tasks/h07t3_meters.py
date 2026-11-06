from kit import table, tables, rng, ts

ID = "h07t3"
NAME = "Daily Consumption with Meter Resets"
LANG = "sql"
MINUTES = 20
TAGS = ["compteurs cumulés", "remise à zéro", "doublons", "LAG", "moyenne par fenêtre"]
DESC = """
<p>The table <b>readings</b> has the columns <code>meter_id</code>, <code>read_at</code> (timestamp) and <code>counter</code> (numeric, kWh). The counter of a meter is cumulative: the consumption between two readings is the difference between the two counters.</p>
<p>The data has three problems:</p>
<ul><li>The same reading can be sent several times: for a meter and a <code>read_at</code>, keep only the highest counter.</li>
<li>When a meter is replaced, its counter restarts from 0. When a counter is lower than the previous one, the consumption of that interval is the new counter itself (counted from 0).</li>
<li>The first reading of a meter has no previous value: its consumption is 0.</li></ul>
<p>The consumption of an interval belongs to the day (date) of its later reading. For each meter and each day with at least one reading, compute <code>kwh</code> (total consumption of the day, rounded to 1 decimal) and <code>readings</code> (number of distinct reading times that day). A day is flagged <code>'SPIKE'</code> when its unrounded consumption is more than 3 times the average daily consumption of that meter (average over the days listed for that meter), else <code>'OK'</code>.</p>
<p>Your task is to return the columns <code>meter_id</code>, <code>day</code>, <code>kwh</code>, <code>readings</code> and <code>flag</code>, sorted by <code>meter_id</code>, then <code>day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH d AS (
  SELECT meter_id, read_at, MAX(counter) AS c FROM readings GROUP BY meter_id, read_at
), l AS (
  SELECT *, LAG(c) OVER (PARTITION BY meter_id ORDER BY read_at) AS pc FROM d
), u AS (
  SELECT meter_id, read_at::date AS day,
         CASE WHEN pc IS NULL THEN 0 WHEN c < pc THEN c ELSE c - pc END AS k
  FROM l
), g AS (
  SELECT meter_id, day, SUM(k) AS kwh, COUNT(*) AS readings FROM u GROUP BY meter_id, day
)
SELECT meter_id, day, ROUND(kwh, 1) AS kwh, readings,
       CASE WHEN kwh > 3 * AVG(kwh) OVER (PARTITION BY meter_id) THEN 'SPIKE' ELSE 'OK' END AS flag
FROM g
ORDER BY meter_id, day;
"""
MUTANTS = [
    SOLUTION.replace("SELECT meter_id, read_at, MAX(counter) AS c FROM readings GROUP BY meter_id, read_at", "SELECT meter_id, read_at, counter AS c FROM readings"),
    SOLUTION.replace("WHEN c < pc THEN c ELSE c - pc END", "ELSE c - pc END"),
    SOLUTION.replace("WHEN c < pc THEN c ELSE", "WHEN c < pc THEN 0 ELSE"),
    SOLUTION.replace("MAX(counter) AS c", "MIN(counter) AS c"),
]
T = "meter_id INT, read_at TIMESTAMP, counter NUMERIC(10,1)"


def tests():
    t = [tables(readings=table(T, [
        [1, ts(0), 100.0], [1, ts(600), 104.5], [1, ts(600), 104.0], [1, ts(1500), 110.0], [1, ts(1600), 2.5], [1, ts(3000), 6.0],
        [1, ts(4400), 40.0], [2, ts(60), 50.0]])),
         tables(readings=table(T, [[3, ts(0), 0.0], [3, ts(1440), 1.0], [3, ts(2880), 2.0], [3, ts(4320), 3.0], [3, ts(5760), 30.0]]))]
    r = rng(4073)
    for _ in range(8):
        rows = []
        for m in range(1, r.randint(2, 4)):
            c, minute = r.randint(0, 500) * 1.0, r.randint(0, 300)
            for _ in range(r.randint(3, 12)):
                minute += r.choice([180, 600, 1440, 2000])
                if r.random() < 0.12:
                    c = round(r.random() * 5, 1)
                else:
                    c = round(c + r.choice([0.5, 2.0, 3.5, 8.0, 40.0]), 1)
                rows.append([m, ts(minute), c])
                if r.random() < 0.15:
                    rows.append([m, ts(minute), round(max(c - 1, 0), 1)])
        r.shuffle(rows)
        t.append(tables(readings=table(T, rows)))
    return t
