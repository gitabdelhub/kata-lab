from kit import exercism, rng, EXERCISM

ID = "bp07"
NAME = "League Standings Report"
LANG = "python"
PARAMS = ["rows"]
MINUTES = 20
TAGS = ["dict d'agrégats", "tri multi-clés", "formatage f-string"]
SOURCE = EXERCISM + " · tournament"
IO = [("input", "array.string rows"), ("output", "array.string")]
SUMMARY_FR = "Lire des résultats de matchs 'A;B;win|loss|draw', calculer par équipe MP, W, D, L, P (3 points la victoire, 1 le nul), trier par points décroissants puis par nom, et formater un tableau aligné."
HINTS = ["Un dict équipe -> [MP, W, D, L] ; un résultat 'loss' pour A est une victoire pour B.",
         "Tri : key=lambda x: (-points, nom). Format : f\"{nom:<31}| {mp:>2} | {w:>2} | {d:>2} | {l:>2} | {p:>2}\" (et l'en-tête 'Team' sur 31 caractères)."]
DESC = """
<p>A company football league stores its results as lines of text. You are given the list <code>rows</code>; each row has the form <code>"&lt;team A&gt;;&lt;team B&gt;;&lt;result&gt;"</code>, where the result is <code>win</code>, <code>loss</code> or <code>draw</code> <b>from the point of view of team A</b>.</p>
<p>A win gives 3 points, a draw 1 point and a loss 0 point. For every team, compute <code>MP</code> (matches played), <code>W</code>, <code>D</code>, <code>L</code> and <code>P</code> (points).</p>
<p>Your task is to return the standings as a list of lines. The first line is the header <code>"Team                           | MP |  W |  D |  L |  P"</code>. Then one line per team, sorted by points (highest first), then by team name in alphabetical order. The team name is padded with spaces to <code>31</code> characters, and every number is right-aligned on <code>2</code> characters, with the separators exactly as in the header.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(rows):
    # write your code here
    return ["Team                           | MP |  W |  D |  L |  P"]
"""
SOLUTION = """
def solution(rows):
    stats = {}
    def add(team, w, d, l):
        s = stats.setdefault(team, [0, 0, 0, 0])
        s[0] += 1; s[1] += w; s[2] += d; s[3] += l
    for row in rows:
        a, b, res = row.split(";")
        if res == "win":
            add(a, 1, 0, 0); add(b, 0, 0, 1)
        elif res == "loss":
            add(a, 0, 0, 1); add(b, 1, 0, 0)
        else:
            add(a, 0, 1, 0); add(b, 0, 1, 0)
    fmt = "{:<31}| {:>2} | {:>2} | {:>2} | {:>2} | {:>2}"
    out = [fmt.format("Team", "MP", "W", "D", "L", "P")]
    order = sorted(stats.items(), key=lambda kv: (-(3 * kv[1][1] + kv[1][2]), kv[0]))
    for team, (mp, w, d, l) in order:
        out.append(fmt.format(team, mp, w, d, l, 3 * w + d))
    return out
"""
ALT = ["""
from collections import Counter
def solution(rows):
    mp, w, d, l = Counter(), Counter(), Counter(), Counter()
    for row in rows:
        a, b, res = row.split(";")
        mp[a] += 1; mp[b] += 1
        if res == "draw": d[a] += 1; d[b] += 1
        else:
            win, lose = (a, b) if res == "win" else (b, a)
            w[win] += 1; l[lose] += 1
    lines = ["Team".ljust(31) + "| MP |  W |  D |  L |  P"]
    for t in sorted(mp, key=lambda t: (-(3 * w[t] + d[t]), t)):
        lines.append(t.ljust(31) + "| " + " | ".join(str(x).rjust(2) for x in (mp[t], w[t], d[t], l[t], 3 * w[t] + d[t])))
    return lines
"""]
MUTANTS = [
    """
def solution(rows):
    stats = {}
    for row in rows:
        a, b, res = row.split(";")
        for team in (a, b):
            stats.setdefault(team, [0, 0, 0, 0])[0] += 1
        if res == "win": stats[a][1] += 1; stats[b][3] += 1
        elif res == "loss": stats[a][3] += 1; stats[b][1] += 1
        else: stats[a][2] += 1; stats[b][2] += 1
    fmt = "{:<31}| {:>2} | {:>2} | {:>2} | {:>2} | {:>2}"
    out = [fmt.format("Team", "MP", "W", "D", "L", "P")]
    for team, (mp, w, d, l) in sorted(stats.items(), key=lambda kv: -(3 * kv[1][1] + kv[1][2])):
        out.append(fmt.format(team, mp, w, d, l, 3 * w + d))
    return out
""",
    """
def solution(rows):
    stats = {}
    for row in rows:
        a, b, res = row.split(";")
        for team in (a, b):
            stats.setdefault(team, [0, 0, 0, 0])[0] += 1
        if res in ("win", "loss"): stats[a][1] += 1; stats[b][3] += 1
        else: stats[a][2] += 1; stats[b][2] += 1
    fmt = "{:<31}| {:>2} | {:>2} | {:>2} | {:>2} | {:>2}"
    out = [fmt.format("Team", "MP", "W", "D", "L", "P")]
    for team, (mp, w, d, l) in sorted(stats.items(), key=lambda kv: (-(3 * kv[1][1] + kv[1][2]), kv[0])):
        out.append(fmt.format(team, mp, w, d, l, 3 * w + d))
    return out
""",
]
CASES = exercism("tournament")


def tests():
    t = [{"rows": ["Data FC;Ops United;win", "Ops United;Finance;draw", "Finance;Data FC;loss"]},
         {"rows": ["Alpha;Beta;loss", "Beta;Gamma;draw", "Gamma;Alpha;win"]}]
    t += [{"rows": i["rows"]} for i, _ in CASES]
    r = rng(107)
    teams = ["Data FC", "Ops United", "Finance", "Legal Stars", "HR Rovers"]
    for _ in range(3):
        rows = []
        for _ in range(r.randint(2, 9)):
            a, b = r.sample(teams, 2)
            rows.append(f"{a};{b};{r.choice(['win', 'loss', 'draw'])}")
        t.append({"rows": rows})
    return t


def expected():
    return [None, None] + [e for _, e in CASES] + [None] * 3
