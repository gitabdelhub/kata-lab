from kit import rng

ID = "d20"
NAME = "Cheapest Way to Compact Files"
LANG = "python"
PARAMS = ["sizes"]
MINUTES = 15
TAGS = ["DSA", "tas (heapq)", "glouton", "toujours les deux plus petits"]
IO = [("input", "array.integer sizes"), ("output", "integer")]
SUMMARY_FR = "Compacter des petits fichiers en un seul en fusionnant deux fichiers à la fois (coût = somme des deux tailles) : coût total minimal."
HINTS = ["À chaque étape, fusionne les DEUX plus petits fichiers du moment : un tas min.", "Le fichier fusionné retourne dans le tas : trier une seule fois au début ne suffit pas."]
DESC = """
<p>A data lake has many small files of the given <code>sizes</code> (MB). A compaction job merges <b>two</b> files at a time into one; merging two files of sizes <code>x</code> and <code>y</code> costs <code>x + y</code> and creates a file of size <code>x + y</code>. Your task is to return the minimum total cost to end with a single file (<code>0</code> if there is at most one file).</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import heapq


def solution(sizes):
    # write your code here
    return 0
"""
SOLUTION = """
import heapq


def solution(sizes):
    h = list(sizes)
    heapq.heapify(h)
    cost = 0
    while len(h) > 1:
        m = heapq.heappop(h) + heapq.heappop(h)
        cost += m
        heapq.heappush(h, m)
    return cost
"""
ALT = ["""
def solution(sizes):
    s = list(sizes); cost = 0
    while len(s) > 1:
        s.sort(); m = s[0] + s[1]; cost += m; s = s[2:] + [m]
    return cost
"""]
MUTANTS = ["""
def solution(sizes):
    s = sorted(sizes); cost = 0; cur = s[0] if s else 0
    for x in s[1:]:
        cur += x; cost += cur
    return cost
""", """
def solution(sizes):
    return sum(sizes) if len(sizes) > 1 else 0
"""]


def tests():
    t = [{"sizes": [4, 3, 2, 6]}, {"sizes": [10]}, {"sizes": []}, {"sizes": [5, 5, 5, 5]}]
    r = rng(2020)
    for _ in range(8):
        t.append({"sizes": [r.randint(1, 20) for _ in range(r.randint(2, 10))]})
    return t
