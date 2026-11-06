from kit import rng

ID = "d17"
NAME = "Depth of a Category Tree"
LANG = "python"
PARAMS = ["tree"]
ENTRY = "__kata_entry__"
MINUTES = 10
TAGS = ["DSA", "arbre binaire", "récursion", "DFS"]
IO = [("input", "array.integer tree"), ("output", "integer")]
SUMMARY_FR = "Profondeur maximale d'un arbre binaire (nombre de nœuds sur le plus long chemin racine -> feuille), 0 pour un arbre vide."
HINTS = ["Récursion : 0 si root est None, sinon 1 + max(profondeur gauche, profondeur droite).", "Variante itérative : BFS niveau par niveau avec une deque, et compter les niveaux."]
DESC = """
<p>A product category tree is a <b>binary tree</b> of <code>TreeNode</code> objects (<code>val</code>, <code>left</code>, <code>right</code>). Implement <code>max_depth(root)</code> so that it returns an integer: the number of nodes on the longest path from the root down to a leaf, or <code>0</code> if <code>root</code> is <code>None</code>.</p>
<p>The class <code>TreeNode</code> is already defined. In the tests, the tree is shown in level order, with <code>null</code> for a missing child (like on most coding platforms).</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
# class TreeNode:  (already defined)
#     def __init__(self, val, left=None, right=None): ...

def max_depth(root):
    # write your code here
    return 0
"""
SOLUTION = """
def max_depth(root):
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
"""
WRAPPER = """
from collections import deque as _kdq


class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def __kata_tree(vals):
    if not vals or vals[0] is None:
        return None
    root = TreeNode(vals[0]); q = _kdq([root]); i = 1
    while q and i < len(vals):
        n = q.popleft()
        if i < len(vals) and vals[i] is not None:
            n.left = TreeNode(vals[i]); q.append(n.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            n.right = TreeNode(vals[i]); q.append(n.right)
        i += 1
    return root


def __kata_entry__(tree):
    return max_depth(__kata_tree(tree))
"""
ALT = ["""
from collections import deque
def max_depth(root):
    if not root: return 0
    q, d = deque([root]), 0
    while q:
        d += 1
        for _ in range(len(q)):
            n = q.popleft()
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
    return d
"""]
MUTANTS = ["""
def max_depth(root):
    if root is None: return 0
    return 1 + max_depth(root.left)
""", """
def max_depth(root):
    if root is None: return 0
    if root.left is None or root.right is None: return 1
    return 1 + max(max_depth(root.left), max_depth(root.right))
"""]


def rand_tree(r, n):
    vals, alive = [1], 1
    while len(vals) < n and alive:
        a = r.random() < 0.7
        vals.append(len(vals) + 1 if a else None)
    while vals and vals[-1] is None:
        vals.pop()
    return vals


def tests():
    t = [{"tree": [3, 9, 20, None, None, 15, 7]}, {"tree": []}, {"tree": [1, None, 2, None, 3]}, {"tree": [1, 2, 3, 4]}]
    r = rng(2017)
    for _ in range(6):
        t.append({"tree": rand_tree(r, r.randint(2, 15))})
    return t
