from kit import rng

ID = "d13"
NAME = "All Column Subsets"
LANG = "python"
PARAMS = ["columns"]
MINUTES = 15
TAGS = ["DSA", "backtracking", "prendre ou ne pas prendre", "2^n"]
IO = [("input", "array.string columns"), ("output", "array.array.string")]
SUMMARY_FR = "Lister tous les sous-ensembles de colonnes (noms distincts), chacun trié, la liste triée par taille puis par ordre alphabétique. Écris le backtracking toi-même."
HINTS = ["Récursion : pour chaque colonne, deux branches (je la prends / je ne la prends pas).", "Trie les colonnes d'abord ; trie ensuite le résultat avec la clé (len(s), s). N'oublie pas le sous-ensemble vide."]
DESC = """
<p>To test which column combinations make a good unique key, you want every subset of <code>columns</code> (all names are different). Your task is to return all subsets, including the empty one. Each subset is sorted alphabetically, and the list of subsets is sorted by size, then alphabetically (compare the lists element by element).</p>
<p>Write the recursion yourself; there are <code>2<sup>n</sup></code> subsets.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(columns):
    # write your code here
    return []
"""
SOLUTION = """
def solution(columns):
    cols = sorted(columns)
    out = []

    def go(i, cur):
        if i == len(cols):
            out.append(cur[:])
            return
        cur.append(cols[i]); go(i + 1, cur); cur.pop()
        go(i + 1, cur)

    go(0, [])
    return sorted(out, key=lambda s: (len(s), s))
"""
ALT = ["""
from itertools import combinations
def solution(columns):
    cols = sorted(columns)
    return [list(c) for n in range(len(cols) + 1) for c in combinations(cols, n)]
"""]
MUTANTS = ["""
from itertools import combinations
def solution(columns):
    cols = sorted(columns)
    return [list(c) for n in range(1, len(cols) + 1) for c in combinations(cols, n)]
""", """
from itertools import combinations
def solution(columns):
    return [list(c) for n in range(len(columns) + 1) for c in combinations(columns, n)]
"""]


def tests():
    t = [{"columns": ["id", "day"]}, {"columns": []}, {"columns": ["c", "a", "b"]}]
    r = rng(2013)
    for _ in range(6):
        t.append({"columns": r.sample(["id", "day", "store", "sku", "region", "user"], r.randint(1, 5))})
    return t
