from kit import rng

ID = "e17t4"
NAME = "API Rate Limiter"
LANG = "python"
PARAMS = ["requests", "limit", "window"]
MINUTES = 20
TAGS = ["fenêtre glissante", "deque", "dictionnaire de files", "requêtes refusées non comptées"]
IO = [("input", "array.array.string requests"), ("input", "integer limit"), ("input", "integer window"), ("output", "array.boolean")]
DESC = """
<p>An API accepts at most <code>limit</code> requests per client in any window of <code>window</code> seconds. You are given <code>requests</code>, a list of <code>[timestamp, client_id]</code> pairs sorted by timestamp (the timestamp is an integer number of seconds written as a string).</p>
<p>A request of a client at time <code>t</code> is <b>accepted</b> when the number of <b>accepted</b> requests of the same client with a timestamp in <code>(t - window, t]</code> is strictly less than <code>limit</code>. Refused requests do not count. Each client has its own counter.</p>
<p>Your task is to return a list of booleans: <code>true</code> when the request at the same position is accepted.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(requests, limit, window):
    # write your code here
    return []
"""
SOLUTION = """
from collections import defaultdict, deque


def solution(requests, limit, window):
    seen = defaultdict(deque)
    out = []
    for ts, client in requests:
        t = int(ts)
        q = seen[client]
        while q and q[0] <= t - window:
            q.popleft()
        if len(q) < limit:
            q.append(t)
            out.append(True)
        else:
            out.append(False)
    return out
"""
MUTANTS = [
    """
from collections import defaultdict, deque
def solution(requests, limit, window):
    seen, out = defaultdict(deque), []
    for ts, c in requests:
        t, q = int(ts), seen[c]
        while q and q[0] <= t - window: q.popleft()
        out.append(len(q) < limit)
        q.append(t)
    return out
""",
    """
from collections import defaultdict, deque
def solution(requests, limit, window):
    seen, out = defaultdict(deque), []
    for ts, c in requests:
        t, q = int(ts), seen[c]
        while q and q[0] < t - window: q.popleft()
        if len(q) < limit: q.append(t); out.append(True)
        else: out.append(False)
    return out
""",
    """
from collections import deque
def solution(requests, limit, window):
    q, out = deque(), []
    for ts, c in requests:
        t = int(ts)
        while q and q[0] <= t - window: q.popleft()
        if len(q) < limit: q.append(t); out.append(True)
        else: out.append(False)
    return out
""",
]


def tests():
    t = [{"requests": [["1", "a"], ["2", "a"], ["3", "a"], ["3", "b"], ["11", "a"], ["12", "a"]], "limit": 2, "window": 10},
         {"requests": [["0", "x"], ["0", "x"], ["5", "x"], ["5", "x"], ["10", "x"]], "limit": 2, "window": 5},
         {"requests": [], "limit": 1, "window": 1}]
    r = rng(1704)
    for _ in range(8):
        ts, req = 0, []
        for _ in range(r.randint(3, 25)):
            ts += r.choice([0, 0, 1, 2, 5])
            req.append([str(ts), r.choice("abc")])
        t.append({"requests": req, "limit": r.randint(1, 4), "window": r.choice([3, 5, 10])})
    return t
