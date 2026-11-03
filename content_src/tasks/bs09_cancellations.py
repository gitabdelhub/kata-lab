from kit import table, tables, rng, BLSQL

ID = "bs09"
NAME = "Daily Cancellation Rate"
LANG = "sql"
MINUTES = 18
TAGS = ["double jointure", "filtre bannis", "division entière", "ROUND"]
SOURCE = BLSQL + " · Trips and Users (LeetCode 262)"
SUMMARY_FR = "Pour chaque jour du 1er au 3 octobre 2026, calculer le taux d'annulation des courses où ni le client ni le chauffeur n'est banni. Une course annulée par l'un ou l'autre compte."
HINTS = ["Joins users deux fois (une pour le client, une pour le chauffeur) et garde banned = 'No' des deux côtés.",
         "Le taux : ROUND(SUM(CASE WHEN status <> 'completed' THEN 1 ELSE 0 END)::numeric / COUNT(*), 2). Sans ::numeric, la division entière donne 0."]
DESC = """
<p>A ride-hailing company audits its cancellations. You have two tables.</p>
<p><b>trips</b>: <code>id</code>, <code>client_id</code>, <code>driver_id</code>, <code>city_id</code>, <code>status</code> and <code>request_at</code> (date). <code>status</code> is <code>'completed'</code>, <code>'cancelled_by_driver'</code> or <code>'cancelled_by_client'</code>.</p>
<p><b>users</b>: <code>users_id</code>, <code>banned</code> (<code>'Yes'</code> or <code>'No'</code>) and <code>role</code> (<code>'client'</code> or <code>'driver'</code>).</p>
<p>The <b>cancellation rate</b> of a day is the number of cancelled trips (by the client or by the driver) divided by the number of trips of that day, counting <b>only the trips where neither the client nor the driver is banned</b>.</p>
<p>Your task is to return, for every day between <code>2026-10-01</code> and <code>2026-10-03</code> (both included) that has at least one such trip, the columns <code>day</code> and <code>cancellation_rate</code> rounded to <code>2</code> decimals, sorted by <code>day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
SELECT t.request_at AS day,
       ROUND(SUM(CASE WHEN t.status <> 'completed' THEN 1 ELSE 0 END)::numeric / COUNT(*), 2) AS cancellation_rate
FROM trips t
JOIN users c ON c.users_id = t.client_id AND c.banned = 'No'
JOIN users d ON d.users_id = t.driver_id AND d.banned = 'No'
WHERE t.request_at BETWEEN DATE '2026-10-01' AND DATE '2026-10-03'
GROUP BY t.request_at
ORDER BY day;
"""
ALT = ["""
SELECT request_at AS day, ROUND(AVG((status LIKE 'cancelled%')::int), 2) AS cancellation_rate
FROM trips
WHERE client_id NOT IN (SELECT users_id FROM users WHERE banned = 'Yes')
  AND driver_id NOT IN (SELECT users_id FROM users WHERE banned = 'Yes')
  AND request_at >= '2026-10-01' AND request_at < '2026-10-04'
GROUP BY request_at ORDER BY day;
"""]
MUTANTS = [
    """
SELECT t.request_at AS day, ROUND(SUM(CASE WHEN t.status <> 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate
FROM trips t JOIN users c ON c.users_id = t.client_id AND c.banned = 'No' JOIN users d ON d.users_id = t.driver_id AND d.banned = 'No'
WHERE t.request_at BETWEEN DATE '2026-10-01' AND DATE '2026-10-03' GROUP BY t.request_at ORDER BY day;
""",
    """
SELECT t.request_at AS day, ROUND(SUM(CASE WHEN t.status <> 'completed' THEN 1 ELSE 0 END)::numeric / COUNT(*), 2) AS cancellation_rate
FROM trips t JOIN users c ON c.users_id = t.client_id AND c.banned = 'No'
WHERE t.request_at BETWEEN DATE '2026-10-01' AND DATE '2026-10-03' GROUP BY t.request_at ORDER BY day;
""",
    """
SELECT t.request_at AS day, ROUND(SUM(CASE WHEN t.status = 'cancelled_by_client' THEN 1 ELSE 0 END)::numeric / COUNT(*), 2) AS cancellation_rate
FROM trips t JOIN users c ON c.users_id = t.client_id AND c.banned = 'No' JOIN users d ON d.users_id = t.driver_id AND d.banned = 'No'
WHERE t.request_at BETWEEN DATE '2026-10-01' AND DATE '2026-10-03' GROUP BY t.request_at ORDER BY day;
""",
]
T = "id INT, client_id INT, driver_id INT, city_id INT, status VARCHAR(25), request_at DATE"
U = "users_id INT, banned VARCHAR(3), role VARCHAR(10)"
ST = ["completed", "completed", "cancelled_by_driver", "cancelled_by_client"]


def tests():
    users = [[1, "No", "client"], [2, "Yes", "client"], [3, "No", "client"], [4, "No", "client"], [10, "No", "driver"], [11, "No", "driver"], [12, "No", "driver"], [13, "No", "driver"]]
    trips = [[1, 1, 10, 1, "completed", "2026-10-01"], [2, 2, 11, 1, "cancelled_by_driver", "2026-10-01"], [3, 3, 12, 6, "completed", "2026-10-01"],
             [4, 4, 13, 6, "cancelled_by_client", "2026-10-01"], [5, 1, 10, 1, "completed", "2026-10-02"], [6, 2, 11, 6, "completed", "2026-10-02"],
             [7, 3, 12, 6, "completed", "2026-10-02"], [8, 2, 12, 12, "completed", "2026-10-03"], [9, 3, 10, 12, "completed", "2026-10-03"],
             [10, 4, 13, 12, "cancelled_by_driver", "2026-10-03"]]
    t = [tables(trips=table(T, trips), users=table(U, users)),
         tables(trips=table(T, [[1, 1, 10, 1, "cancelled_by_client", "2026-09-30"], [2, 1, 13, 1, "cancelled_by_driver", "2026-10-02"], [3, 3, 13, 1, "completed", "2026-10-02"],
                                [4, 3, 11, 1, "completed", "2026-10-02"], [5, 4, 12, 1, "completed", "2026-10-04"]]),
                users=table(U, [[1, "No", "client"], [3, "No", "client"], [4, "No", "client"], [10, "No", "driver"], [11, "No", "driver"], [12, "No", "driver"], [13, "No", "driver"]]))]
    r = rng(209)
    for _ in range(6):
        us = [[c, r.choice(["No", "No", "Yes"]), "client"] for c in range(1, 6)] + [[d, r.choice(["No", "No", "No", "Yes"]), "driver"] for d in range(10, 14)]
        tr = [[i, r.randint(1, 5), r.randint(10, 13), 1, r.choice(ST), f"2026-{r.choice(['09-30', '10-01', '10-02', '10-03', '10-03', '10-04'])}"] for i in range(1, r.randint(4, 16))]
        t.append(tables(trips=table(T, tr), users=table(U, us)))
    return t
