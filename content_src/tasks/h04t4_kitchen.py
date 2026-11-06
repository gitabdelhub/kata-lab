from kit import rng

ID = "h04t4"
NAME = "Kitchen Dispatch Simulator"
LANG = "python"
PARAMS = ["cooks", "events"]
MINUTES = 30
TAGS = ["simulation par événements", "priorités", "annulations", "ordre des égalités"]
IO = [("input", "integer cooks"), ("input", "array.string events"), ("output", "array.array.integer")]
DESC = """
<p>A dark kitchen has <code>cooks</code> cooks, numbered from 1. You are given <code>events</code>, a list of strings sorted by time (an integer number of minutes):</p>
<ul><li><code>"t ORDER id duration vip"</code>: order <code>id</code> arrives at time <code>t</code>; it takes <code>duration</code> minutes to cook; <code>vip</code> is <code>1</code> for a VIP order, else <code>0</code>.</li>
<li><code>"t CANCEL id"</code>: the customer cancels order <code>id</code> at time <code>t</code>.</li></ul>
<p>Simulate the kitchen:</p>
<ul><li>Every cook is free at time 0. A cook who starts an order at time <code>s</code> is busy until <code>s + duration</code> and is free again at that exact time.</li>
<li>As soon as a cook is free and an order is waiting, the cook starts an order immediately. The waiting order chosen is: VIP orders first, then the earliest arrival, then the smallest id. The cook chosen is the one who has been free for the longest time (earliest time at which they became free), then the smallest number.</li>
<li>A cancelled order that is still waiting is removed from the queue. A cancelled order that is being cooked is stopped: its cook is free at the time of the cancellation. Cancelling an order that is finished, already cancelled or unknown does nothing.</li>
<li>At a given time, first the cooks who finish at that time become free, then the events of that time are applied in the order of the list, and only then cooks pick orders.</li></ul>
<p>Your task is to return, for every order sorted by id, <code>[id, cook, start, end]</code>: the cook who cooked it and the times when cooking started and ended. Use <code>-1</code> for <code>cook</code>, <code>start</code> and <code>end</code> when the order was cancelled before starting, and <code>-1</code> for <code>end</code> only when it was cancelled while being cooked.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(cooks, events):
    # write your code here
    return []
"""
SOLUTION = """
def solution(cooks, events):
    free_since = {}              # cuisinier libre -> depuis quand
    for c in range(1, cooks + 1):
        free_since[c] = 0
    busy = {}                    # cuisinier occupé -> [id de la commande, heure de fin]
    waiting = []                 # [priorité (0 = VIP), arrivée, id, durée]
    result = {}                  # id -> [cuisinier, début, fin]
    i = 0
    while True:
        # Prochain instant : prochain événement ou prochaine fin de cuisson
        t = None
        if i < len(events):
            t = int(events[i].split()[0])
        for c in busy:
            if t is None or busy[c][1] < t:
                t = busy[c][1]
        if t is None:
            break
        # 1. Les cuisiniers qui finissent à t deviennent libres
        done = []
        for c in busy:
            if busy[c][1] <= t:
                done.append(c)
        for c in done:
            free_since[c] = busy[c][1]
            del busy[c]
        # 2. Les événements de l'instant t, dans l'ordre de la liste
        while i < len(events) and int(events[i].split()[0]) == t:
            p = events[i].split()
            i += 1
            oid = int(p[2])
            if p[1] == "ORDER":
                prio = 0 if p[4] == "1" else 1
                waiting.append([prio, t, oid, int(p[3])])
                result[oid] = [-1, -1, -1]
            else:
                removed = False
                for w in waiting:
                    if w[2] == oid:
                        waiting.remove(w)
                        removed = True
                        break
                if not removed:
                    for c in busy:
                        if busy[c][0] == oid:
                            result[oid][2] = -1
                            free_since[c] = t
                            del busy[c]
                            break
        # 3. Les cuisiniers libres prennent des commandes
        while len(waiting) > 0 and len(busy) < cooks:
            waiting.sort()
            w = waiting.pop(0)
            best = None
            for c in range(1, cooks + 1):
                if c in busy:
                    continue
                if best is None or free_since[c] < free_since[best]:
                    best = c
            busy[best] = [w[2], t + w[3]]
            result[w[2]] = [best, t, t + w[3]]
    out = []
    for oid in sorted(result):
        out.append([oid, result[oid][0], result[oid][1], result[oid][2]])
    return out
"""
MUTANTS = [
    SOLUTION.replace("prio = 0 if p[4] == \"1\" else 1", "prio = 0"),
    SOLUTION.replace("if best is None or free_since[c] < free_since[best]:", "if best is None:"),
    SOLUTION.replace("                            free_since[c] = t\n                            del busy[c]\n", ""),
    SOLUTION.replace("for c in range(1, cooks + 1):\n                if c in busy:", "for c in range(cooks, 0, -1):\n                if c in busy:"),
    SOLUTION.replace("waiting.append([prio, t, oid, int(p[3])])", "waiting.append([prio, oid, t, int(p[3])])").replace("busy[best] = [w[2], t + w[3]]\n            result[w[2]] = [best, t, t + w[3]]", "busy[best] = [w[1], t + w[3]]\n            result[w[1]] = [best, t, t + w[3]]"),
]


def tests():
    t = [{"cooks": 2, "events": ["0 ORDER 1 10 0", "0 ORDER 2 5 0", "1 ORDER 3 4 0", "2 ORDER 4 6 1", "3 CANCEL 3", "5 ORDER 5 1 0",
                                 "8 CANCEL 1", "20 CANCEL 2"]},
         {"cooks": 1, "events": ["0 ORDER 7 3 0", "3 ORDER 8 2 0", "3 ORDER 6 2 1", "4 CANCEL 6", "4 ORDER 9 0 0", "9 CANCEL 42"]},
         {"cooks": 3, "events": []}]
    r = rng(4044)
    for k in range(9):
        ev, tt, ids = [], 0, []
        n = r.randint(4, 40) if k < 8 else 1500
        for j in range(n):
            tt += r.choice([0, 0, 1, 2, 5])
            if ids and r.random() < 0.2:
                ev.append(f"{tt} CANCEL {r.choice(ids + [999999])}")
            else:
                oid = len(ids) + 1 + r.randint(0, 1) * 1000
                while oid in ids:
                    oid += 1
                ids.append(oid)
                ev.append(f"{tt} ORDER {oid} {r.choice([0, 1, 3, 5, 8])} {1 if r.random() < 0.25 else 0}")
        t.append({"cooks": r.randint(1, 4), "events": ev})
    return t
