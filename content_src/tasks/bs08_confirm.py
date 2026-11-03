from kit import table, tables, rng, BLSQL

ID = "bs08"
NAME = "Second-Day Confirmations"
LANG = "sql"
MINUTES = 15
TAGS = ["dates relatives", "LOWER pour comparer", "EXISTS / NOT EXISTS"]
SOURCE = BLSQL + " · Text Confirmation"
SUMMARY_FR = "Trouver les utilisateurs qui n'ont pas confirmé par SMS le jour de leur inscription, mais qui ont confirmé le lendemain. Les identifiants se comparent sans tenir compte des majuscules."
HINTS = ["Compare LOWER(user_id) des deux côtés, et travaille sur les dates : ts::date.",
         "Deux conditions : EXISTS une confirmation le jour d'inscription + 1, et NOT EXISTS une confirmation le jour même."]
DESC = """
<p>New users sign up with their email, then must confirm their account with a text message. You have two tables.</p>
<p><b>signups</b>: <code>user_id</code>, <code>signed_up_at</code> (timestamp) and <code>email</code>. Each user signs up once.</p>
<p><b>texts</b>: one row per text message sent to a user, with <code>user_id</code>, <code>sent_at</code> (timestamp) and <code>action</code>, which is <code>'CONFIRMED'</code> if the user confirmed with this message, or <code>NULL</code> otherwise.</p>
<p>The two systems do not store user IDs with the same case: <b>user IDs must be compared without case</b> (<code>'Ali'</code> and <code>'ali'</code> are the same user).</p>
<p>Your task is to return the users who did <b>not</b> confirm on the calendar day of their sign up, but confirmed on the <b>next</b> calendar day. Return one column <code>user_id</code>, in lower case, sorted.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
SELECT LOWER(s.user_id) AS user_id
FROM signups s
WHERE EXISTS (SELECT 1 FROM texts t WHERE LOWER(t.user_id) = LOWER(s.user_id) AND t.action = 'CONFIRMED'
              AND t.sent_at::date = s.signed_up_at::date + 1)
  AND NOT EXISTS (SELECT 1 FROM texts t WHERE LOWER(t.user_id) = LOWER(s.user_id) AND t.action = 'CONFIRMED'
              AND t.sent_at::date = s.signed_up_at::date)
ORDER BY 1;
"""
ALT = ["""
WITH c AS (
  SELECT LOWER(s.user_id) AS u, s.signed_up_at::date AS d0,
         BOOL_OR(t.sent_at::date = s.signed_up_at::date) AS same_day,
         BOOL_OR(t.sent_at::date = s.signed_up_at::date + 1) AS next_day
  FROM signups s JOIN texts t ON LOWER(t.user_id) = LOWER(s.user_id) AND t.action = 'CONFIRMED'
  GROUP BY 1, 2
)
SELECT u AS user_id FROM c WHERE next_day AND NOT same_day ORDER BY 1;
"""]
MUTANTS = [
    """
SELECT LOWER(s.user_id) AS user_id FROM signups s
WHERE EXISTS (SELECT 1 FROM texts t WHERE t.user_id = s.user_id AND t.action = 'CONFIRMED' AND t.sent_at::date = s.signed_up_at::date + 1)
  AND NOT EXISTS (SELECT 1 FROM texts t WHERE t.user_id = s.user_id AND t.action = 'CONFIRMED' AND t.sent_at::date = s.signed_up_at::date) ORDER BY 1;
""",
    """
SELECT LOWER(s.user_id) AS user_id FROM signups s
WHERE EXISTS (SELECT 1 FROM texts t WHERE LOWER(t.user_id) = LOWER(s.user_id) AND t.action = 'CONFIRMED' AND t.sent_at::date = s.signed_up_at::date + 1)
  AND NOT EXISTS (SELECT 1 FROM texts t WHERE LOWER(t.user_id) = LOWER(s.user_id) AND t.sent_at::date = s.signed_up_at::date) ORDER BY 1;
""",
    """
SELECT LOWER(s.user_id) AS user_id FROM signups s
WHERE EXISTS (SELECT 1 FROM texts t WHERE LOWER(t.user_id) = LOWER(s.user_id) AND t.action = 'CONFIRMED' AND t.sent_at <= s.signed_up_at + INTERVAL '1 day' AND t.sent_at > s.signed_up_at)
ORDER BY 1;
""",
]
SG = "user_id VARCHAR(20), signed_up_at TIMESTAMP, email VARCHAR(40)"
TX = "user_id VARCHAR(20), sent_at TIMESTAMP, action VARCHAR(10)"


def tests():
    t = [tables(signups=table(SG, [["neo", "2026-03-13 00:00:00", "neo@matrix.io"], ["Ross", "2026-03-17 12:15:00", "ross@mail.com"],
                                   ["ali", "2026-03-18 05:37:00", "ali@mail.com"], ["shaw", "2026-03-18 06:00:00", "shaw@mail.com"]]),
                texts=table(TX, [["Ross", "2026-03-17 12:15:00", "CONFIRMED"], ["Ali", "2026-03-18 05:37:00", None], ["Ali", "2026-03-19 14:00:00", "CONFIRMED"],
                                 ["shaw", "2026-03-18 06:00:00", None], ["shaw", "2026-03-19 06:00:00", None], ["shaw", "2026-03-20 08:00:00", "CONFIRMED"],
                                 ["neo", "2026-03-14 23:59:00", "CONFIRMED"]])),
         tables(signups=table(SG, [["Kofi", "2026-03-01 23:50:00", "k@mail.com"], ["ama", "2026-03-01 10:00:00", "a@mail.com"]]),
                texts=table(TX, [["kofi", "2026-03-02 00:10:00", "CONFIRMED"], ["AMA", "2026-03-01 11:00:00", "CONFIRMED"], ["ama", "2026-03-02 09:00:00", "CONFIRMED"]]))]
    r = rng(208)
    for _ in range(6):
        users = r.sample(["neo", "ross", "ali", "shaw", "kofi", "ama", "yao"], r.randint(2, 6))
        sg, tx = [], []
        for u in users:
            day = r.randint(1, 20)
            sg.append([r.choice([u, u.capitalize()]), f"2026-03-{day:02d} {r.randint(0, 23):02d}:00:00", u + "@mail.com"])
            for _ in range(r.randint(0, 3)):
                tx.append([r.choice([u, u.upper(), u.capitalize()]), f"2026-03-{day + r.choice([0, 1, 1, 2]):02d} {r.randint(0, 23):02d}:30:00", r.choice(["CONFIRMED", None])])
        t.append(tables(signups=table(SG, sg), texts=table(TX, tx)))
    return t
