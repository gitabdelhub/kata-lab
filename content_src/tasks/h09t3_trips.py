from kit import table, tables, rng, ts

ID = "h09t3"
NAME = "Passenger Trips from Flight Legs"
LANG = "sql"
MINUTES = 20
TAGS = ["îlots", "LAG", "intervalles de temps", "string_agg ordonné", "array_agg"]
DESC = """
<p>The table <b>legs</b> has the columns <code>leg_id</code>, <code>passenger_id</code>, <code>origin</code>, <code>dest</code>, <code>dep</code> and <code>arr</code> (timestamps). Each row is one flight taken by a passenger.</p>
<p>Sort the legs of a passenger by <code>dep</code>. A leg <b>continues the trip</b> of the passenger's previous leg when both conditions hold: it departs from the airport where the previous leg arrived (<code>origin</code> = previous <code>dest</code>), and the layover (its <code>dep</code> minus the previous <code>arr</code>) is between 45 minutes and 6 hours, both included. Otherwise the leg starts a new trip. Trips are numbered 1, 2, 3... per passenger in time order.</p>
<p>Your task is to return one row per trip with the columns <code>passenger_id</code>, <code>trip_no</code>, <code>route</code> (the airports of the trip joined with <code>&gt;</code>, for example <code>CMN&gt;CDG&gt;JFK</code>), <code>legs</code>, <code>total_hours</code> (from the first departure to the last arrival, rounded to 1 decimal) and <code>longest_layover_min</code> (the longest layover of the trip in minutes, <code>NULL</code> for a trip with one leg), sorted by <code>passenger_id</code>, then <code>trip_no</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH l AS (
  SELECT *, LAG(dest) OVER w AS prev_dest, LAG(arr) OVER w AS prev_arr
  FROM legs
  WINDOW w AS (PARTITION BY passenger_id ORDER BY dep)
), f AS (
  SELECT *, (prev_dest = origin AND dep - prev_arr BETWEEN INTERVAL '45 minutes' AND INTERVAL '6 hours') AS cont
  FROM l
), g AS (
  SELECT *, SUM(CASE WHEN cont THEN 0 ELSE 1 END) OVER (PARTITION BY passenger_id ORDER BY dep) AS trip_no,
         CASE WHEN cont THEN EXTRACT(EPOCH FROM dep - prev_arr) / 60 END AS layover
  FROM f
)
SELECT passenger_id, trip_no,
       (array_agg(origin ORDER BY dep))[1] || '>' || string_agg(dest, '>' ORDER BY dep) AS route,
       COUNT(*) AS legs,
       ROUND(EXTRACT(EPOCH FROM MAX(arr) - MIN(dep)) / 3600, 1) AS total_hours,
       MAX(layover)::int AS longest_layover_min
FROM g
GROUP BY passenger_id, trip_no
ORDER BY passenger_id, trip_no;
"""
MUTANTS = [
    SOLUTION.replace(" AND dep - prev_arr BETWEEN INTERVAL '45 minutes' AND INTERVAL '6 hours'", ""),
    SOLUTION.replace("BETWEEN INTERVAL '45 minutes' AND INTERVAL '6 hours'", "> INTERVAL '45 minutes' AND dep - prev_arr < INTERVAL '6 hours'"),
    SOLUTION.replace("(array_agg(origin ORDER BY dep))[1] || '>' || string_agg(dest, '>' ORDER BY dep)", "string_agg(origin, '>' ORDER BY dep)"),
    SOLUTION.replace("SUM(CASE WHEN cont THEN 0 ELSE 1 END)", "SUM(CASE WHEN cont IS FALSE THEN 1 ELSE 0 END)"),
]
T = "leg_id INT, passenger_id INT, origin TEXT, dest TEXT, dep TIMESTAMP, arr TIMESTAMP"


def tests():
    t = [tables(legs=table(T, [
        [1, 1, "CMN", "CDG", ts(0), ts(180)], [2, 1, "CDG", "JFK", ts(240), ts(720)], [3, 1, "JFK", "CMN", ts(5000), ts(5420)],
        [4, 2, "RAK", "MAD", ts(60), ts(150)], [5, 2, "MAD", "LIS", ts(180), ts(250)], [6, 2, "LIS", "RAK", ts(295), ts(380)]])),
         tables(legs=table(T, [[1, 7, "DSS", "CMN", ts(0), ts(200)], [2, 7, "CMN", "IST", ts(560), ts(800)], [3, 7, "IST", "DXB", ts(845), ts(1100)],
                               [4, 7, "DXB", "BOM", ts(1461), ts(1600)]]))]
    r = rng(4093)
    ap = ["CMN", "CDG", "MAD", "LIS", "JFK", "DSS"]
    for _ in range(8):
        rows, n = [], 0
        for p in range(1, r.randint(2, 4)):
            m, here = r.randint(0, 100), r.choice(ap)
            for _ in range(r.randint(2, 7)):
                n += 1
                dest = r.choice([a for a in ap if a != here])
                dur = r.choice([60, 90, 180, 420])
                origin = here if r.random() < 0.85 else r.choice(ap)
                rows.append([n, p, origin, dest, ts(m), ts(m + dur)])
                m += dur + r.choice([30, 44, 45, 120, 360, 361, 2000])
                here = dest
        t.append(tables(legs=table(T, rows)))
    return t
