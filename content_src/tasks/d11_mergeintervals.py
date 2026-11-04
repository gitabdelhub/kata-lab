from kit import rng

ID = "d11"
NAME = "Merge Maintenance Windows"
LANG = "python"
PARAMS = ["windows"]
MINUTES = 12
TAGS = ["DSA", "tri", "intervalles", "fusion"]
IO = [("input", "array.array.integer windows"), ("output", "array.array.integer")]
SUMMARY_FR = "Fusionner des fenêtres [début, fin] (bornes incluses) qui se chevauchent ou se touchent (une finit à 5, l'autre commence à 5), puis les renvoyer triées."
HINTS = ["Trie par début. Garde la fenêtre en cours ; si la suivante commence <= fin en cours, étends la fin avec max.", "max, pas l'affectation : une fenêtre peut être entièrement contenue dans la précédente."]
DESC = """
<p>Teams book maintenance <code>windows</code> on a database, each <code>[start, end]</code> with <code>start &lt;= end</code> (in minutes, both included), in any order. Your task is to merge the windows that overlap or touch (one ends at the minute the next one starts) and return the merged windows sorted by start.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(windows):
    # write your code here
    return []
"""
SOLUTION = """
def solution(windows):
    out = []
    for s, e in sorted(windows):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out
"""
ALT = ["""
def solution(windows):
    if not windows: return []
    pts = set()
    for s, e in windows:
        pts.update(range(2 * s, 2 * e + 1))
    pts = sorted(pts); out = [[pts[0], pts[0]]]
    for p in pts[1:]:
        if p == out[-1][1] + 1: out[-1][1] = p
        else: out.append([p, p])
    return [[a // 2, b // 2] for a, b in out]
"""]
MUTANTS = ["""
def solution(windows):
    out = []
    for s, e in windows:
        if out and s <= out[-1][1]: out[-1][1] = max(out[-1][1], e)
        else: out.append([s, e])
    return out
""", """
def solution(windows):
    out = []
    for s, e in sorted(windows):
        if out and s <= out[-1][1]: out[-1][1] = e
        else: out.append([s, e])
    return out
""", """
def solution(windows):
    out = []
    for s, e in sorted(windows):
        if out and s < out[-1][1]: out[-1][1] = max(out[-1][1], e)
        else: out.append([s, e])
    return out
"""]


def tests():
    t = [{"windows": [[8, 10], [1, 3], [2, 6], [15, 18]]}, {"windows": [[1, 4], [4, 5]]}, {"windows": [[1, 10], [2, 3], [4, 5]]}, {"windows": []}]
    r = rng(2011)
    for _ in range(8):
        w = []
        for _ in range(r.randint(1, 8)):
            s = r.randint(0, 30); w.append([s, s + r.randint(0, 8)])
        t.append({"windows": w})
    return t
