from kit import rng

ID = "d16"
NAME = "Merge Two Sorted Linked Lists"
LANG = "python"
PARAMS = ["a", "b"]
ENTRY = "__kata_entry__"
MINUTES = 15
TAGS = ["DSA", "liste chaînée", "nœud sentinelle", "fusion"]
IO = [("input", "array.integer a"), ("input", "array.integer b"), ("output", "array.integer")]
SUMMARY_FR = "Fusionner deux listes chaînées triées en une seule liste triée, en réutilisant les nœuds (pas de nouvelle liste de valeurs)."
HINTS = ["Un nœud sentinelle dummy = ListNode(0) et un pointeur tail : tu accroches à chaque fois le plus petit des deux.", "À égalité, prends d'abord le nœud de la liste a. À la fin, accroche le reste de la liste non vide."]
DESC = """
<p>Two sorted streams of order ids are stored as <b>singly linked lists</b> of <code>ListNode</code> (<code>val</code>, <code>next</code>). Implement <code>merge_lists(a, b)</code>: return the head of one sorted list that contains all nodes of both lists. <b>Reuse the existing nodes</b>: do not create new nodes for the values. When two values are equal, the node from <code>a</code> comes first.</p>
<p>The class <code>ListNode(val, next=None)</code> is already defined (you may create one extra sentinel node). The tests show <code>values</code> (the merged values) and <code>from</code> (for each node, the list it came from: <code>a</code> or <code>b</code>).</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
# class ListNode:  (already defined)
#     def __init__(self, val, next=None):
#         self.val = val
#         self.next = next

def merge_lists(a, b):
    # write your code here
    return a
"""
SOLUTION = """
def merge_lists(a, b):
    dummy = tail = ListNode(0)
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next
"""
WRAPPER = """
class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next


def __kata_build(values, tag):
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
        head.tag = tag
    return head


def __kata_entry__(a, b):
    ha, hb = __kata_build(a, "a"), __kata_build(b, "b")
    ids = set()
    for h in (ha, hb):
        while h: ids.add(id(h)); h = h.next
    res = merge_lists(ha, hb)
    out, tags, seen = [], [], set()
    while res is not None and id(res) not in seen and len(out) <= len(a) + len(b):
        seen.add(id(res)); out.append(res.val); tags.append(getattr(res, "tag", "?")); res = res.next
    if seen != ids:
        return {"error": "the merged list must contain exactly the nodes of a and b", "got": out}
    return {"values": out, "from": "".join(tags)}
"""
ALT = ["""
def merge_lists(a, b):
    if not a: return b
    if not b: return a
    if a.val <= b.val:
        a.next = merge_lists(a.next, b); return a
    b.next = merge_lists(a, b.next); return b
"""]
MUTANTS = ["""
def merge_lists(a, b):
    dummy = tail = ListNode(0)
    while a and b:
        if a.val < b.val: tail.next, a = a, a.next
        else: tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next
""", """
def merge_lists(a, b):
    dummy = tail = ListNode(0)
    while a and b:
        if a.val <= b.val: tail.next, a = a, a.next
        else: tail.next, b = b, b.next
        tail = tail.next
    return dummy.next
""", """
def merge_lists(a, b):
    vals = []
    for h in (a, b):
        while h: vals.append(h.val); h = h.next
    head = None
    for v in sorted(vals, reverse=True): head = ListNode(v, head)
    return head
"""]


def tests():
    t = [{"a": [1, 2, 4], "b": [1, 3, 4]}, {"a": [], "b": [0]}, {"a": [], "b": []}, {"a": [5, 6], "b": [1]}]
    r = rng(2016)
    for _ in range(6):
        t.append({"a": sorted(r.randint(0, 9) for _ in range(r.randint(0, 6))), "b": sorted(r.randint(0, 9) for _ in range(r.randint(0, 6)))})
    return t
