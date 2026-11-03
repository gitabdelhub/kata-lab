from kit import table, tables, rng, BLSQL

ID = "bs02"
NAME = "Lifetime Listening Counts"
LANG = "sql"
MINUTES = 15
TAGS = ["agrégat puis jointure", "FULL JOIN", "COALESCE", "filtre sur le dernier jour"]
SOURCE = BLSQL + " · Listening History"
SUMMARY_FR = "Ajouter aux compteurs cumulés (history) les écoutes du dernier jour présent dans plays, y compris les nouvelles paires utilisateur-chanson."
HINTS = ["Agrège d'abord plays du dernier jour (GROUP BY user_id, song_id), PUIS joins à history : sinon tu multiplies les lignes.",
         "FULL OUTER JOIN + COALESCE(h.tally, 0) + COALESCE(p.n, 0) pour garder les anciennes et les nouvelles paires."]
DESC = """
<p>A music app keeps lifetime listening counts. You have two tables.</p>
<p><b>history</b> contains, for each user and song, the number of times the user has listened to the song so far (one row per pair):</p>
<ul><li><code>user_id</code>, <code>song_id</code> - the pair;</li><li><code>tally</code> - the lifetime count (integer).</li></ul>
<p><b>plays</b> is an event log with one row each time a user listens to a song:</p>
<ul><li><code>user_id</code>, <code>song_id</code> - the pair;</li><li><code>played_at</code> - the timestamp of the play.</li></ul>
<p><code>history</code> is up to date until the end of the day <b>before</b> the latest day of <code>plays</code>. Only the plays whose date is the latest date present in <code>plays</code> must be added; older plays are already counted.</p>
<p>Your task is to return the updated lifetime counts with the columns <code>user_id</code>, <code>song_id</code> and <code>tally</code>, for every pair of <code>history</code> and every new pair of the latest day, sorted by <code>user_id</code>, then <code>song_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
SELECT user_id, song_id, tally FROM history;
"""
SOLUTION = """
WITH today AS (
  SELECT user_id, song_id, COUNT(*) AS n
  FROM plays
  WHERE played_at::date = (SELECT MAX(played_at)::date FROM plays)
  GROUP BY user_id, song_id
)
SELECT COALESCE(h.user_id, t.user_id) AS user_id,
       COALESCE(h.song_id, t.song_id) AS song_id,
       COALESCE(h.tally, 0) + COALESCE(t.n, 0) AS tally
FROM history h
FULL OUTER JOIN today t ON t.user_id = h.user_id AND t.song_id = h.song_id
ORDER BY user_id, song_id;
"""
ALT = ["""
SELECT user_id, song_id, SUM(c)::bigint AS tally FROM (
  SELECT user_id, song_id, tally AS c FROM history
  UNION ALL
  SELECT user_id, song_id, 1 FROM plays
  WHERE DATE(played_at) = (SELECT DATE(MAX(played_at)) FROM plays)
) x GROUP BY user_id, song_id ORDER BY user_id, song_id;
"""]
MUTANTS = [
    """
WITH today AS (SELECT user_id, song_id, COUNT(*) AS n FROM plays GROUP BY user_id, song_id)
SELECT COALESCE(h.user_id, t.user_id) AS user_id, COALESCE(h.song_id, t.song_id) AS song_id, COALESCE(h.tally, 0) + COALESCE(t.n, 0) AS tally
FROM history h FULL OUTER JOIN today t ON t.user_id = h.user_id AND t.song_id = h.song_id ORDER BY user_id, song_id;
""",
    """
WITH today AS (SELECT user_id, song_id, COUNT(*) AS n FROM plays WHERE played_at::date = (SELECT MAX(played_at)::date FROM plays) GROUP BY user_id, song_id)
SELECT h.user_id, h.song_id, h.tally + COALESCE(t.n, 0) AS tally
FROM history h LEFT JOIN today t ON t.user_id = h.user_id AND t.song_id = h.song_id ORDER BY user_id, song_id;
""",
    """
SELECT h.user_id, h.song_id, h.tally + COUNT(p.user_id) AS tally
FROM history h LEFT JOIN plays p ON p.user_id = h.user_id AND p.song_id = h.song_id
GROUP BY h.user_id, h.song_id, h.tally ORDER BY user_id, song_id;
""",
]
H = "user_id VARCHAR(20), song_id VARCHAR(20), tally INT"
P = "user_id VARCHAR(20), song_id VARCHAR(20), played_at TIMESTAMP"


def tests():
    t = [tables(history=table(H, [["shaw", "rise", 2], ["linda", "lemon", 4]]),
                plays=table(P, [["shaw", "rise", "2026-03-01 05:33:08"], ["shaw", "rise", "2026-03-01 16:00:00"], ["shaw", "goodie", "2026-03-01 10:15:00"],
                                ["linda", "lemon", "2026-02-28 00:00:00"], ["mark", "game", "2026-03-01 04:00:00"]])),
         tables(history=table(H, [["a", "s1", 10], ["b", "s2", 1]]),
                plays=table(P, [["a", "s1", "2026-03-04 23:59:59"], ["a", "s1", "2026-03-05 00:00:00"], ["b", "s3", "2026-03-05 08:00:00"]]))]
    r = rng(202)
    for _ in range(6):
        users, songs = ["ana", "bo", "cy", "di"], ["s1", "s2", "s3"]
        pairs = r.sample([(u, s) for u in users for s in songs], r.randint(1, 6))
        hist = [[u, s, r.randint(1, 30)] for u, s in pairs]
        pl = [[r.choice(users), r.choice(songs), f"2026-03-{r.choice([3, 4, 4, 5]):02d} {r.randint(0, 23):02d}:{r.randint(0, 59):02d}:00"] for _ in range(r.randint(1, 12))]
        t.append(tables(history=table(H, hist), plays=table(P, pl)))
    return t
