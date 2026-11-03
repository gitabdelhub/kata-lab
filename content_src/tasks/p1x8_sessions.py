from kit import rng

ID = "p1x8"
NAME = "Sessionize click events"
LANG = "python"
PARAMS = ["events", "gap"]
MINUTES = 20
TAGS = ["tri", "dict", "boucle", "sessions"]
SUMMARY_FR = "Des clics [user, ts] dans le désordre. Pour chaque utilisateur, une nouvelle session commence quand il s'est passé PLUS de gap secondes depuis le clic précédent. Renvoie [user, début, fin, nombre de clics] trié par user puis début."
IO = [("input", "array.array.string events"), ("input", "integer gap"), ("output", "array.array")]
DESC = """
<p>A website logs every click as a pair <code>[user, ts]</code>, where <code>user</code> is a string and <code>ts</code> a timestamp in seconds (integer). The list <code>events</code> is <b>not sorted</b>, and a user can click twice in the same second.</p>
<p>A <b>session</b> of a user is a group of consecutive clicks (in time order) where the time between two consecutive clicks is at most <code>gap</code> seconds. A click that comes strictly more than <code>gap</code> seconds after the previous click of the same user starts a new session.</p>
<p>Return every session as <code>[user, start, end, clicks]</code>, where <code>start</code> and <code>end</code> are the first and last timestamps of the session and <code>clicks</code> the number of clicks. Sort the result by <code>user</code>, then <code>start</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>For <code>"ana"</code>, the click at <code>2000</code> comes <code>1900</code> seconds after the click at <code>100</code>, which is more than <code>1800</code>: a new session starts.</p>
"""
STARTER = """
def solution(events, gap):
    # write your code here
    return []
"""
SOLUTION = """
def solution(events, gap):
    by_user = {}
    for user, ts in events:
        by_user.setdefault(user, []).append(ts)
    out = []
    for user in sorted(by_user):
        times = sorted(by_user[user])
        start = prev = times[0]
        n = 1
        for ts in times[1:]:
            if ts - prev > gap:
                out.append([user, start, prev, n])
                start, n = ts, 0
            n += 1
            prev = ts
        out.append([user, start, prev, n])
    return out
"""
MUTANTS = [
    """
def solution(events, gap):
    by_user = {}
    for user, ts in events:
        by_user.setdefault(user, []).append(ts)
    out = []
    for user in sorted(by_user):
        times = sorted(by_user[user])
        start = prev = times[0]; n = 1
        for ts in times[1:]:
            if ts - prev >= gap:
                out.append([user, start, prev, n]); start, n = ts, 0
            n += 1; prev = ts
        out.append([user, start, prev, n])
    return out
""",
    """
def solution(events, gap):
    by_user = {}
    for user, ts in events:
        by_user.setdefault(user, []).append(ts)
    out = []
    for user in sorted(by_user):
        times = by_user[user]
        start = prev = times[0]; n = 1
        for ts in times[1:]:
            if ts - prev > gap:
                out.append([user, start, prev, n]); start, n = ts, 0
            n += 1; prev = ts
        out.append([user, start, prev, n])
    return out
""",
]
HINTS = ["ENTRÉE : clics en désordre. CLÉ : l'utilisateur. Regroupe les ts par user dans un dict, puis trie chaque liste.",
         "Parcours les ts triés en gardant start, prev et n. Quand ts - prev > gap, ferme la session en cours et ouvre-en une nouvelle.",
         "N'oublie pas d'ajouter la dernière session après la boucle."]


def tests():
    t = [{"events": [["ana", 100], ["bob", 50], ["ana", 2000], ["ana", 60], ["bob", 1850]], "gap": 1800},
         {"events": [["u", 0], ["u", 0], ["u", 10]], "gap": 10}]
    r = rng(15)
    for k in range(7):
        ev = []
        for u in ["ana", "bob", "chen", "dia"][: 1 + k % 4]:
            ts = r.randint(0, 500)
            for _ in range(r.randint(1, 8)):
                ts += r.choice([0, 5, 30, 100, 1799, 1800, 1801, 4000])
                ev.append([u, ts])
        r.shuffle(ev)
        t.append({"events": ev, "gap": r.choice([1800, 100, 30])})
    return t
