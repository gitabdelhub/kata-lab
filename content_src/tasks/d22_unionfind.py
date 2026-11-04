from kit import rng

ID = "d22"
NAME = "Count Replication Clusters"
LANG = "python"
PARAMS = ["n", "links"]
MINUTES = 15
TAGS = ["DSA", "union-find", "composantes connexes", "compression de chemin"]
IO = [("input", "integer n"), ("input", "array.array.integer links"), ("output", "array.integer")]
SUMMARY_FR = "n serveurs (0 à n-1) et des liens de réplication (non orientés) ajoutés un par un : après chaque lien, le nombre de clusters. Avec union-find."
HINTS = ["parent[i] = i au départ ; find avec compression de chemin ; union fusionne les deux racines.", "Le nombre de clusters baisse de 1 seulement si les deux serveurs avaient des racines différentes."]
DESC = """
<p>There are <code>n</code> database servers numbered <code>0</code> to <code>n - 1</code>. Replication <code>links</code> <code>[a, b]</code> are added one by one (a link works in both directions). A <b>cluster</b> is a group of servers connected directly or through other servers.</p>
<p>Your task is to return a list with the number of clusters after each link is added. Use union-find (disjoint sets) so each step is almost <code>O(1)</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(n, links):
    # write your code here
    return []
"""
SOLUTION = """
def solution(n, links):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    count, out = n, []
    for a, b in links:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            count -= 1
        out.append(count)
    return out
"""
ALT = ["""
def solution(n, links):
    out, adj = [], {i: set() for i in range(n)}
    for a, b in links:
        adj[a].add(b); adj[b].add(a)
        seen, c = set(), 0
        for s in range(n):
            if s in seen: continue
            c += 1; st = [s]; seen.add(s)
            while st:
                x = st.pop()
                for y in adj[x]:
                    if y not in seen: seen.add(y); st.append(y)
        out.append(c)
    return out
"""]
MUTANTS = ["""
def solution(n, links):
    return [n - i - 1 for i in range(len(links))]
""", """
def solution(n, links):
    parent = list(range(n)); count, out = n, []
    for a, b in links:
        if parent[a] != parent[b]:
            parent[a] = parent[b]; count -= 1
        out.append(count)
    return out
"""]


def tests():
    t = [{"n": 5, "links": [[0, 1], [1, 2], [3, 4], [0, 2]]}, {"n": 3, "links": []}, {"n": 4, "links": [[0, 1], [2, 3], [1, 2], [0, 3]]}]
    r = rng(2022)
    for _ in range(8):
        n = r.randint(2, 9)
        t.append({"n": n, "links": [[r.randrange(n), r.randrange(n)] for _ in range(r.randint(1, 10))]})
    return t
