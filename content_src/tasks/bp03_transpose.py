from kit import exercism, rng, EXERCISM

ID = "bp03"
NAME = "Transpose Text Columns"
LANG = "python"
PARAMS = ["lines"]
MINUTES = 15
TAGS = ["grille", "lignes de longueurs différentes", "colonnes verticales"]
SOURCE = EXERCISM + " · transpose"
IO = [("input", "array.string lines"), ("output", "array.string")]
SUMMARY_FR = "Transposer un texte : la colonne k devient la ligne k. Si les lignes n'ont pas la même longueur, on complète par des espaces à gauche seulement, jamais à droite."
HINTS = ["La ligne k de la sortie lit le caractère k de chaque ligne d'entrée, de haut en bas.",
         "Pour la ligne k, une ligne d'entrée trop courte donne un espace seulement s'il reste une ligne plus bas qui a un caractère k ; sinon on s'arrête."]
DESC = """
<p>A legacy system prints reports written vertically: each column of the printed page is one record. To read them, you must transpose the text. You are given the page as a list of strings <code>lines</code>.</p>
<p>Line <code>k</code> of the result is made of the characters at position <code>k</code> of every input line, read from top to bottom. The input lines can have different lengths:</p>
<ul><li>if an input line is too short for position <code>k</code>, but a <b>later</b> line has a character at position <code>k</code>, a space is used instead;</li><li>a result line never ends with such padding spaces: after the last line that has a character at position <code>k</code>, nothing is added.</li></ul>
<p>Spaces that are really in the input are kept. Your task is to return the transposed lines. An empty input gives an empty list.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(lines):
    # write your code here
    return lines
"""
SOLUTION = """
def solution(lines):
    width = max((len(l) for l in lines), default=0)
    out = []
    for k in range(width):
        last = max(i for i, l in enumerate(lines) if len(l) > k)
        out.append("".join(l[k] if len(l) > k else " " for l in lines[: last + 1]))
    return out
"""
ALT = ["""
def solution(lines):
    rows = []
    for i in range(len(lines)):
        need = max((len(l) for l in lines[i:]), default=0)
        rows.append(lines[i].ljust(need, "\\0"))
    width = max((len(l) for l in rows), default=0)
    out = []
    for k in range(width):
        out.append("".join(r[k] for r in rows if k < len(r)).replace("\\0", " "))
    return out
"""]
MUTANTS = [
    """
def solution(lines):
    width = max((len(l) for l in lines), default=0)
    return ["".join(l.ljust(width)[k] for l in lines) for k in range(width)]
""",
    """
def solution(lines):
    width = max((len(l) for l in lines), default=0)
    return ["".join(l[k] for l in lines if len(l) > k) for k in range(width)]
""",
]
CASES = exercism("transpose")


def tests():
    t = [{"lines": ["ID42", "OK", "PAID"]}, {"lines": ["a", "bcd", "e f"]}]
    t += [{"lines": i["lines"]} for i, _ in CASES]
    r = rng(103)
    for _ in range(3):
        t.append({"lines": ["".join(r.choice("XY ") for _ in range(r.randint(0, 6))) for _ in range(r.randint(1, 5))]})
    return t


def expected():
    return [None, None] + [e for _, e in CASES] + [None] * 3
