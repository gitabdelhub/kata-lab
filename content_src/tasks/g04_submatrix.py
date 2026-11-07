from kit import rng

ID = "g04"
NAME = "Pattern in a Digit Grid"
LANG = "python"
PARAMS = ["board", "pattern"]
MINUTES = 25
TAGS = ["grille", "sous-matrice", "dict de correspondance", "bijection", "BCG"]
SOURCE = "Question rapportée du test BCG (fastprep.io), réécrite et testée par Kata Lab"
IO = [("input", "array.array.integer board"), ("input", "array.string pattern"), ("output", "array.integer")]
SUMMARY_FR = "Chercher dans une grille de chiffres un carré qui correspond à un motif : un chiffre doit être égal, une même lettre = un même chiffre, deux lettres différentes = deux chiffres différents. Renvoyer [ligne, colonne] du coin haut gauche, ou [-1, -1]."
HINTS = ["Essaie chaque coin (r, c) possible, ligne par ligne puis colonne par colonne : le premier qui marche est la réponse.",
         "Pour un coin, garde deux dict : lettre -> chiffre et chiffre -> lettre. Si une lettre a déjà un autre chiffre, ou si le chiffre appartient déjà à une autre lettre, ce coin ne marche pas."]
DESC = """
<p>You are given a rectangular <code>board</code> of digits (each cell is an integer from <code>0</code> to <code>9</code>) and a square <code>pattern</code> of side <code>n</code>: an array of <code>n</code> strings of length <code>n</code>. Each character of the pattern is either a digit or a lowercase English letter.</p>
<p>An <code>n &times; n</code> submatrix of the board with top-left corner <code>(r, c)</code> <b>matches</b> the pattern when, for every position:</p>
<ul><li>a digit in the pattern is equal to the board cell at the same position;</li>
<li>every occurrence of the same letter corresponds to the same board digit;</li>
<li>two different letters correspond to two different board digits.</li></ul>
<p>A letter may correspond to a digit that also appears literally in the pattern; only two distinct letters cannot share a digit.</p>
<p>Return <code>[r, c]</code> for a matching submatrix. If several match, return the one with the smallest <code>r</code>, then the smallest <code>c</code>. If none matches (including when the pattern is bigger than the board), return <code>[-1, -1]</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(board, pattern):
    # write your code here
    return []
"""
SOLUTION = """
def solution(board, pattern):
    n = len(pattern)
    rows, cols = len(board), len(board[0])
    for r in range(rows - n + 1):
        for c in range(cols - n + 1):
            to_digit, to_letter, ok = {}, {}, True
            for i in range(n):
                for j in range(n):
                    p, d = pattern[i][j], board[r + i][c + j]
                    if p.isdigit():
                        ok = int(p) == d
                    elif p in to_digit:
                        ok = to_digit[p] == d
                    elif d in to_letter:
                        ok = False
                    else:
                        to_digit[p], to_letter[d] = d, p
                    if not ok:
                        break
                if not ok:
                    break
            if ok:
                return [r, c]
    return [-1, -1]
"""
ALT = ["""
def solution(board, pattern):
    n = len(pattern)
    R, C = len(board), len(board[0])
    for r in range(R - n + 1):
        for c in range(C - n + 1):
            cells = [(pattern[i][j], board[r + i][c + j]) for i in range(n) for j in range(n)]
            if any(p.isdigit() and int(p) != d for p, d in cells):
                continue
            pairs = {(p, d) for p, d in cells if not p.isdigit()}
            letters = {p for p, _ in pairs}
            digits = {d for _, d in pairs}
            if len(pairs) == len(letters) == len(digits):
                return [r, c]
    return [-1, -1]
"""]
MUTANTS = [
    """
def solution(board, pattern):
    n = len(pattern)
    for r in range(len(board) - n + 1):
        for c in range(len(board[0]) - n + 1):
            m, ok = {}, True
            for i in range(n):
                for j in range(n):
                    p, d = pattern[i][j], board[r + i][c + j]
                    if p.isdigit():
                        ok = ok and int(p) == d
                    elif p in m:
                        ok = ok and m[p] == d
                    else:
                        m[p] = d
            if ok:
                return [r, c]
    return [-1, -1]
""",
    """
def solution(board, pattern):
    n = len(pattern)
    for c in range(len(board[0]) - n + 1):
        for r in range(len(board) - n + 1):
            td, tl, ok = {}, {}, True
            for i in range(n):
                for j in range(n):
                    p, d = pattern[i][j], board[r + i][c + j]
                    if p.isdigit():
                        ok = ok and int(p) == d
                    elif p in td:
                        ok = ok and td[p] == d
                    elif d in tl:
                        ok = False
                    else:
                        td[p], tl[d] = d, p
            if ok:
                return [r, c]
    return [-1, -1]
""",
    """
def solution(board, pattern):
    n = len(pattern)
    lit = {int(ch) for row in pattern for ch in row if ch.isdigit()}
    for r in range(len(board) - n + 1):
        for c in range(len(board[0]) - n + 1):
            td, tl, ok = {}, {}, True
            for i in range(n):
                for j in range(n):
                    p, d = pattern[i][j], board[r + i][c + j]
                    if p.isdigit():
                        ok = ok and int(p) == d
                    elif d in lit:
                        ok = False
                    elif p in td:
                        ok = ok and td[p] == d
                    elif d in tl:
                        ok = False
                    else:
                        td[p], tl[d] = d, p
            if ok:
                return [r, c]
    return [-1, -1]
""",
    """
def solution(board, pattern):
    n = len(pattern)
    for r in range(len(board) - n):
        for c in range(len(board[0]) - n):
            td, tl, ok = {}, {}, True
            for i in range(n):
                for j in range(n):
                    p, d = pattern[i][j], board[r + i][c + j]
                    if p.isdigit():
                        ok = ok and int(p) == d
                    elif p in td:
                        ok = ok and td[p] == d
                    elif d in tl:
                        ok = False
                    else:
                        td[p], tl[d] = d, p
            if ok:
                return [r, c]
    return [-1, -1]
""",
]


def tests():
    t = [{"board": [[1, 2, 1], [2, 1, 2]], "pattern": ["ab", "ba"]},
         {"board": [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 5, 1]], "pattern": ["a6", "9a"]},
         {"board": [[1, 1], [1, 1]], "pattern": ["ab", "ba"]},
         {"board": [[3, 3], [3, 3]], "pattern": ["aa", "a3"]},
         {"board": [[1, 2], [3, 4]], "pattern": ["abc", "abc", "abc"]},
         {"board": [[7, 7, 1], [2, 7, 7], [5, 2, 7]], "pattern": ["a7", "ba"]},
         {"board": [[4, 4, 9], [4, 4, 9], [9, 9, 9]], "pattern": ["aab", "aab", "bbb"]},
         {"board": [[5, 5, 2], [5, 6, 2], [1, 2, 2]], "pattern": ["5"]},
         {"board": [[0, 0, 7, 8], [7, 8, 0, 0], [0, 0, 0, 0]], "pattern": ["ab", "00"]}]
    r = rng(1904)
    for _ in range(6):
        R, C = r.randint(2, 6), r.randint(2, 6)
        board = [[r.choice([1, 2, 3]) for _ in range(C)] for _ in range(R)]
        n = r.randint(1, min(R, C))
        pattern = ["".join(r.choice("ab1") for _ in range(n)) for _ in range(n)]
        t.append({"board": board, "pattern": pattern})
    return t


def expected():
    return [[0, 0], [1, 1], [-1, -1]] + [None] * 12
