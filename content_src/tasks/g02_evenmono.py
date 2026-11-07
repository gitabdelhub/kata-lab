from kit import rng

ID = "g02"
NAME = "Even-Position Trend"
LANG = "python"
PARAMS = ["numbers"]
MINUTES = 10
TAGS = ["indices pairs", "parcours de liste", "strictement", "BCG"]
SOURCE = "Question rapportée du test BCG (fastprep.io), réécrite et testée par Kata Lab"
IO = [("input", "array.integer numbers"), ("output", "string")]
SUMMARY_FR = "Regarder seulement les valeurs aux indices pairs (0, 2, 4...) et dire si elles sont strictement croissantes, strictement décroissantes, ou ni l'un ni l'autre."
HINTS = ["Construis d'abord la liste des valeurs aux indices 0, 2, 4... avec range(0, len(numbers), 2).",
         "Strictement : deux valeurs égales cassent les deux tendances, la réponse est alors \"none\"."]
DESC = """
<p>You are given an array of non-negative integers <code>numbers</code> (length at least <code>3</code>). Consider only the elements at <b>even</b> zero-based indices: <code>0, 2, 4, ...</code>. Elements at odd indices are ignored.</p>
<p>Return <code>"increasing"</code> if those elements are strictly increasing, <code>"decreasing"</code> if they are strictly decreasing, and <code>"none"</code> otherwise.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(numbers):
    # write your code here
    return ""
"""
SOLUTION = """
def solution(numbers):
    ev = numbers[0::2]
    if all(ev[i] < ev[i + 1] for i in range(len(ev) - 1)):
        return "increasing"
    if all(ev[i] > ev[i + 1] for i in range(len(ev) - 1)):
        return "decreasing"
    return "none"
"""
MUTANTS = [
    """
def solution(numbers):
    ev = numbers[0::2]
    if all(ev[i] <= ev[i + 1] for i in range(len(ev) - 1)):
        return "increasing"
    if all(ev[i] >= ev[i + 1] for i in range(len(ev) - 1)):
        return "decreasing"
    return "none"
""",
    """
def solution(numbers):
    ev = numbers[1::2]
    if all(ev[i] < ev[i + 1] for i in range(len(ev) - 1)):
        return "increasing"
    if all(ev[i] > ev[i + 1] for i in range(len(ev) - 1)):
        return "decreasing"
    return "none"
""",
    """
def solution(numbers):
    ev = numbers[0::2]
    if ev[0] < ev[-1]:
        return "increasing"
    if ev[0] > ev[-1]:
        return "decreasing"
    return "none"
""",
]


def tests():
    t = [{"numbers": [12, 65, 15, 72, 19, 72]}, {"numbers": [12, 1, 54, 5, 19, 14]}, {"numbers": [666, 17, 66, 5, 6, 23]},
         {"numbers": [5, 9, 5]}, {"numbers": [1, 100, 2, 0, 3]}, {"numbers": [9, 0, 7, 0, 7, 0]}, {"numbers": [1, 50, 3, 40, 2, 60, 4]}]
    r = rng(1902)
    for _ in range(6):
        n = r.randint(3, 9)
        base = sorted(r.sample(range(100), n), reverse=r.random() < 0.5)
        if r.random() < 0.4:
            base = [r.randint(0, 20) for _ in range(n)]
        t.append({"numbers": base})
    return t


def expected():
    return ["increasing", "none", "decreasing"] + [None] * 10
