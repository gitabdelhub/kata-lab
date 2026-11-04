from kit import rng

ID = "d24"
NAME = "Common Steps of Two Pipelines"
LANG = "python"
PARAMS = ["a", "b"]
MINUTES = 18
TAGS = ["DSA", "programmation dynamique", "tableau 2D", "plus longue sous-suite commune"]
IO = [("input", "array.string a"), ("input", "array.string b"), ("output", "integer")]
SUMMARY_FR = "Longueur de la plus longue sous-suite commune (pas forcément contiguë, ordre respecté) entre deux listes d'étapes. C'est la base des outils de diff."
HINTS = ["dp[i][j] = réponse pour a[:i] et b[:j]. Si a[i-1] == b[j-1] : dp[i-1][j-1] + 1, sinon max(dp[i-1][j], dp[i][j-1]).", "Sous-suite, pas sous-chaîne : les étapes communes n'ont pas besoin d'être côte à côte."]
DESC = """
<p>Two versions of a pipeline are given as lists of step names <code>a</code> and <code>b</code>. Your task is to return the length of their longest common <b>subsequence</b>: the largest number of steps that appear in both lists in the same order, not necessarily next to each other. This is how diff tools find unchanged lines.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(a, b):
    # write your code here
    return 0
"""
SOLUTION = """
def solution(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[len(a)][len(b)]
"""
ALT = ["""
from functools import lru_cache
def solution(a, b):
    @lru_cache(None)
    def f(i, j):
        if i == len(a) or j == len(b): return 0
        if a[i] == b[j]: return 1 + f(i + 1, j + 1)
        return max(f(i + 1, j), f(i, j + 1))
    return f(0, 0)
"""]
MUTANTS = ["""
def solution(a, b):
    best = 0
    for i in range(len(a)):
        for j in range(len(b)):
            k = 0
            while i + k < len(a) and j + k < len(b) and a[i + k] == b[j + k]: k += 1
            best = max(best, k)
    return best
""", """
def solution(a, b):
    return len(set(a) & set(b))
"""]


def tests():
    t = [{"a": ["extract", "clean", "join", "load", "test"], "b": ["extract", "join", "dedupe", "load"]}, {"a": [], "b": ["x"]}, {"a": ["a", "b", "a"], "b": ["a", "a"]}, {"a": ["x", "y"], "b": ["y", "x"]}]
    r = rng(2024)
    for _ in range(8):
        t.append({"a": [r.choice("abcde") for _ in range(r.randint(0, 9))], "b": [r.choice("abcde") for _ in range(r.randint(0, 9))]})
    return t
