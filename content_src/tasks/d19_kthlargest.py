from kit import rng

ID = "d19"
NAME = "K-th Largest Transaction"
LANG = "python"
PARAMS = ["amounts", "k"]
MINUTES = 12
TAGS = ["DSA", "tas (heapq)", "tas de taille k", "O(n log k)"]
IO = [("input", "array.integer amounts"), ("input", "integer k"), ("output", "integer")]
SUMMARY_FR = "Le k-ième plus grand montant (avec répétitions : [5, 5, 3], k = 2 donne 5), avec un tas min de taille k."
HINTS = ["Garde un tas min des k plus grands vus : heappush, et heappop si la taille dépasse k.", "À la fin, le sommet du tas (heap[0]) est le k-ième plus grand."]
DESC = """
<p>Fraud analysts watch a stream of transaction <code>amounts</code>. Your task is to return the <code>k</code>-th largest amount, counting repeated values (for <code>[5, 5, 3]</code> and <code>k = 2</code>, the answer is <code>5</code>). <code>1 &lt;= k &lt;= len(amounts)</code>.</p>
<p>Use a min-heap that keeps only <code>k</code> values: <code>O(n log k)</code> time, <code>O(k)</code> memory, so it also works on a stream.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import heapq


def solution(amounts, k):
    # write your code here
    return 0
"""
SOLUTION = """
import heapq


def solution(amounts, k):
    h = []
    for a in amounts:
        heapq.heappush(h, a)
        if len(h) > k:
            heapq.heappop(h)
    return h[0]
"""
ALT = ["""
def solution(amounts, k):
    return sorted(amounts, reverse=True)[k - 1]
"""]
MUTANTS = ["""
def solution(amounts, k):
    return sorted(set(amounts), reverse=True)[min(k, len(set(amounts))) - 1]
""", """
def solution(amounts, k):
    return sorted(amounts)[k - 1]
"""]


def tests():
    t = [{"amounts": [3, 2, 1, 5, 6, 4], "k": 2}, {"amounts": [5, 5, 3], "k": 2}, {"amounts": [7], "k": 1}]
    r = rng(2019)
    for _ in range(8):
        a = [r.randint(1, 20) for _ in range(r.randint(1, 15))]
        t.append({"amounts": a, "k": r.randint(1, len(a))})
    return t
