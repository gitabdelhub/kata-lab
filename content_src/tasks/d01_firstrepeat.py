from kit import rng

ID = "d01"
NAME = "First Repeated Event"
LANG = "python"
PARAMS = ["event_ids"]
MINUTES = 10
TAGS = ["DSA", "ensemble (set)", "O(n)"]
IO = [("input", "array.string event_ids"), ("output", "string")]
SUMMARY_FR = "Renvoyer le premier identifiant qui apparaît une deuxième fois en lisant la liste de gauche à droite, ou une chaîne vide."
HINTS = ["Un set des identifiants déjà vus : l'appartenance coûte O(1).", "Le premier à revenir, c'est celui dont la DEUXIÈME apparition arrive en premier, pas celui qui apparaît en premier."]
DESC = """
<p>A stream delivers <code>event_ids</code> in order. Some events are delivered twice. Your task is to return the first id that is seen a second time while reading the list from left to right, or <code>""</code> if no id repeats.</p>
<p>The list can have up to <code>10<sup>5</sup></code> ids: aim for <code>O(n)</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(event_ids):
    # write your code here
    return ""
"""
SOLUTION = """
def solution(event_ids):
    seen = set()
    for e in event_ids:
        if e in seen:
            return e
        seen.add(e)
    return ""
"""
ALT = ["""
def solution(event_ids):
    best, ans = None, ""
    for j in range(len(event_ids)):
        for i in range(j):
            if event_ids[i] == event_ids[j]:
                if best is None or j < best:
                    best, ans = j, event_ids[j]
    return ans
"""]
MUTANTS = ["""
from collections import Counter
def solution(event_ids):
    c = Counter(event_ids)
    for e in event_ids:
        if c[e] > 1: return e
    return ""
""", """
def solution(event_ids):
    seen = set()
    for e in event_ids:
        if e in seen: return e
        seen.add(e)
    return None
"""]


def tests():
    t = [{"event_ids": ["a", "b", "c", "b", "a"]}, {"event_ids": ["x", "y"]}, {"event_ids": []}]
    r = rng(2001)
    for _ in range(8):
        t.append({"event_ids": [r.choice("abcdefghij") + str(r.randint(1, 3)) for _ in range(r.randint(1, 12))]})
    return t
