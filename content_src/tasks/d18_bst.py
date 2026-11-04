from kit import rng

ID = "d18"
NAME = "Validate a Sorted Index Tree"
LANG = "python"
PARAMS = ["tree"]
ENTRY = "__kata_entry__"
MINUTES = 15
TAGS = ["DSA", "arbre binaire de recherche", "bornes min/max", "parcours infixe"]
IO = [("input", "array.integer tree"), ("output", "boolean")]
SUMMARY_FR = "Dire si l'arbre est un arbre binaire de recherche strict : tout le sous-arbre gauche < nœud < tout le sous-arbre droit (pas de doublon)."
HINTS = ["Comparer chaque nœud à ses enfants ne suffit pas : passe des bornes (low, high) dans la récursion.", "Autre méthode : le parcours infixe (gauche, nœud, droite) d'un BST est strictement croissant."]
DESC = """
<p>An index is stored as a binary tree of <code>TreeNode</code> (<code>val</code>, <code>left</code>, <code>right</code>). Implement <code>is_valid_bst(root)</code>: return <code>true</code> if, for every node, <b>all</b> values in its left subtree are strictly smaller than its value and <b>all</b> values in its right subtree are strictly greater. An empty tree is valid.</p>
<p>The class <code>TreeNode</code> is already defined. In the tests, the tree is shown in level order, with <code>null</code> for a missing child.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
# class TreeNode:  (already defined)
#     def __init__(self, val, left=None, right=None): ...

def is_valid_bst(root):
    # write your code here
    return True
"""
SOLUTION = """
def is_valid_bst(root, low=None, high=None):
    if root is None:
        return True
    if (low is not None and root.val <= low) or (high is not None and root.val >= high):
        return False
    return is_valid_bst(root.left, low, root.val) and is_valid_bst(root.right, root.val, high)
"""
WRAPPER = open(__file__.replace("d18_bst.py", "d17_depth.py")).read().split('WRAPPER = """')[1].split('"""')[0].replace(
    "return max_depth(__kata_tree(tree))", "return is_valid_bst(__kata_tree(tree))")
ALT = ["""
def is_valid_bst(root):
    vals = []
    def ino(n):
        if n: ino(n.left); vals.append(n.val); ino(n.right)
    ino(root)
    return all(a < b for a, b in zip(vals, vals[1:]))
"""]
MUTANTS = ["""
def is_valid_bst(root):
    if root is None: return True
    if root.left and root.left.val >= root.val: return False
    if root.right and root.right.val <= root.val: return False
    return is_valid_bst(root.left) and is_valid_bst(root.right)
""", """
def is_valid_bst(root, low=None, high=None):
    if root is None: return True
    if (low is not None and root.val < low) or (high is not None and root.val > high): return False
    return is_valid_bst(root.left, low, root.val) and is_valid_bst(root.right, root.val, high)
"""]


def bst_level(r, keys):
    class N:
        def __init__(s, v): s.v, s.l, s.r = v, None, None
    root = None
    for k in keys:
        if root is None:
            root = N(k); continue
        n = root
        while True:
            if k < n.v:
                if n.l is None: n.l = N(k); break
                n = n.l
            else:
                if n.r is None: n.r = N(k); break
                n = n.r
    out, q = [], [root]
    while q:
        n = q.pop(0)
        out.append(None if n is None else n.v)
        if n is not None:
            q += [n.l, n.r]
    while out and out[-1] is None:
        out.pop()
    return out


def tests():
    t = [{"tree": [5, 3, 8, 1, 4, 7, 9]}, {"tree": [5, 1, 8, None, None, 4, 9]}, {"tree": [2, 2, 3]}, {"tree": []}, {"tree": [10, 5, 15, None, None, 6, 20]}]
    r = rng(2018)
    for i in range(6):
        keys = r.sample(range(1, 30), r.randint(2, 9))
        lv = bst_level(r, keys)
        if i % 2:
            j = r.randrange(len(lv))
            if lv[j] is not None:
                lv[j] = r.choice([x for x in keys] + [lv[j] + 1])
        t.append({"tree": lv})
    return t
