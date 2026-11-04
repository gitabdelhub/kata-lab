from kit import rng

ID = "d03"
NAME = "Merge Two Sorted Exports"
LANG = "python"
PARAMS = ["a", "b"]
MINUTES = 10
TAGS = ["DSA", "deux pointeurs", "fusion", "O(n + m)"]
IO = [("input", "array.integer a"), ("input", "array.integer b"), ("output", "array.integer")]
SUMMARY_FR = "Fusionner deux listes triées en une liste triée sans doublon, en O(n + m), sans utiliser sorted()."
HINTS = ["Un indice par liste ; avance celui dont la valeur est la plus petite.", "Avant d'ajouter une valeur, compare-la à la dernière ajoutée pour éviter les doublons."]
DESC = """
<p>Two systems export customer ids, each list already sorted in ascending order (a list can contain the same id several times). Your task is to return one sorted list with every id that appears in at least one export, <b>once</b>.</p>
<p>Do it in <code>O(n + m)</code> with two pointers, without sorting again.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(a, b):
    # write your code here
    return []
"""
SOLUTION = """
def solution(a, b):
    i = j = 0
    out = []
    while i < len(a) or j < len(b):
        if j >= len(b) or (i < len(a) and a[i] <= b[j]):
            x = a[i]; i += 1
        else:
            x = b[j]; j += 1
        if not out or out[-1] != x:
            out.append(x)
    return out
"""
ALT = ["""
def solution(a, b):
    return sorted(set(a) | set(b))
"""]
MUTANTS = ["""
def solution(a, b):
    return sorted(a + b)
""", """
def solution(a, b):
    i = j = 0; out = []
    while i < len(a) and j < len(b):
        x = a[i] if a[i] <= b[j] else b[j]
        if a[i] <= b[j]: i += 1
        else: j += 1
        if not out or out[-1] != x: out.append(x)
    return out
"""]


def tests():
    t = [{"a": [1, 3, 3, 7], "b": [2, 3, 8]}, {"a": [], "b": [4, 4]}, {"a": [1, 2], "b": []}]
    r = rng(2003)
    for _ in range(8):
        t.append({"a": sorted(r.randint(1, 15) for _ in range(r.randint(0, 8))), "b": sorted(r.randint(1, 15) for _ in range(r.randint(0, 8)))})
    return t
