from kit import rng

ID = "e03t4"
NAME = "Consultation Room Scheduler"
LANG = "python"
PARAMS = ["requests", "rooms"]
MINUTES = 25
TAGS = ["heapq", "simulation", "tri", "deux tas"]
IO = [("input", "array.array.integer requests"), ("input", "integer rooms"), ("output", "array.array.integer")]
DESC = """
<p>A clinic has <code>rooms</code> consultation rooms, numbered from <code>0</code> to <code>rooms - 1</code>. Patients arrive during the day, and each one needs a room for a given time. You are given <code>requests</code>, a list of <code>[patient_id, arrival, duration]</code> (integers, in minutes). The list is not sorted.</p>
<p>Requests are handled in order of <code>arrival</code>; requests with the same <code>arrival</code> are handled in increasing <code>patient_id</code> order. When a request is handled:</p>
<ol><li>if one or more rooms are free at the arrival time, the patient gets the free room with the <b>smallest number</b> and starts at <code>arrival</code>. A room whose previous consultation ends exactly at <code>arrival</code> is free;</li><li>otherwise the patient waits for the room that becomes free <b>first</b> (if several rooms become free at the same time, the one with the smallest number), and starts when it becomes free;</li><li>the consultation keeps the same duration, so it ends at <code>start + duration</code>.</li></ol>
<p>Return a list of <code>[patient_id, room, start, end]</code>, sorted by <code>patient_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>Patient <code>4</code> arrives at <code>12</code> while both rooms are busy. Room <code>1</code> becomes free first, at <code>15</code>.</p>
"""
STARTER = """
def solution(requests, rooms):
    # write your code here
    return []
"""
SOLUTION = """
import heapq


def solution(requests, rooms):
    free = list(range(rooms))
    heapq.heapify(free)
    busy = []
    out = []
    for pid, arrival, duration in sorted(requests, key=lambda r: (r[1], r[0])):
        while busy and busy[0][0] <= arrival:
            _, room = heapq.heappop(busy)
            heapq.heappush(free, room)
        if free:
            room = heapq.heappop(free)
            start = arrival
        else:
            start, room = heapq.heappop(busy)
        heapq.heappush(busy, (start + duration, room))
        out.append([pid, room, start, start + duration])
    return sorted(out)
"""
MUTANTS = [
    """
import heapq
def solution(requests, rooms):
    busy = [(0, r) for r in range(rooms)]
    heapq.heapify(busy)
    out = []
    for pid, arrival, duration in sorted(requests, key=lambda r: (r[1], r[0])):
        end, room = heapq.heappop(busy)
        start = max(end, arrival)
        heapq.heappush(busy, (start + duration, room))
        out.append([pid, room, start, start + duration])
    return sorted(out)
""",
    """
import heapq
def solution(requests, rooms):
    free = list(range(rooms)); heapq.heapify(free); busy = []; out = []
    for pid, arrival, duration in sorted(requests, key=lambda r: (r[1], r[0])):
        while busy and busy[0][0] < arrival:
            _, room = heapq.heappop(busy); heapq.heappush(free, room)
        if free:
            room = heapq.heappop(free); start = arrival
        else:
            start, room = heapq.heappop(busy)
        heapq.heappush(busy, (start + duration, room)); out.append([pid, room, start, start + duration])
    return sorted(out)
""",
    """
import heapq
def solution(requests, rooms):
    free = list(range(rooms)); heapq.heapify(free); busy = []; out = []
    for pid, arrival, duration in requests:
        while busy and busy[0][0] <= arrival:
            _, room = heapq.heappop(busy); heapq.heappush(free, room)
        if free:
            room = heapq.heappop(free); start = arrival
        else:
            start, room = heapq.heappop(busy)
        heapq.heappush(busy, (start + duration, room)); out.append([pid, room, start, start + duration])
    return sorted(out)
""",
]


def tests():
    t = [{"requests": [[1, 0, 20], [2, 5, 10], [3, 15, 10], [4, 12, 5]], "rooms": 2},
         {"requests": [[7, 10, 5], [3, 10, 5], [9, 0, 10]], "rooms": 1}]
    r = rng(53)
    t.append({"requests": [], "rooms": 3})
    t.append({"requests": [[1, 0, 10], [2, 10, 10], [3, 3, 1]], "rooms": 2})
    for k in range(8):
        n = 4 + 3 * k
        ids = r.sample(range(1, 100), n)
        req = [[ids[i], r.randint(0, 60), r.randint(1, 30)] for i in range(n)]
        t.append({"requests": req, "rooms": r.randint(1, 4)})
    return t
