from kit import exercism, rng, EXERCISM

ID = "bp05"
NAME = "Sensor Grid Counts"
LANG = "python"
PARAMS = ["garden"]
MINUTES = 15
TAGS = ["grille", "8 voisins", "bornes"]
SOURCE = EXERCISM + " · flower-field"
IO = [("input", "array.string garden"), ("output", "array.string")]
SUMMARY_FR = "Dans une grille, chaque case vide reçoit le nombre de * parmi ses 8 voisines (rien si 0). Les * restent des *."
HINTS = ["Pour chaque case, parcours dr et dc dans (-1, 0, 1) en sautant (0, 0), et vérifie que la voisine est dans la grille.",
         "Attention aux lignes vides : la grille peut avoir des lignes mais 0 colonne."]
DESC = """
<p>A greenhouse is mapped as a rectangular grid <code>garden</code>. Each string is one row: <code>'*'</code> is a plant with a sensor alert, and <code>' '</code> is an empty cell.</p>
<p>Your task is to return the same grid where every empty cell is replaced by the number of alert cells among its <b>8 neighbours</b> (horizontal, vertical and diagonal). If an empty cell has no alert neighbour, it stays <code>' '</code>. Alert cells stay <code>'*'</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(garden):
    # write your code here
    return garden
"""
SOLUTION = """
def solution(garden):
    rows = len(garden)
    out = []
    for r in range(rows):
        line = ""
        for c in range(len(garden[r])):
            if garden[r][c] == "*":
                line += "*"
                continue
            n = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    rr, cc = r + dr, c + dc
                    if (dr or dc) and 0 <= rr < rows and 0 <= cc < len(garden[rr]) and garden[rr][cc] == "*":
                        n += 1
            line += str(n) if n else " "
        out.append(line)
    return out
"""
ALT = ["""
def solution(garden):
    stars = {(r, c) for r, row in enumerate(garden) for c, ch in enumerate(row) if ch == "*"}
    res = []
    for r, row in enumerate(garden):
        cells = []
        for c, ch in enumerate(row):
            if ch == "*":
                cells.append("*")
            else:
                k = sum((r + a, c + b) in stars for a in (-1, 0, 1) for b in (-1, 0, 1))
                cells.append(str(k) if k else " ")
        res.append("".join(cells))
    return res
"""]
MUTANTS = [
    """
def solution(garden):
    out = []
    for r in range(len(garden)):
        line = ""
        for c in range(len(garden[r])):
            if garden[r][c] == "*":
                line += "*"; continue
            n = sum(1 for rr, cc in ((r-1, c), (r+1, c), (r, c-1), (r, c+1)) if 0 <= rr < len(garden) and 0 <= cc < len(garden[rr]) and garden[rr][cc] == "*")
            line += str(n) if n else " "
        out.append(line)
    return out
""",
    """
def solution(garden):
    out = []
    for r in range(len(garden)):
        line = ""
        for c in range(len(garden[r])):
            if garden[r][c] == "*":
                line += "*"; continue
            n = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    rr, cc = r + dr, c + dc
                    if (dr or dc) and 0 <= rr < len(garden) and 0 <= cc < len(garden[rr]) and garden[rr][cc] == "*":
                        n += 1
            line += str(n)
        out.append(line)
    return out
""",
]
CASES = exercism("flower-field")


def tests():
    t = [{"garden": [" * ", "   ", "** "]}, {"garden": ["*  *"]}]
    t += [{"garden": i["garden"]} for i, _ in CASES]
    r = rng(105)
    for _ in range(3):
        w = r.randint(1, 6)
        t.append({"garden": ["".join(r.choice("*  ") for _ in range(w)) for _ in range(r.randint(1, 5))]})
    return t


def expected():
    return [None, None] + [e for _, e in CASES] + [None] * 3
