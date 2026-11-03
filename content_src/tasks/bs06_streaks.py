from kit import table, tables, rng, BLSQL

ID = "bs06"
NAME = "Three-Day Login Streaks"
LANG = "sql"
MINUTES = 15
TAGS = ["gaps and islands", "DISTINCT avant fenêtre", "date - ROW_NUMBER"]
SOURCE = BLSQL + " · Consecutive Active Users"
SUMMARY_FR = "Trouver les utilisateurs qui se sont connectés au moins 3 jours calendaires consécutifs, avec la longueur de leur plus longue série. Attention aux connexions en double le même jour."
HINTS = ["Enlève d'abord les doublons (SELECT DISTINCT user_id, ts::date) : sinon ROW_NUMBER compte deux fois le même jour.",
         "Dans une série de jours consécutifs, jour - ROW_NUMBER() est constant : c'est la clé du groupe (l'île)."]
DESC = """
<p>The engagement team looks for users with login streaks. You have the table <b>logins</b> with the columns <code>user_id</code> and <code>login_at</code> (timestamp). A user can log in several times the same day.</p>
<p>A <b>streak</b> is a maximal series of consecutive calendar days with at least one login each day.</p>
<p>Your task is to return the users whose longest streak is <b>at least 3 days</b>, with the columns <code>user_id</code> and <code>longest_streak</code> (in days), sorted by <code>longest_streak</code> descending, then <code>user_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH d AS (SELECT DISTINCT user_id, login_at::date AS day FROM logins),
g AS (SELECT user_id, day, day - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY day))::int AS grp FROM d),
s AS (SELECT user_id, grp, COUNT(*) AS len FROM g GROUP BY user_id, grp)
SELECT user_id, MAX(len) AS longest_streak
FROM s
GROUP BY user_id
HAVING MAX(len) >= 3
ORDER BY longest_streak DESC, user_id;
"""
ALT = ["""
WITH RECURSIVE d AS (SELECT DISTINCT user_id, login_at::date AS day FROM logins),
starts AS (SELECT a.user_id, a.day FROM d a WHERE NOT EXISTS (SELECT 1 FROM d b WHERE b.user_id = a.user_id AND b.day = a.day - 1)),
walk AS (
  SELECT user_id, day AS start_day, day, 1 AS len FROM starts
  UNION ALL
  SELECT w.user_id, w.start_day, d.day, w.len + 1 FROM walk w JOIN d ON d.user_id = w.user_id AND d.day = w.day + 1
)
SELECT user_id, MAX(len) AS longest_streak FROM walk GROUP BY user_id HAVING MAX(len) >= 3 ORDER BY longest_streak DESC, user_id;
"""]
MUTANTS = [
    """
WITH g AS (SELECT user_id, login_at::date AS day, login_at::date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_at))::int AS grp FROM logins),
s AS (SELECT user_id, grp, COUNT(*) AS len FROM g GROUP BY user_id, grp)
SELECT user_id, MAX(len) AS longest_streak FROM s GROUP BY user_id HAVING MAX(len) >= 3 ORDER BY longest_streak DESC, user_id;
""",
    """
SELECT DISTINCT a.user_id, 3 AS longest_streak FROM logins a JOIN logins b ON b.user_id = a.user_id AND b.login_at::date = a.login_at::date + 1
JOIN logins c ON c.user_id = a.user_id AND c.login_at::date = a.login_at::date + 2 ORDER BY 1;
""",
]
L = "user_id INT, login_at TIMESTAMP"


def tests():
    t = [tables(logins=table(L, [[1, "2026-02-14 09:00:00"], [1, "2026-02-13 10:00:00"], [1, "2026-02-12 08:30:00"], [1, "2026-02-11 22:00:00"],
                                 [2, "2026-02-14 09:00:00"], [2, "2026-02-12 09:00:00"], [2, "2026-02-11 09:00:00"], [2, "2026-02-10 09:00:00"],
                                 [3, "2026-02-14 09:00:00"], [3, "2026-02-12 09:00:00"],
                                 [4, "2026-02-09 09:00:00"], [4, "2026-02-08 09:00:00"], [4, "2026-02-08 18:00:00"], [4, "2026-02-07 09:00:00"]])),
         tables(logins=table(L, [[7, "2026-02-27 23:59:00"], [7, "2026-02-28 00:01:00"], [7, "2026-03-01 12:00:00"], [8, "2026-03-01 01:00:00"], [8, "2026-03-01 02:00:00"], [8, "2026-03-01 03:00:00"]]))]
    r = rng(206)
    for _ in range(6):
        rows = []
        for u in range(1, 6):
            for day in r.sample(range(1, 15), r.randint(1, 9)):
                for _ in range(r.choice([1, 1, 2])):
                    rows.append([u, f"2026-03-{day:02d} {r.randint(0, 23):02d}:{r.randint(0, 59):02d}:00"])
        r.shuffle(rows)
        t.append(tables(logins=table(L, rows)))
    return t
