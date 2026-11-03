from kit import exercism, EXERCISM

ID = "bp06"
NAME = "Spiral Shelf Numbering"
LANG = "python"
PARAMS = ["size"]
MINUTES = 15
TAGS = ["grille", "directions", "simulation"]
SOURCE = EXERCISM + " · spiral-matrix"
IO = [("input", "integer size"), ("output", "array.array.integer")]
SUMMARY_FR = "Remplir une grille size x size avec 1, 2, 3... en spirale dans le sens des aiguilles d'une montre, en partant du coin en haut à gauche."
HINTS = ["Garde une direction (droite, bas, gauche, haut) et tourne quand la case suivante sort de la grille ou est déjà remplie.",
         "size = 0 donne une liste vide."]
DESC = """
<p>A storage room has <code>size</code> rows of <code>size</code> shelves. The robot numbers the shelves <code>1, 2, 3, ...</code> along a <b>clockwise spiral</b>: it starts at the top-left shelf, goes right along the first row, then down the last column, left along the last row, up the first column, and continues inwards.</p>
<p>Your task is to return the grid of numbers as a list of rows. For <code>size = 0</code>, return an empty list.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(size):
    # write your code here
    return []
"""
SOLUTION = """
def solution(size):
    grid = [[0] * size for _ in range(size)]
    r, c, dr, dc = 0, 0, 0, 1
    for k in range(1, size * size + 1):
        grid[r][c] = k
        nr, nc = r + dr, c + dc
        if not (0 <= nr < size and 0 <= nc < size) or grid[nr][nc]:
            dr, dc = dc, -dr
            nr, nc = r + dr, c + dc
        r, c = nr, nc
    return grid
"""
ALT = ["""
def solution(size):
    g = [[0] * size for _ in range(size)]
    top, bottom, left, right, k = 0, size - 1, 0, size - 1, 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1): g[top][c] = k; k += 1
        top += 1
        for r in range(top, bottom + 1): g[r][right] = k; k += 1
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1): g[bottom][c] = k; k += 1
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1): g[r][left] = k; k += 1
            left += 1
    return g
"""]
MUTANTS = [
    """
def solution(size):
    return [[r * size + c + 1 for c in range(size)] for r in range(size)]
""",
    """
def solution(size):
    grid = [[0] * size for _ in range(size)]
    r, c, dr, dc = 0, 0, 1, 0
    for k in range(1, size * size + 1):
        grid[r][c] = k
        nr, nc = r + dr, c + dc
        if not (0 <= nr < size and 0 <= nc < size) or grid[nr][nc]:
            dr, dc = -dc, dr
            nr, nc = r + dr, c + dc
        r, c = nr, nc
    return grid
""",
]
CASES = exercism("spiral-matrix")


def tests():
    t = [{"size": 3}, {"size": 5}]
    t += [{"size": i["size"]} for i, _ in CASES]
    t += [{"size": 7}, {"size": 8}]
    return t


def expected():
    return [None, None] + [e for _, e in CASES] + [None] * 2
