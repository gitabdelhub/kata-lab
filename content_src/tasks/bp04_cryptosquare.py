from kit import exercism, rng, EXERCISM

ID = "bp04"
NAME = "Square Code"
LANG = "python"
PARAMS = ["plaintext"]
MINUTES = 15
TAGS = ["nettoyage", "grille", "lire en colonnes", "math.ceil"]
SOURCE = EXERCISM + " · crypto-square"
IO = [("input", "string plaintext"), ("output", "string")]
SUMMARY_FR = "Nettoyer le texte (minuscules, lettres et chiffres seulement), l'écrire en rectangle de c colonnes et r lignes, puis le lire colonne par colonne. Les morceaux sont séparés par des espaces."
HINTS = ["c est le plus petit entier tel que c * c >= n, et r vaut c ou c - 1 : prends r = ceil(n / c).",
         "Complète le texte nettoyé avec des espaces jusqu'à r * c caractères, puis la colonne j = text[j::c]."]
DESC = """
<p>A field team sends short messages with a classic square code. You are given the message <code>plaintext</code>.</p>
<p>First, the message is <b>normalized</b>: every character that is not a letter or a digit is removed, and letters are lower-cased. Let <code>n</code> be the length of the normalized text.</p>
<p>The normalized text is then written row by row in a rectangle of <code>r</code> rows and <code>c</code> columns, where <code>c</code> is the smallest integer such that <code>c * r &gt;= n</code> with <code>c &gt;= r</code> and <code>c - r &lt;= 1</code>. If the last row is not full, it is padded with spaces.</p>
<p>Your task is to return the coded message: the <code>c</code> columns read from top to bottom, from left to right, separated by a single space. Each column has exactly <code>r</code> characters (padding included). An empty normalized text gives <code>""</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(plaintext):
    # write your code here
    return plaintext
"""
SOLUTION = """
def solution(plaintext):
    s = "".join(ch.lower() for ch in plaintext if ch.isalnum())
    n = len(s)
    if n == 0:
        return ""
    c = 1
    while c * c < n:
        c += 1
    r = c - 1 if c * (c - 1) >= n else c
    s = s.ljust(r * c)
    return " ".join(s[j::c] for j in range(c))
"""
ALT = ["""
import math
def solution(plaintext):
    s = [ch.lower() for ch in plaintext if ch.isalnum()]
    if not s:
        return ""
    c = math.ceil(math.sqrt(len(s)))
    r = math.ceil(len(s) / c)
    grid = [s[i * c:(i + 1) * c] + [" "] * (c - len(s[i * c:(i + 1) * c])) for i in range(r)]
    return " ".join("".join(grid[i][j] for i in range(r)) for j in range(c))
"""]
MUTANTS = [
    """
def solution(plaintext):
    s = "".join(ch.lower() for ch in plaintext if ch.isalnum())
    if not s:
        return ""
    c = 1
    while c * c < len(s):
        c += 1
    return " ".join(s[j::c] for j in range(c))
""",
    """
def solution(plaintext):
    s = "".join(ch.lower() for ch in plaintext if ch.isalpha())
    if not s:
        return ""
    c = 1
    while c * c < len(s):
        c += 1
    r = c - 1 if c * (c - 1) >= len(s) else c
    s = s.ljust(r * c)
    return " ".join(s[j::c] for j in range(c))
""",
]
CASES = exercism("crypto-square")


def tests():
    t = [{"plaintext": "Meet at Gate 7, 9pm!"}, {"plaintext": "Abc-def"}]
    t += [{"plaintext": i["plaintext"]} for i, _ in CASES]
    r = rng(104)
    for _ in range(3):
        t.append({"plaintext": "".join(r.choice("ab1 ,.Z") for _ in range(r.randint(3, 30)))})
    return t


def expected():
    return [None, None] + [e for _, e in CASES] + [None] * 3
