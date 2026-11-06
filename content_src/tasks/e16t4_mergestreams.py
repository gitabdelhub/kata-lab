from kit import rng

ID = "e16t4"
NAME = "Merge Sorted Log Streams"
LANG = "python"
PARAMS = ["streams"]
MINUTES = 20
TAGS = ["heapq", "fusion de k listes triées", "départage stable", "doublons consécutifs"]
IO = [("input", "array.array.array.string streams"), ("output", "array.string")]
DESC = """
<p>Each server of a cluster writes its own log, already sorted by time. You are given <code>streams</code>: <code>streams[i]</code> is the log of server <code>i</code>, a list of <code>[timestamp, message]</code> pairs sorted by <code>timestamp</code> (an integer written as a string, without leading zeros). A server can write several lines with the same timestamp.</p>
<p>Your task is to merge all logs and return one list of strings, sorted by timestamp, written as <code>"timestamp server message"</code> (for example <code>"105 2 disk full"</code>). When several lines have the same timestamp, the line of the server with the smallest index comes first, and lines of the same server keep their order.</p>
<p>Finally, when the <b>same message</b> appears on consecutive lines of the merged list (whatever the server and the timestamp), only its first line is kept.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(streams):
    # write your code here
    return []
"""
SOLUTION = """
import heapq


def solution(streams):
    heap = []
    for i, s in enumerate(streams):
        if s:
            heapq.heappush(heap, (int(s[0][0]), i, 0))
    out, last = [], None
    while heap:
        ts, i, k = heapq.heappop(heap)
        msg = streams[i][k][1]
        if msg != last:
            out.append(f"{ts} {i} {msg}")
        last = msg
        if k + 1 < len(streams[i]):
            heapq.heappush(heap, (int(streams[i][k + 1][0]), i, k + 1))
    return out
"""
MUTANTS = [
    """
def solution(streams):
    lines = sorted((ts, i, m) for i, s in enumerate(streams) for ts, m in s)
    out, last = [], None
    for ts, i, m in lines:
        if m != last: out.append(f"{ts} {i} {m}")
        last = m
    return out
""",
    """
def solution(streams):
    lines = sorted(((int(ts), i, k, m) for i, s in enumerate(streams) for k, (ts, m) in enumerate(s)))
    out, seen = [], set()
    for ts, i, k, m in lines:
        if m not in seen: out.append(f"{ts} {i} {m}")
        seen.add(m)
    return out
""",
    """
def solution(streams):
    lines = sorted(((int(ts), i, k, m) for i, s in enumerate(streams) for k, (ts, m) in enumerate(s)))
    out, last = [], None
    for ts, i, k, m in lines:
        if m != last: out.append(f"{ts} {i} {m}")
        last = m if m != last else None
    return out
""",
]


def tests():
    t = [{"streams": [[["100", "boot"], ["105", "disk full"], ["120", "ok"]], [["99", "boot"], ["105", "disk full"], ["105", "retry"]], [["105", "ok"]]]},
         {"streams": [[], [["9", "a"], ["10", "a"]], [["10", "b"], ["10", "a"]]]},
         {"streams": [[["5", "x"], ["5", "x"], ["5", "x"]]]}]
    r = rng(1604)
    for _ in range(8):
        st = []
        for _ in range(r.randint(1, 5)):
            ts, s = r.randint(1, 20), []
            for _ in range(r.randint(0, 6)):
                ts += r.choice([0, 0, 1, 3, 10])
                s.append([str(ts), r.choice(["ok", "retry", "disk full", "timeout"])])
            st.append(s)
        t.append({"streams": st})
    return t
