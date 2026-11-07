from kit import rng

ID = "g01"
NAME = "Longest Character Run"
LANG = "python"
PARAMS = ["source"]
MINUTES = 12
TAGS = ["parcours de chaîne", "compteur", "égalité à droite", "BCG"]
SOURCE = "Question rapportée du test BCG (fastprep.io), réécrite et testée par Kata Lab"
IO = [("input", "string source"), ("output", "string")]
SUMMARY_FR = "Trouver la plus longue suite de caractères identiques et renvoyer le caractère suivi de sa longueur. En cas d'égalité, la suite la plus à droite gagne."
HINTS = ["Parcours la chaîne en gardant la longueur de la suite en cours ; quand le caractère change, compare avec le meilleur.",
         "Égalité : la plus à droite gagne, donc remplace le meilleur avec >= et pas >. N'oublie pas la dernière suite après la boucle."]
DESC = """
<p>You are given a non-empty string <code>source</code> made only of lowercase English letters.</p>
<p>A <i>run</i> is a maximal block of consecutive identical characters. Find the longest run. If several runs share the maximum length, choose the <b>rightmost</b> one.</p>
<p>Return the character of that run immediately followed by its length, with no separator (for example <code>"c3"</code>).</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(source):
    # write your code here
    return ""
"""
SOLUTION = """
def solution(source):
    best_ch, best_len = "", 0
    i = 0
    while i < len(source):
        j = i
        while j < len(source) and source[j] == source[i]:
            j += 1
        if j - i >= best_len:
            best_ch, best_len = source[i], j - i
        i = j
    return best_ch + str(best_len)
"""
ALT = ["""
from itertools import groupby
def solution(source):
    runs = [(len(list(g)), k) for k, g in groupby(source)]
    m = max(n for n, _ in runs)
    k = [c for n, c in runs if n == m][-1]
    return k + str(m)
"""]
MUTANTS = [
    """
def solution(source):
    best_ch, best_len = "", 0
    i = 0
    while i < len(source):
        j = i
        while j < len(source) and source[j] == source[i]:
            j += 1
        if j - i > best_len:
            best_ch, best_len = source[i], j - i
        i = j
    return best_ch + str(best_len)
""",
    """
def solution(source):
    best_ch, best_len, cur = source[0], 1, 1
    for k in range(1, len(source)):
        if source[k] == source[k - 1]:
            cur += 1
        else:
            if cur >= best_len:
                best_ch, best_len = source[k - 1], cur
            cur = 1
    return best_ch + str(best_len)
""",
    """
def solution(source):
    counts = {}
    for ch in source:
        counts[ch] = counts.get(ch, 0) + 1
    m = max(counts.values())
    return [c for c in source if counts[c] == m][-1] + str(m)
""",
]


def tests():
    t = [{"source": "bbacccdbbab"}, {"source": "bbaacaa"}, {"source": "z"}, {"source": "abc"},
         {"source": "aaaaaaaaaaaab"}, {"source": "abbbbbbbbbbbb"}, {"source": "aabbaabb"}]
    r = rng(1901)
    for _ in range(6):
        t.append({"source": "".join(r.choice("ab") * r.randint(1, 5) for _ in range(r.randint(2, 9)))})
    return t


def expected():
    return ["c3", "a2"] + [None] * 11
