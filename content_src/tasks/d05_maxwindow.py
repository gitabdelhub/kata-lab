from kit import rng

ID = "d05"
NAME = "Busiest K-Minute Window"
LANG = "python"
PARAMS = ["counts", "k"]
MINUTES = 10
TAGS = ["DSA", "fenêtre glissante", "taille fixe", "O(n)"]
IO = [("input", "array.integer counts"), ("input", "integer k"), ("output", "array.integer")]
SUMMARY_FR = "counts[i] = requêtes à la minute i. Trouver la fenêtre de k minutes consécutives avec le plus de requêtes : renvoyer [début, total], le plus petit début en cas d'égalité, [] si k > len(counts)."
HINTS = ["Calcule la somme des k premières, puis fais glisser : + l'entrée, - la sortie.", "Ne mets à jour le meilleur que si c'est STRICTEMENT plus grand, pour garder le plus petit début."]
DESC = """
<p><code>counts[i]</code> is the number of requests received during minute <code>i</code>. Your task is to find the <code>k</code> consecutive minutes with the most requests and return <code>[start, total]</code>: the first minute of that window and its total. If several windows have the same total, return the one with the smallest <code>start</code>. If <code>k</code> is larger than the number of minutes, return <code>[]</code>.</p>
<p>Aim for <code>O(n)</code>: do not recompute each window from scratch.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(counts, k):
    # write your code here
    return []
"""
SOLUTION = """
def solution(counts, k):
    if k > len(counts):
        return []
    cur = sum(counts[:k])
    best = [0, cur]
    for i in range(k, len(counts)):
        cur += counts[i] - counts[i - k]
        if cur > best[1]:
            best = [i - k + 1, cur]
    return best
"""
ALT = ["""
def solution(counts, k):
    if k > len(counts): return []
    best = None
    for s in range(len(counts) - k + 1):
        tot = sum(counts[s:s + k])
        if best is None or tot > best[1]: best = [s, tot]
    return best
"""]
MUTANTS = ["""
def solution(counts, k):
    if k > len(counts): return []
    cur = sum(counts[:k]); best = [0, cur]
    for i in range(k, len(counts)):
        cur += counts[i] - counts[i - k]
        if cur >= best[1]: best = [i - k + 1, cur]
    return best
""", """
def solution(counts, k):
    if k > len(counts): return []
    cur = sum(counts[:k]); best = [0, cur]
    for i in range(k, len(counts)):
        cur += counts[i] - counts[i - k]
        if cur > best[1]: best = [i - k, cur]
    return best
"""]


def tests():
    t = [{"counts": [3, 1, 4, 1, 5, 9, 2], "k": 3}, {"counts": [2, 2, 2], "k": 2}, {"counts": [1], "k": 2}, {"counts": [0, 0, 7], "k": 1}]
    r = rng(2005)
    for _ in range(8):
        c = [r.randint(0, 6) for _ in range(r.randint(1, 12))]
        t.append({"counts": c, "k": r.randint(1, len(c) + 1)})
    return t
