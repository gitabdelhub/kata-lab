from kit import rng

ID = "d07"
NAME = "Days Until a Higher Price"
LANG = "python"
PARAMS = ["prices"]
MINUTES = 15
TAGS = ["DSA", "pile monotone", "prochain plus grand", "O(n)"]
IO = [("input", "array.integer prices"), ("output", "array.integer")]
SUMMARY_FR = "Pour chaque jour, le nombre de jours à attendre avant un prix strictement plus haut, 0 s'il n'y en a pas. En O(n) avec une pile."
HINTS = ["Pile des indices dont on attend encore un prix plus haut (prix décroissants dans la pile).", "Quand prices[i] dépasse le sommet, dépile et note i - indice."]
DESC = """
<p><code>prices[i]</code> is the price of a product on day <code>i</code>. Your task is to return a list where element <code>i</code> is the number of days to wait after day <code>i</code> to see a <b>strictly higher</b> price, or <code>0</code> if it never happens.</p>
<p>The naive double loop is <code>O(n<sup>2</sup>)</code>; aim for <code>O(n)</code> with a stack.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(prices):
    # write your code here
    return []
"""
SOLUTION = """
def solution(prices):
    out = [0] * len(prices)
    stack = []
    for i, p in enumerate(prices):
        while stack and prices[stack[-1]] < p:
            j = stack.pop()
            out[j] = i - j
        stack.append(i)
    return out
"""
ALT = ["""
def solution(prices):
    out = []
    for i, p in enumerate(prices):
        out.append(next((j - i for j in range(i + 1, len(prices)) if prices[j] > p), 0))
    return out
"""]
MUTANTS = ["""
def solution(prices):
    out = [0] * len(prices); stack = []
    for i, p in enumerate(prices):
        while stack and prices[stack[-1]] <= p:
            j = stack.pop(); out[j] = i - j
        stack.append(i)
    return out
""", """
def solution(prices):
    return [1 if i + 1 < len(prices) and prices[i + 1] > p else 0 for i, p in enumerate(prices)]
"""]


def tests():
    t = [{"prices": [73, 74, 75, 71, 69, 72, 76, 73]}, {"prices": [5, 5, 6]}, {"prices": []}, {"prices": [9, 8, 7]}]
    r = rng(2007)
    for _ in range(8):
        t.append({"prices": [r.randint(1, 8) for _ in range(r.randint(1, 14))]})
    return t
