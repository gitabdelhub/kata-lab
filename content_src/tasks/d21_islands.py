from kit import rng

ID = "d21"
NAME = "Count Outage Zones"
LANG = "python"
PARAMS = ["grid"]
MINUTES = 15
TAGS = ["DSA", "graphe sur grille", "BFS/DFS", "cases visitées"]
IO = [("input", "array.string grid"), ("output", "integer")]
SUMMARY_FR = "Compter les zones de '#' connectées par le haut, le bas, la gauche ou la droite (pas en diagonale)."
HINTS = ["Parcours chaque case ; sur un '#' pas encore vu, compte une zone et lance un BFS/DFS qui marque toute la zone.", "4 voisins seulement. Une pile ou une deque évite la limite de récursion de Python sur une grande grille."]
DESC = """
<p>A data center map is given as <code>grid</code>, a list of strings of the same length: <code>'#'</code> is a rack in outage, <code>'.'</code> a healthy rack. Two outage racks are in the same zone when they are neighbours up, down, left or right (not diagonally). Your task is to return the number of outage zones.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(grid):
    # write your code here
    return 0
"""
SOLUTION = """
from collections import deque


def solution(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    seen = set()
    zones = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "#" and (r, c) not in seen:
                zones += 1
                q = deque([(r, c)]); seen.add((r, c))
                while q:
                    a, b = q.popleft()
                    for x, y in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                        if 0 <= x < rows and 0 <= y < cols and grid[x][y] == "#" and (x, y) not in seen:
                            seen.add((x, y)); q.append((x, y))
    return zones
"""
ALT = ["""
def solution(grid):
    cells = {(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "#"}
    parent = {x: x for x in cells}
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for (r, c) in cells:
        for n in ((r + 1, c), (r, c + 1)):
            if n in cells: parent[find(n)] = find((r, c))
    return len({find(x) for x in cells})
"""]
MUTANTS = ["""
def solution(grid):
    cells = {(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "#"}
    seen, z = set(), 0
    for s in cells:
        if s in seen: continue
        z += 1; st = [s]; seen.add(s)
        while st:
            a, b = st.pop()
            for da in (-1, 0, 1):
                for db in (-1, 0, 1):
                    n = (a + da, b + db)
                    if n in cells and n not in seen: seen.add(n); st.append(n)
    return z
""", """
def solution(grid):
    return sum(row.count("#") for row in grid)
"""]


def tests():
    t = [{"grid": ["##..#", "#...#", "..#..", "...##"]}, {"grid": []}, {"grid": ["#.", ".#"]}, {"grid": ["...."]}]
    r = rng(2021)
    for _ in range(8):
        h, w = r.randint(1, 6), r.randint(1, 7)
        t.append({"grid": ["".join(r.choice("##..") for _ in range(w)) for _ in range(h)]})
    return t
