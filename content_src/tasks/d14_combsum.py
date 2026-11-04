from kit import rng

ID = "d14"
NAME = "Fill a Truck Exactly"
LANG = "python"
PARAMS = ["sizes", "capacity"]
MINUTES = 18
TAGS = ["DSA", "backtracking", "élagage", "réutilisation permise"]
IO = [("input", "array.integer sizes"), ("input", "integer capacity"), ("output", "array.array.integer")]
SUMMARY_FR = "Toutes les façons de remplir exactement la capacité avec des tailles de colis (chaque taille réutilisable), chaque combinaison triée croissante, la liste triée."
HINTS = ["Backtracking avec un indice de départ : on peut reprendre la même taille, jamais une taille d'avant (sinon doublons).", "Trie les tailles et arrête la boucle dès que la taille dépasse le reste (élagage)."]
DESC = """
<p>Parcels come in a few distinct <code>sizes</code> (positive integers, as many parcels of each size as you want). Your task is to return every way to fill a truck of <code>capacity</code> <b>exactly</b>. Each way is a list of sizes in non-decreasing order, and the list of ways is sorted (compare element by element). Return <code>[]</code> if there is no way.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(sizes, capacity):
    # write your code here
    return []
"""
SOLUTION = """
def solution(sizes, capacity):
    s = sorted(sizes)
    out = []

    def go(start, left, cur):
        if left == 0:
            out.append(cur[:])
            return
        for i in range(start, len(s)):
            if s[i] > left:
                break
            cur.append(s[i]); go(i, left - s[i], cur); cur.pop()

    go(0, capacity, [])
    return sorted(out)
"""
ALT = ["""
def solution(sizes, capacity):
    res = set()
    def go(left, cur):
        if left == 0: res.add(tuple(sorted(cur))); return
        for x in sizes:
            if x <= left: go(left - x, cur + [x])
    go(capacity, [])
    return sorted(list(t) for t in res)
"""]
MUTANTS = ["""
def solution(sizes, capacity):
    s = sorted(sizes); out = []
    def go(start, left, cur):
        if left == 0: out.append(cur[:]); return
        for i in range(start, len(s)):
            if s[i] > left: break
            cur.append(s[i]); go(i + 1, left - s[i], cur); cur.pop()
    go(0, capacity, [])
    return sorted(out)
""", """
def solution(sizes, capacity):
    out = []
    def go(start, left, cur):
        if left == 0: out.append(cur[:]); return
        for i in range(start, len(sizes)):
            if sizes[i] > left: break
            cur.append(sizes[i]); go(i, left - sizes[i], cur); cur.pop()
    go(0, capacity, [])
    return sorted(out)
"""]


def tests():
    t = [{"sizes": [2, 3, 6, 7], "capacity": 7}, {"sizes": [2, 3, 5], "capacity": 8}, {"sizes": [4], "capacity": 2}, {"sizes": [5, 1], "capacity": 6}]
    r = rng(2014)
    for _ in range(7):
        t.append({"sizes": r.sample(range(1, 9), r.randint(1, 4)), "capacity": r.randint(1, 12)})
    return t
