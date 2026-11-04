from kit import rng

ID = "d25"
NAME = "Can the Retry Chain Finish"
LANG = "python"
PARAMS = ["jumps"]
MINUTES = 12
TAGS = ["DSA", "glouton", "portée maximale", "O(n)"]
IO = [("input", "array.integer jumps"), ("output", "boolean")]
SUMMARY_FR = "Depuis la position 0, on peut avancer de 1 à jumps[i] cases. Peut-on atteindre la dernière position ? Glouton : garder la portée maximale."
HINTS = ["reach = la plus loin qu'on peut atteindre jusqu'ici. Si i > reach, on est bloqué.", "reach = max(reach, i + jumps[i]). Liste d'un seul élément : true."]
DESC = """
<p>A workflow has steps <code>0</code> to <code>n - 1</code>. From step <code>i</code>, the scheduler can jump forward by any number of steps between <code>1</code> and <code>jumps[i]</code> (<code>0</code> means it is stuck there). Starting at step <code>0</code>, your task is to return <code>true</code> if the last step can be reached. <code>jumps</code> is not empty.</p>
<p>A greedy <code>O(n)</code> solution exists: keep the farthest step reachable so far.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(jumps):
    # write your code here
    return False
"""
SOLUTION = """
def solution(jumps):
    reach = 0
    for i, j in enumerate(jumps):
        if i > reach:
            return False
        reach = max(reach, i + j)
    return True
"""
ALT = ["""
def solution(jumps):
    n = len(jumps); ok = [False] * n; ok[0] = True
    for i in range(n):
        if ok[i]:
            for k in range(1, jumps[i] + 1):
                if i + k < n: ok[i + k] = True
    return ok[-1]
"""]
MUTANTS = ["""
def solution(jumps):
    return 0 not in jumps[:-1]
""", """
def solution(jumps):
    i = 0
    while i < len(jumps) - 1:
        if jumps[i] == 0: return False
        i += jumps[i]
    return True
"""]


def tests():
    t = [{"jumps": [2, 3, 1, 1, 4]}, {"jumps": [3, 2, 1, 0, 4]}, {"jumps": [0]}, {"jumps": [2, 0, 0]}, {"jumps": [1, 3, 0, 0, 2]}, {"jumps": [2, 5, 0, 0]}]
    r = rng(2025)
    for _ in range(8):
        t.append({"jumps": [r.choice([0, 0, 1, 1, 2, 3]) for _ in range(r.randint(1, 10))]})
    return t
