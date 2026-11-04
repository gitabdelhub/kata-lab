from kit import rng

ID = "d23"
NAME = "Fewest Batches to Reach a Quota"
LANG = "python"
PARAMS = ["batch_sizes", "quota"]
MINUTES = 15
TAGS = ["DSA", "programmation dynamique", "rendu de monnaie", "le glouton échoue"]
IO = [("input", "array.integer batch_sizes"), ("input", "integer quota"), ("output", "integer")]
SUMMARY_FR = "Nombre minimal de lots (tailles réutilisables) dont la somme vaut exactement le quota, -1 si impossible. Le glouton « toujours le plus gros » est faux."
HINTS = ["dp[x] = nombre minimal de lots pour faire exactement x ; dp[0] = 0.", "dp[x] = 1 + min(dp[x - s]) pour chaque taille s <= x. Contre-exemple du glouton : tailles [1, 3, 4], quota 6."]
DESC = """
<p>A job processes records in batches whose size must be one of <code>batch_sizes</code> (each size can be used any number of times). Your task is to return the minimum number of batches whose sizes add up to <b>exactly</b> <code>quota</code>, or <code>-1</code> if it is impossible. <code>quota = 0</code> needs <code>0</code> batches.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(batch_sizes, quota):
    # write your code here
    return -1
"""
SOLUTION = """
def solution(batch_sizes, quota):
    INF = float("inf")
    dp = [0] + [INF] * quota
    for x in range(1, quota + 1):
        for s in batch_sizes:
            if s <= x and dp[x - s] + 1 < dp[x]:
                dp[x] = dp[x - s] + 1
    return dp[quota] if dp[quota] != INF else -1
"""
ALT = ["""
from collections import deque
def solution(batch_sizes, quota):
    dist = {0: 0}; q = deque([0])
    while q:
        x = q.popleft()
        if x == quota: return dist[x]
        for s in batch_sizes:
            y = x + s
            if y <= quota and y not in dist: dist[y] = dist[x] + 1; q.append(y)
    return -1
"""]
MUTANTS = ["""
def solution(batch_sizes, quota):
    n = 0
    for s in sorted(batch_sizes, reverse=True):
        n += quota // s; quota %= s
    return n if quota == 0 else -1
""", """
def solution(batch_sizes, quota):
    INF = float("inf"); dp = [0] + [INF] * quota
    for x in range(1, quota + 1):
        for s in batch_sizes:
            if s <= x and dp[x - s] + 1 < dp[x]: dp[x] = dp[x - s] + 1
    return dp[quota] if dp[quota] != INF else 0
"""]


def tests():
    t = [{"batch_sizes": [1, 3, 4], "quota": 6}, {"batch_sizes": [2], "quota": 3}, {"batch_sizes": [5, 2], "quota": 0}, {"batch_sizes": [1, 2, 5], "quota": 11}]
    r = rng(2023)
    for _ in range(8):
        t.append({"batch_sizes": r.sample(range(2, 10), r.randint(1, 3)), "quota": r.randint(0, 30)})
    return t
