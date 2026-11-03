from kit import table, tables, rng

ID = "e03t3"
NAME = "Top Doctors by Daily Utilization"
LANG = "sql"
MINUTES = 20
TAGS = ["LEFT JOIN", "NULLIF", "DENSE_RANK", "PARTITION BY", "division entière"]
DESC = """
<p>The clinic manager wants to see, every day, which doctors had the busiest schedule compared with the time they made available.</p>
<p>You are given two tables.</p>
<p><b>availability</b> - one row per doctor and per day the doctor opened slots:</p>
<ul><li><code>doctor_id</code> - the ID of the doctor;</li><li><code>day</code> - the date;</li><li><code>minutes_open</code> - the number of minutes the doctor made available that day (integer, can be <code>0</code>).</li></ul>
<p><b>bookings</b> - one row per booking:</p>
<ul><li><code>booking_id</code> - the ID of the booking;</li><li><code>doctor_id</code>, <code>day</code> - the doctor and the date of the booking;</li><li><code>minutes</code> - the length of the booking (integer);</li><li><code>status</code> - <code>'confirmed'</code>, <code>'done'</code> or <code>'cancelled'</code>.</li></ul>
<p>The <b>utilization</b> of a doctor on a day is the sum of <code>minutes</code> of the non-cancelled bookings of that doctor that day, divided by <code>minutes_open</code>, in percent, rounded to 1 decimal. Only doctor-days that appear in <b>availability</b> with <code>minutes_open</code> greater than <code>0</code> are considered; a doctor-day with no booking has a utilization of <code>0</code>. Bookings on a doctor-day without availability are ignored.</p>
<p>Your task is to rank the doctors of each day by utilization, the highest first, with <code>DENSE_RANK</code> (equal utilizations share the same rank), and return the rows with a rank of <code>1</code> or <code>2</code>: <code>day</code>, <code>doctor_id</code>, <code>utilization_pct</code> and <code>rnk</code>. Sort by <code>day</code>, then <code>rnk</code>, then <code>doctor_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH booked AS (
  SELECT doctor_id, day, SUM(minutes) AS booked
  FROM bookings
  WHERE status <> 'cancelled'
  GROUP BY doctor_id, day
), util AS (
  SELECT a.day, a.doctor_id,
         ROUND(100.0 * COALESCE(b.booked, 0) / NULLIF(a.minutes_open, 0), 1) AS utilization_pct
  FROM availability a
  LEFT JOIN booked b ON b.doctor_id = a.doctor_id AND b.day = a.day
  WHERE a.minutes_open > 0
), ranked AS (
  SELECT *, DENSE_RANK() OVER (PARTITION BY day ORDER BY utilization_pct DESC) AS rnk
  FROM util
)
SELECT day, doctor_id, utilization_pct, rnk
FROM ranked
WHERE rnk <= 2
ORDER BY day, rnk, doctor_id;
"""
MUTANTS = [
    """
WITH booked AS (SELECT doctor_id, day, SUM(minutes) AS booked FROM bookings WHERE status <> 'cancelled' GROUP BY doctor_id, day),
util AS (SELECT a.day, a.doctor_id, ROUND(100.0 * b.booked / a.minutes_open, 1) AS utilization_pct FROM availability a JOIN booked b ON b.doctor_id = a.doctor_id AND b.day = a.day WHERE a.minutes_open > 0),
ranked AS (SELECT *, DENSE_RANK() OVER (PARTITION BY day ORDER BY utilization_pct DESC) AS rnk FROM util)
SELECT day, doctor_id, utilization_pct, rnk FROM ranked WHERE rnk <= 2 ORDER BY day, rnk, doctor_id;
""",
    """
WITH booked AS (SELECT doctor_id, day, SUM(minutes) AS booked FROM bookings WHERE status <> 'cancelled' GROUP BY doctor_id, day),
util AS (SELECT a.day, a.doctor_id, ROUND(100.0 * COALESCE(b.booked, 0) / NULLIF(a.minutes_open, 0), 1) AS utilization_pct FROM availability a LEFT JOIN booked b ON b.doctor_id = a.doctor_id AND b.day = a.day WHERE a.minutes_open > 0),
ranked AS (SELECT *, RANK() OVER (PARTITION BY day ORDER BY utilization_pct DESC) AS rnk FROM util)
SELECT day, doctor_id, utilization_pct, rnk FROM ranked WHERE rnk <= 2 ORDER BY day, rnk, doctor_id;
""",
    """
WITH booked AS (SELECT doctor_id, day, SUM(minutes) AS booked FROM bookings GROUP BY doctor_id, day),
util AS (SELECT a.day, a.doctor_id, ROUND(100.0 * COALESCE(b.booked, 0) / NULLIF(a.minutes_open, 0), 1) AS utilization_pct FROM availability a LEFT JOIN booked b ON b.doctor_id = a.doctor_id AND b.day = a.day WHERE a.minutes_open > 0),
ranked AS (SELECT *, DENSE_RANK() OVER (PARTITION BY day ORDER BY utilization_pct DESC) AS rnk FROM util)
SELECT day, doctor_id, utilization_pct, rnk FROM ranked WHERE rnk <= 2 ORDER BY day, rnk, doctor_id;
""",
]
A = "doctor_id TEXT, day DATE, minutes_open INT"
B = "booking_id INT, doctor_id TEXT, day DATE, minutes INT, status TEXT"


def tests():
    t = [tables(availability=table(A, [["d1", "2026-03-02", 240], ["d2", "2026-03-02", 120], ["d3", "2026-03-02", 120], ["d4", "2026-03-02", 0], ["d1", "2026-03-03", 60]]),
                bookings=table(B, [[1, "d1", "2026-03-02", 60, "done"], [2, "d1", "2026-03-02", 60, "confirmed"], [3, "d2", "2026-03-02", 60, "done"],
                                   [4, "d3", "2026-03-02", 90, "cancelled"], [5, "d4", "2026-03-02", 30, "done"], [6, "d5", "2026-03-03", 30, "done"]])),
         tables(availability=table(A, [["x", "2026-03-05", 100], ["y", "2026-03-05", 100], ["z", "2026-03-05", 100]]),
                bookings=table(B, [[1, "x", "2026-03-05", 20, "done"], [2, "y", "2026-03-05", 20, "done"], [3, "z", "2026-03-05", 10, "done"]]))]
    r = rng(52)
    for k in range(7):
        av, bk, n = [], [], 0
        for day in ["2026-03-02", "2026-03-03", "2026-03-04"][: 1 + k % 3]:
            for d in r.sample(["d1", "d2", "d3", "d4", "d5"], r.randint(2, 5)):
                av.append([d, day, r.choice([0, 60, 120, 240, 480])])
                for _ in range(r.randint(0, 4)):
                    n += 1
                    bk.append([n, d, day, r.choice([15, 30, 60]), r.choice(["confirmed", "done", "cancelled"])])
            n += 1
            bk.append([n, "d9", day, 30, "done"])
        t.append(tables(availability=table(A, av), bookings=table(B, bk)))
    return t
