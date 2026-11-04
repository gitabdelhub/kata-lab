from kit import rng

ID = "d09"
NAME = "First Log Line After a Time"
LANG = "python"
PARAMS = ["times", "t"]
MINUTES = 10
TAGS = ["DSA", "recherche binaire", "lower bound", "O(log n)"]
IO = [("input", "array.integer times"), ("input", "integer t"), ("output", "integer")]
SUMMARY_FR = "Liste triée d'horodatages : renvoyer l'indice de la première ligne dont l'heure est >= t (len(times) s'il n'y en a pas), en O(log n), sans le module bisect."
HINTS = ["lo = 0, hi = len(times) ; tant que lo < hi : mid ; si times[mid] < t alors lo = mid + 1, sinon hi = mid.", "Avec des doublons, il faut le PREMIER indice : ne t'arrête pas dès que tu trouves t."]
DESC = """
<p>A huge log file is sorted by time. <code>times</code> holds the timestamp of each line in order (several lines can share a timestamp). Your task is to return the index of the <b>first</b> line with a timestamp greater than or equal to <code>t</code>, or <code>len(times)</code> if there is none.</p>
<p>Write the binary search yourself (no <code>bisect</code>): <code>O(log n)</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(times, t):
    # write your code here
    return 0
"""
SOLUTION = """
def solution(times, t):
    lo, hi = 0, len(times)
    while lo < hi:
        mid = (lo + hi) // 2
        if times[mid] < t:
            lo = mid + 1
        else:
            hi = mid
    return lo
"""
ALT = ["""
def solution(times, t):
    return next((i for i, x in enumerate(times) if x >= t), len(times))
"""]
MUTANTS = ["""
def solution(times, t):
    lo, hi = 0, len(times)
    while lo < hi:
        mid = (lo + hi) // 2
        if times[mid] <= t: lo = mid + 1
        else: hi = mid
    return lo
""", """
def solution(times, t):
    lo, hi = 0, len(times) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if times[mid] < t: lo = mid + 1
        else: hi = mid
    return lo
"""]


def tests():
    t = [{"times": [1, 3, 3, 3, 8], "t": 3}, {"times": [1, 2], "t": 5}, {"times": [], "t": 1}, {"times": [4, 4], "t": 0}]
    r = rng(2009)
    for _ in range(8):
        t.append({"times": sorted(r.randint(0, 10) for _ in range(r.randint(1, 12))), "t": r.randint(-1, 12)})
    return t
