from kit import rng

ID = "d10"
NAME = "Smallest Batch Size"
LANG = "python"
PARAMS = ["files", "hours"]
MINUTES = 18
TAGS = ["DSA", "recherche binaire sur la réponse", "glouton de vérification"]
IO = [("input", "array.integer files"), ("input", "integer hours"), ("output", "integer")]
SUMMARY_FR = "Fichiers à charger dans l'ordre, une capacité max par heure (sans couper un fichier) : trouver la plus petite capacité qui finit en au plus `hours` heures."
HINTS = ["La réponse est entre max(files) et sum(files) : cherche-la par dichotomie.", "Pour une capacité donnée, compte les heures en remplissant chaque heure dans l'ordre (glouton). Si ça tient, essaie plus petit."]
DESC = """
<p>A loader must load <code>files</code> (sizes in GB) <b>in this order</b>. Each hour it can load files whose total size is at most its capacity <code>C</code>; a file is never split across two hours. Your task is to return the smallest integer <code>C</code> that loads everything in at most <code>hours</code> hours.</p>
<p><code>files</code> is not empty and <code>hours &gt;= 1</code>. Hint of complexity: <code>O(n log(sum))</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(files, hours):
    # write your code here
    return 0
"""
SOLUTION = """
def solution(files, hours):
    def needed(c):
        h, cur = 1, 0
        for f in files:
            if cur + f > c:
                h += 1; cur = 0
            cur += f
        return h
    lo, hi = max(files), sum(files)
    while lo < hi:
        mid = (lo + hi) // 2
        if needed(mid) <= hours:
            hi = mid
        else:
            lo = mid + 1
    return lo
"""
ALT = ["""
def solution(files, hours):
    c = max(files)
    while True:
        h, cur = 1, 0
        for f in files:
            if cur + f > c: h += 1; cur = 0
            cur += f
        if h <= hours: return c
        c += 1
"""]
MUTANTS = ["""
def solution(files, hours):
    import math
    return max(max(files), math.ceil(sum(files) / hours))
""", """
def solution(files, hours):
    def needed(c):
        h, cur = 1, 0
        for f in files:
            if cur + f > c: h += 1; cur = 0
            cur += f
        return h
    lo, hi = 1, sum(files)
    while lo < hi:
        mid = (lo + hi) // 2
        if needed(mid) <= hours: hi = mid
        else: lo = mid + 1
    return lo
"""]


def tests():
    t = [{"files": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "hours": 5}, {"files": [3, 2, 2, 4, 1, 4], "hours": 3}, {"files": [1, 2, 3, 1, 1], "hours": 4}, {"files": [9, 1], "hours": 5}]
    r = rng(2010)
    for _ in range(8):
        f = [r.randint(1, 12) for _ in range(r.randint(1, 10))]
        t.append({"files": f, "hours": r.randint(1, len(f))})
    return t
