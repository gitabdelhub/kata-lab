from kit import rng

ID = "g03"
NAME = "Pair Sum Queries"
LANG = "python"
PARAMS = ["a", "b", "queries"]
MINUTES = 20
TAGS = ["hashmap", "compteur", "requêtes", "mise à jour", "BCG"]
SOURCE = "Question rapportée du test BCG (fastprep.io), réécrite et testée par Kata Lab"
IO = [("input", "array.integer a"), ("input", "array.integer b"), ("input", "array.array.integer queries"), ("output", "array.integer")]
SUMMARY_FR = "Traiter des requêtes dans l'ordre : [0, i, x] remplace a[i] par x ; [1, x] compte les paires (i, j) avec a[i] + b[j] = x. Renvoyer les réponses des requêtes de type 1."
HINTS = ["Compter avec deux boucles imbriquées marche, mais c'est lent si a et b sont longs (les tests cachés en ont des longs).",
         "Garde un dict valeur -> nombre d'apparitions pour b. Pour une requête [1, x], parcours a et ajoute compte_b[x - a[i]]. Si a est plus long que b, fais l'inverse avec un dict pour a, mis à jour à chaque [0, i, x]."]
DESC = """
<p>You are given two integer arrays <code>a</code> and <code>b</code> and a list of <code>queries</code>, processed in order. There are two kinds of query:</p>
<ul><li><code>[0, i, x]</code>: assign <code>a[i] = x</code>. This query produces no output.</li>
<li><code>[1, x]</code>: count the pairs of indices <code>(i, j)</code> such that <code>a[i] + b[j] = x</code>, using the current values of <code>a</code>.</li></ul>
<p>Return an array with the answer of every query of the second kind, in the order they appear.</p>
<p>Guaranteed constraints: <code>1 &le; a.length, b.length &le; 1000</code>, <code>1 &le; queries.length &le; 1000</code>, every index <code>i</code> is valid, every value is between <code>-10<sup>6</sup></code> and <code>10<sup>6</sup></code>. A solution that compares every pair for every query is too slow.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
LIMIT = 4
STARTER = """
def solution(a, b, queries):
    # write your code here
    return []
"""
SOLUTION = """
def solution(a, b, queries):
    a = list(a)
    cb = {}
    for v in b:
        cb[v] = cb.get(v, 0) + 1
    out = []
    for q in queries:
        if q[0] == 0:
            a[q[1]] = q[2]
        else:
            x = q[1]
            out.append(sum(cb.get(x - v, 0) for v in a))
    return out
"""
ALT = ["""
def solution(a, b, queries):
    a = list(a)
    ca = {}
    for v in a:
        ca[v] = ca.get(v, 0) + 1
    out = []
    for q in queries:
        if q[0] == 0:
            ca[a[q[1]]] -= 1
            a[q[1]] = q[2]
            ca[q[2]] = ca.get(q[2], 0) + 1
        else:
            out.append(sum(ca.get(q[1] - v, 0) for v in b))
    return out
"""]
MUTANTS = [
    """
def solution(a, b, queries):
    cb = {}
    for v in b:
        cb[v] = cb.get(v, 0) + 1
    out = []
    for q in queries:
        if q[0] == 1:
            out.append(sum(cb.get(q[1] - v, 0) for v in a))
    return out
""",
    """
def solution(a, b, queries):
    a = list(a)
    sb = set(b)
    out = []
    for q in queries:
        if q[0] == 0:
            a[q[1]] = q[2]
        else:
            out.append(sum(1 for v in a if q[1] - v in sb))
    return out
""",
    """
def solution(a, b, queries):
    a = list(a)
    out = []
    for q in queries:
        if q[0] == 0:
            a[q[1]] = q[2]
        else:
            out.append(sum(1 for v in a for w in b if v + w == q[1]))
    return out
""",
]


def tests():
    t = [{"a": [3, 4], "b": [1, 2, 3], "queries": [[1, 5], [0, 0, 1], [1, 5]]},
         {"a": [1, 1, 2], "b": [1, 1], "queries": [[1, 2], [1, 3], [0, 2, 1], [1, 2], [1, 3]]},
         {"a": [-1, 0], "b": [1, -1, 1], "queries": [[1, 0], [0, 0, 1], [1, 0], [1, 2]]},
         {"a": [5], "b": [5], "queries": [[0, 0, 4], [0, 0, 6], [1, 11], [1, 10]]}]
    r = rng(1903)
    for _ in range(5):
        a = [r.randint(-4, 4) for _ in range(r.randint(1, 8))]
        b = [r.randint(-4, 4) for _ in range(r.randint(1, 8))]
        qs = []
        for _ in range(r.randint(2, 9)):
            if r.random() < 0.4:
                qs.append([0, r.randrange(len(a)), r.randint(-4, 4)])
            else:
                qs.append([1, r.randint(-6, 6)])
        t.append({"a": a, "b": b, "queries": qs})
    # gros test : la double boucle par requête est trop lente
    a = [r.randint(0, 50) for _ in range(1000)]
    b = [r.randint(0, 50) for _ in range(1000)]
    qs = [[1, r.randint(20, 80)] if r.random() < 0.7 else [0, r.randrange(1000), r.randint(0, 50)] for _ in range(1000)]
    t.append({"a": a, "b": b, "queries": qs})
    return t


def expected():
    return [[2, 1]] + [None] * 9
