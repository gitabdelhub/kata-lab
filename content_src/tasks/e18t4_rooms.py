from kit import rng

ID = "e18t4"
NAME = "Assign Meeting Rooms"
LANG = "python"
PARAMS = ["meetings", "rooms"]
MINUTES = 20
TAGS = ["heapq", "deux tas", "intervalles", "plus petit index libre"]
IO = [("input", "array.array.integer meetings"), ("input", "integer rooms"), ("output", "array.integer")]
DESC = """
<p>An office has <code>rooms</code> meeting rooms, numbered from <code>0</code>. You are given <code>meetings</code>, a list of <code>[start, end]</code> pairs (integers, <code>start &lt; end</code>); a meeting uses its room from <code>start</code> included to <code>end</code> excluded. All start times are different.</p>
<p>Meetings are handled in order of start time. A meeting goes to the <b>free room with the smallest number</b>. When no room is free, the meeting is <b>delayed</b>: it waits for the first room that becomes free (smallest number if several become free at the same time) and keeps its duration.</p>
<p>Your task is to return a list with, for each meeting in the order of the input, the number of the room it used.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(meetings, rooms):
    # write your code here
    return []
"""
SOLUTION = """
import heapq


def solution(meetings, rooms):
    free = list(range(rooms))
    busy = []
    out = [None] * len(meetings)
    for idx in sorted(range(len(meetings)), key=lambda i: meetings[i][0]):
        s, e = meetings[idx]
        while busy and busy[0][0] <= s:
            heapq.heappush(free, heapq.heappop(busy)[1])
        if free:
            room = heapq.heappop(free)
            heapq.heappush(busy, (e, room))
        else:
            t, room = heapq.heappop(busy)
            heapq.heappush(busy, (t + e - s, room))
        out[idx] = room
    return out
"""
MUTANTS = [
    """
import heapq
def solution(meetings, rooms):
    free, busy, out = list(range(rooms)), [], []
    for s, e in meetings:
        while busy and busy[0][0] <= s: heapq.heappush(free, heapq.heappop(busy)[1])
        if free: room = heapq.heappop(free); heapq.heappush(busy, (e, room))
        else: t, room = heapq.heappop(busy); heapq.heappush(busy, (t + e - s, room))
        out.append(room)
    return out
""",
    """
import heapq
def solution(meetings, rooms):
    free, busy, out = list(range(rooms)), [], [None] * len(meetings)
    for idx in sorted(range(len(meetings)), key=lambda i: meetings[i][0]):
        s, e = meetings[idx]
        while busy and busy[0][0] <= s: heapq.heappush(free, heapq.heappop(busy)[1])
        if free: room = heapq.heappop(free); heapq.heappush(busy, (e, room))
        else: t, room = heapq.heappop(busy); heapq.heappush(busy, (e, room))
        out[idx] = room
    return out
""",
    """
import heapq
def solution(meetings, rooms):
    free, busy, out = list(range(rooms)), [], [None] * len(meetings)
    for idx in sorted(range(len(meetings)), key=lambda i: meetings[i][0]):
        s, e = meetings[idx]
        while busy and busy[0][0] < s: heapq.heappush(free, heapq.heappop(busy)[1])
        if free: room = heapq.heappop(free); heapq.heappush(busy, (e, room))
        else: t, room = heapq.heappop(busy); heapq.heappush(busy, (t + e - s, room))
        out[idx] = room
    return out
""",
]


def tests():
    t = [{"meetings": [[0, 10], [1, 5], [2, 7], [3, 4]], "rooms": 2},
         {"meetings": [[5, 10], [0, 5], [10, 11], [1, 2]], "rooms": 1},
         {"meetings": [[1, 3], [3, 5], [2, 6]], "rooms": 3}]
    r = rng(1804)
    for _ in range(8):
        starts = r.sample(range(0, 40), r.randint(2, 12))
        t.append({"meetings": [[s, s + r.randint(1, 9)] for s in starts], "rooms": r.randint(1, 3)})
    return t
