from kit import table, tables, rng, BLSQL

ID = "bs03"
NAME = "Monthly Active Users"
LANG = "sql"
MINUTES = 12
TAGS = ["filtre de dates", "GROUP BY", "dépendance fonctionnelle"]
SOURCE = BLSQL + " · Monthly Active User"
SUMMARY_FR = "Lister les utilisateurs qui se sont connectés (action logged_on) dans les 30 jours avant le 1er mars 2026, avec leur dernière connexion de cette période."
HINTS = ["La fenêtre : date >= DATE '2026-03-01' - 30 AND date < DATE '2026-03-01'. Seule l'action 'logged_on' compte.",
         "Toutes les colonnes du SELECT doivent être dans le GROUP BY ou dans un agrégat (MAX(date))."]
DESC = """
<p>The growth team reports the monthly active users. You have two tables.</p>
<p><b>users</b>: <code>user_id</code> (unique), <code>name</code> and <code>phone_num</code>.</p>
<p><b>user_history</b>: one row per action of a user, with <code>user_id</code>, <code>date</code> (date) and <code>action</code>. A login is an action equal to <code>'logged_on'</code>; other actions (for example <code>'signed_up'</code>) are not logins.</p>
<p>The report date is <code>2026-03-01</code>. A user is <b>active</b> if they logged in at least once during the 30 days before the report date: from <code>2026-01-30</code> to <code>2026-02-28</code>, both included.</p>
<p>Your task is to return the columns <code>name</code>, <code>phone_num</code> and <code>last_login</code> (the latest login date of the user in this period) for every active user, sorted by <code>last_login</code> descending, then <code>name</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
SELECT u.name, u.phone_num, MAX(h.date) AS last_login
FROM users u
JOIN user_history h ON h.user_id = u.user_id
WHERE h.action = 'logged_on'
  AND h.date >= DATE '2026-03-01' - 30
  AND h.date < DATE '2026-03-01'
GROUP BY u.user_id, u.name, u.phone_num
ORDER BY last_login DESC, u.name;
"""
ALT = ["""
SELECT name, phone_num, last_login FROM (
  SELECT u.name, u.phone_num, h.date AS last_login,
         ROW_NUMBER() OVER (PARTITION BY u.user_id ORDER BY h.date DESC) AS rn
  FROM users u JOIN user_history h USING (user_id)
  WHERE h.action = 'logged_on' AND h.date BETWEEN DATE '2026-01-30' AND DATE '2026-02-28'
) x WHERE rn = 1 ORDER BY last_login DESC, name;
"""]
MUTANTS = [
    """
SELECT u.name, u.phone_num, MAX(h.date) AS last_login FROM users u JOIN user_history h ON h.user_id = u.user_id
WHERE h.date >= DATE '2026-03-01' - 30 AND h.date < DATE '2026-03-01' GROUP BY u.user_id, u.name, u.phone_num ORDER BY last_login DESC, u.name;
""",
    """
SELECT u.name, u.phone_num, MAX(h.date) AS last_login FROM users u JOIN user_history h ON h.user_id = u.user_id
WHERE h.action = 'logged_on' AND h.date > DATE '2026-03-01' - 30 AND h.date < DATE '2026-03-01' GROUP BY u.user_id, u.name, u.phone_num ORDER BY last_login DESC, u.name;
""",
    """
SELECT u.name, u.phone_num, MAX(h.date) AS last_login FROM users u JOIN user_history h ON h.user_id = u.user_id
WHERE h.action = 'logged_on' AND h.date >= DATE '2026-03-01' - 30 GROUP BY u.user_id, u.name, u.phone_num ORDER BY last_login DESC, u.name;
""",
]
U = "user_id VARCHAR(20), name VARCHAR(30), phone_num VARCHAR(20)"
H = "user_id VARCHAR(20), date DATE, action VARCHAR(20)"


def tests():
    users = [["jkog", "Jing", "202-555-0176"], ["niceguy", "Goodman", "202-555-0174"], ["sanhoo", "Sanjay", "202-555-0100"], ["shaw123", "Shaw", "202-555-0111"]]
    t = [tables(users=table(U, users), user_history=table(H, [["shaw123", "2026-02-20", "logged_on"], ["shaw123", "2026-03-12", "signed_up"],
                ["sanhoo", "2026-02-27", "logged_on"], ["sanhoo", "2026-01-01", "logged_on"], ["niceguy", "2026-01-22", "logged_on"]])),
         tables(users=table(U, users[:3]), user_history=table(H, [["jkog", "2026-01-30", "logged_on"], ["jkog", "2026-01-29", "logged_on"],
                ["niceguy", "2026-03-01", "logged_on"], ["sanhoo", "2026-02-28", "signed_up"], ["sanhoo", "2026-02-10", "logged_on"]]))]
    r = rng(203)
    days = ["2026-01-28", "2026-01-29", "2026-01-30", "2026-02-05", "2026-02-15", "2026-02-27", "2026-02-28", "2026-03-01", "2026-03-02"]
    for _ in range(6):
        h = [[r.choice(users)[0], r.choice(days), r.choice(["logged_on", "logged_on", "signed_up", "logged_off"])] for _ in range(r.randint(2, 12))]
        t.append(tables(users=table(U, users), user_history=table(H, h)))
    return t
