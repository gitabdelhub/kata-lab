from kit import rng

ID = "e09t4"
NAME = "Fewest Connections Route"
LANG = "python"
PARAMS = ["routes", "start", "goal"]
MINUTES = 22
TAGS = ["graphe", "BFS", "plus court chemin", "ordre alphabétique"]
IO = [("input", "array.array.string routes"), ("input", "string start"), ("input", "string goal"), ("output", "array.string")]
DESC = """
<p>A travel agent wants the itinerary with the fewest flights between two airports. You are given <code>routes</code>, a list of <b>direct</b> flights <code>[from, to]</code> (a flight only goes in this direction), and two airport codes <code>start</code> and <code>goal</code>.</p>
<p>Your task is to return the itinerary as the list of airports visited, from <code>start</code> to <code>goal</code> included, using the <b>smallest number of flights</b>. If several itineraries have this smallest number of flights, return the one that comes first when the lists are compared airport by airport in alphabetical order. If <code>goal</code> cannot be reached, return an empty list. If <code>start</code> is equal to <code>goal</code>, return <code>[start]</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>Both <code>LFW → ABJ → CMN</code> and <code>LFW → DSS → CMN</code> use 2 flights: <code>ABJ</code> comes before <code>DSS</code>.</p>
"""
STARTER = """
def solution(routes, start, goal):
    # write your code here
    return []
"""
SOLUTION = """
from collections import deque


def solution(routes, start, goal):
    if start == goal:
        return [start]
    adj = {}
    for a, b in routes:
        adj.setdefault(a, set()).add(b)
    # distance de chaque aéroport jusqu'au but (BFS sur le graphe inversé)
    rev = {}
    for a, b in routes:
        rev.setdefault(b, set()).add(a)
    dist = {goal: 0}
    q = deque([goal])
    while q:
        x = q.popleft()
        for p in rev.get(x, ()):
            if p not in dist:
                dist[p] = dist[x] + 1
                q.append(p)
    if start not in dist:
        return []
    path = [start]
    while path[-1] != goal:
        cur = path[-1]
        path.append(min(n for n in adj[cur] if dist.get(n) == dist[cur] - 1))
    return path
"""
MUTANTS = [
    """
from collections import deque
def solution(routes, start, goal):
    adj = {}
    for a, b in routes:
        adj.setdefault(a, []).append(b)
    q, seen = deque([[start]]), {start}
    while q:
        p = q.popleft()
        if p[-1] == goal: return p
        for n in adj.get(p[-1], []):
            if n not in seen:
                seen.add(n); q.append(p + [n])
    return []
""",
    """
def solution(routes, start, goal):
    adj = {}
    for a, b in routes:
        adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    from collections import deque
    q, seen = deque([[start]]), {start}
    while q:
        p = q.popleft()
        if p[-1] == goal: return p
        for n in sorted(adj.get(p[-1], [])):
            if n not in seen:
                seen.add(n); q.append(p + [n])
    return []
""",
    """
def solution(routes, start, goal):
    adj = {}
    for a, b in routes:
        adj.setdefault(a, set()).add(b)
    best = []
    def dfs(p):
        nonlocal best
        if best:
            return
        if p[-1] == goal:
            best = p[:]
            return
        for n in sorted(adj.get(p[-1], [])):
            if n not in p: dfs(p + [n])
    dfs([start])
    return best
""",
]


def tests():
    t = [{"routes": [["LFW", "DSS"], ["LFW", "ABJ"], ["DSS", "CMN"], ["ABJ", "CMN"], ["LFW", "ACC"], ["ACC", "ABJ"]], "start": "LFW", "goal": "CMN"},
         {"routes": [["A", "B"], ["B", "C"]], "start": "C", "goal": "A"},
         {"routes": [["A", "B"]], "start": "A", "goal": "A"},
         {"routes": [["S", "Z"], ["S", "Y"], ["Z", "A"], ["Y", "B"], ["A", "G"], ["B", "G"], ["S", "X"], ["X", "Q"], ["Q", "R"], ["R", "G"]], "start": "S", "goal": "G"},
         {"routes": [["S", "B"], ["S", "A"], ["A", "M"], ["B", "C"], ["M", "N"], ["C", "G"], ["N", "G"]], "start": "S", "goal": "G"}]
    r = rng(904)
    aps = ["ABJ", "ACC", "CMN", "DSS", "LFW", "LOS", "NBO", "ADD"]
    for _ in range(7):
        routes = []
        for _ in range(r.randint(3, 16)):
            a, b = r.sample(aps, 2)
            routes.append([a, b])
        s, g = r.sample(aps, 2)
        t.append({"routes": routes, "start": s, "goal": g})
    return t
