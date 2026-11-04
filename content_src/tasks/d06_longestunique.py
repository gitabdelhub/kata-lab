from kit import rng

ID = "d06"
NAME = "Longest Run of Distinct Pages"
LANG = "python"
PARAMS = ["pages"]
MINUTES = 15
TAGS = ["DSA", "fenêtre glissante", "taille variable", "dernier indice vu"]
IO = [("input", "array.string pages"), ("output", "integer")]
SUMMARY_FR = "Longueur de la plus longue suite de pages consécutives sans aucune page répétée."
HINTS = ["Fenêtre [left, right] ; un dict page -> dernier indice vu.", "Quand la page est déjà dans la fenêtre (dernier indice >= left), avance left juste après ce dernier indice."]
DESC = """
<p><code>pages</code> is the list of pages a user visited, in order. Your task is to return the length of the longest run of <b>consecutive</b> visits in which no page appears twice.</p>
<p>Aim for <code>O(n)</code> with a window that grows on the right and shrinks on the left.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(pages):
    # write your code here
    return 0
"""
SOLUTION = """
def solution(pages):
    last, left, best = {}, 0, 0
    for right, p in enumerate(pages):
        if p in last and last[p] >= left:
            left = last[p] + 1
        last[p] = right
        best = max(best, right - left + 1)
    return best
"""
ALT = ["""
def solution(pages):
    best = 0
    for i in range(len(pages)):
        seen = set()
        for j in range(i, len(pages)):
            if pages[j] in seen: break
            seen.add(pages[j]); best = max(best, j - i + 1)
    return best
"""]
MUTANTS = ["""
def solution(pages):
    last, left, best = {}, 0, 0
    for right, p in enumerate(pages):
        if p in last: left = last[p] + 1
        last[p] = right
        best = max(best, right - left + 1)
    return best
""", """
def solution(pages):
    return len(set(pages))
"""]


def tests():
    t = [{"pages": ["home", "cart", "home", "pay", "done"]}, {"pages": []}, {"pages": ["a", "b", "b", "a"]}, {"pages": ["a", "b", "c", "a", "d", "b"]}]
    r = rng(2006)
    for _ in range(8):
        t.append({"pages": [r.choice("abcdef") for _ in range(r.randint(1, 14))]})
    return t
