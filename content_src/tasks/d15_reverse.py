from kit import rng

ID = "d15"
NAME = "Reverse a Linked Change Log"
LANG = "python"
PARAMS = ["values"]
ENTRY = "__kata_entry__"
MINUTES = 12
TAGS = ["DSA", "liste chaînée", "trois pointeurs", "O(1) mémoire"]
IO = [("input", "array.integer values"), ("output", "array.integer")]
SUMMARY_FR = "Inverser une liste chaînée en place (prev, cur, next) et renvoyer la nouvelle tête. Les tests donnent la liste sous forme de valeurs."
HINTS = ["prev = None, cur = head ; à chaque tour : nxt = cur.next, cur.next = prev, prev = cur, cur = nxt.", "La nouvelle tête est prev à la fin. Liste vide : head vaut None."]
DESC = """
<p>A change log is stored as a <b>singly linked list</b> of <code>ListNode</code> objects: each node has <code>val</code> and <code>next</code> (<code>None</code> after the last node). Implement <code>reverse_list(head)</code>: reverse the list <b>in place</b> and return the new head (<code>head</code> can be <code>None</code>).</p>
<p>The class <code>ListNode(val, next=None)</code> is already defined. In the tests, the input list and your returned list are shown as lists of values.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
# class ListNode:  (already defined)
#     def __init__(self, val, next=None):
#         self.val = val
#         self.next = next

def reverse_list(head):
    # write your code here
    return head
"""
SOLUTION = """
def reverse_list(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    return prev
"""
WRAPPER = """
class ListNode:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next


def __kata_entry__(values):
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    nodes = []
    n = head
    while n:
        nodes.append(n); n = n.next
    res = reverse_list(head)
    out, seen = [], set()
    while res is not None and id(res) not in seen and len(out) <= len(values):
        seen.add(id(res)); out.append(res.val); res = res.next
    if len(out) != len(values) or sorted(id(x) for x in nodes) != sorted(seen):
        return {"error": "the returned list must reuse the same nodes", "got": out}
    return out
"""
ALT = ["""
def reverse_list(head):
    if head is None or head.next is None: return head
    new = reverse_list(head.next)
    head.next.next = head; head.next = None
    return new
"""]
MUTANTS = ["""
def reverse_list(head):
    vals = []
    while head: vals.append(head.val); head = head.next
    new = None
    for v in vals: new = ListNode(v, new)
    return new
""", """
def reverse_list(head):
    prev, cur = None, head
    while cur and cur.next:
        nxt = cur.next; cur.next = prev; prev, cur = cur, nxt
    return prev
"""]


def tests():
    t = [{"values": [1, 2, 3, 4]}, {"values": []}, {"values": [7]}]
    r = rng(2015)
    for _ in range(6):
        t.append({"values": [r.randint(0, 9) for _ in range(r.randint(2, 10))]})
    return t
