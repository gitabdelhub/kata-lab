from kit import rng

ID = "d02"
NAME = "Two Invoices for a Payment"
LANG = "python"
PARAMS = ["amounts", "target"]
MINUTES = 12
TAGS = ["DSA", "dictionnaire", "complément", "O(n)"]
IO = [("input", "array.integer amounts"), ("input", "integer target"), ("output", "array.integer")]
SUMMARY_FR = "Trouver deux factures différentes dont la somme vaut exactement le paiement ; renvoyer leurs indices [i, j] avec i < j, la paire dont j est le plus petit, puis i le plus petit ; [] si aucune."
HINTS = ["Pour chaque j, le complément target - amounts[j] a-t-il déjà été vu ? Un dict valeur -> premier indice.", "Garde le PREMIER indice de chaque valeur pour avoir le plus petit i."]
DESC = """
<p>A customer paid <code>target</code> to settle exactly two invoices. <code>amounts[i]</code> is the amount of invoice <code>i</code> (in cents). Your task is to return <code>[i, j]</code> with <code>i &lt; j</code> and <code>amounts[i] + amounts[j] == target</code>.</p>
<p>If several pairs work, return the one with the smallest <code>j</code>, then the smallest <code>i</code>. If no pair works, return <code>[]</code>. Aim for <code>O(n)</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(amounts, target):
    # write your code here
    return []
"""
SOLUTION = """
def solution(amounts, target):
    first = {}
    for j, a in enumerate(amounts):
        i = first.get(target - a)
        if i is not None:
            return [i, j]
        if a not in first:
            first[a] = j
    return []
"""
ALT = ["""
def solution(amounts, target):
    for j in range(len(amounts)):
        for i in range(j):
            if amounts[i] + amounts[j] == target:
                return [i, j]
    return []
"""]
MUTANTS = ["""
def solution(amounts, target):
    pos = {}
    for j, a in enumerate(amounts):
        if target - a in pos: return [pos[target - a], j]
        pos[a] = j
    return []
""", """
def solution(amounts, target):
    pos = {a: i for i, a in enumerate(amounts)}
    for i, a in enumerate(amounts):
        if target - a in pos: return sorted([i, pos[target - a]])
    return []
"""]


def tests():
    t = [{"amounts": [500, 300, 200, 700], "target": 1000}, {"amounts": [5, 5, 5], "target": 10}, {"amounts": [1, 2], "target": 4}, {"amounts": [3, 1, 3, 3], "target": 6}, {"amounts": [3, 3, 1, 2], "target": 4}]
    r = rng(2002)
    for _ in range(8):
        a = [r.randint(1, 9) for _ in range(r.randint(2, 10))]
        t.append({"amounts": a, "target": r.randint(2, 14)})
    return t
