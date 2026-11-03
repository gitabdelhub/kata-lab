from kit import rng

ID = "e05t4"
NAME = "Card Velocity Alerts"
LANG = "python"
PARAMS = ["transactions", "max_count", "window"]
MINUTES = 22
TAGS = ["fenêtre glissante", "deux pointeurs", "tri par carte", "bornes incluses"]
IO = [("input", "array.array.string transactions"), ("input", "integer max_count"), ("input", "integer window"), ("output", "array.array.string")]
DESC = """
<p>The fraud team blocks cards that are used too often in a short time. You are given <code>transactions</code>, a list of <code>[card_id, timestamp, status]</code> where <code>timestamp</code> is a number of seconds written as a string and <code>status</code> is <code>"approved"</code> or <code>"declined"</code>. Transactions are <b>not sorted</b>.</p>
<p>Both approved and declined transactions count. A card triggers an alert as soon as it has <b>more than</b> <code>max_count</code> transactions inside a time window of <code>window</code> seconds, which means: there are <code>max_count + 1</code> transactions of the card whose timestamps <code>t1 &lt;= ... &lt;= tk</code> satisfy <code>tk - t1 &lt; window</code>.</p>
<p>Your task is to return, for every card that triggers an alert, a pair <code>[card_id, alert_at]</code>, where <code>alert_at</code> is the timestamp (as a string) of the transaction that triggers the <b>first</b> alert of the card. Sort by <code>alert_at</code> as a number, then by <code>card_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>With <code>max_count = 2</code> and <code>window = 60</code>, card <code>c1</code> has 3 transactions at <code>100</code>, <code>130</code> and <code>159</code>: <code>159 - 100 &lt; 60</code>, so the alert is at <code>159</code>. Card <code>c2</code> has 3 transactions but <code>160 - 100</code> is not less than <code>60</code>.</p>
"""
STARTER = """
def solution(transactions, max_count, window):
    # write your code here
    return []
"""
SOLUTION = """
def solution(transactions, max_count, window):
    by = {}
    for card, ts, _ in transactions:
        by.setdefault(card, []).append(int(ts))
    out = []
    for card, times in by.items():
        times.sort()
        left = 0
        for right, t in enumerate(times):
            while t - times[left] >= window:
                left += 1
            if right - left + 1 > max_count:
                out.append((t, card))
                break
    out.sort()
    return [[card, str(t)] for t, card in out]
"""
MUTANTS = [
    """
def solution(transactions, max_count, window):
    by = {}
    for card, ts, st in transactions:
        if st == "approved":
            by.setdefault(card, []).append(int(ts))
    out = []
    for card, times in by.items():
        times.sort(); left = 0
        for right, t in enumerate(times):
            while t - times[left] >= window: left += 1
            if right - left + 1 > max_count:
                out.append((t, card)); break
    out.sort()
    return [[c, str(t)] for t, c in out]
""",
    """
def solution(transactions, max_count, window):
    by = {}
    for card, ts, st in transactions:
        by.setdefault(card, []).append(int(ts))
    out = []
    for card, times in by.items():
        times.sort(); left = 0
        for right, t in enumerate(times):
            while t - times[left] > window: left += 1
            if right - left + 1 > max_count:
                out.append((t, card)); break
    out.sort()
    return [[c, str(t)] for t, c in out]
""",
    """
def solution(transactions, max_count, window):
    by = {}
    for card, ts, st in transactions:
        by.setdefault(card, []).append(ts)
    out = []
    for card, times in by.items():
        times.sort(); left = 0
        for right, t in enumerate(times):
            while int(t) - int(times[left]) >= window: left += 1
            if right - left + 1 > max_count:
                out.append((t, card)); break
    out.sort()
    return [[c, t] for t, c in out]
""",
]


def tests():
    t = [{"transactions": [["c1", "130", "approved"], ["c2", "100", "approved"], ["c1", "100", "declined"], ["c2", "160", "approved"], ["c1", "159", "approved"], ["c2", "130", "declined"]],
          "max_count": 2, "window": 60},
         {"transactions": [["b", "5", "approved"], ["a", "9", "approved"], ["a", "10", "approved"], ["b", "5", "approved"], ["z", "1000", "approved"]], "max_count": 1, "window": 1},
         {"transactions": [["x", "95", "approved"], ["x", "100", "approved"], ["x", "1000", "approved"], ["y", "200", "approved"], ["y", "210", "declined"]], "max_count": 1, "window": 10}]
    r = rng(504)
    for _ in range(8):
        tx = [[f"c{r.randint(1, 5)}", str(r.randint(0, 3000 if r.random() < 0.5 else 300)), r.choice(["approved", "declined"])] for _ in range(r.randint(3, 25))]
        t.append({"transactions": tx, "max_count": r.randint(1, 3), "window": r.choice([30, 60, 120, 600])})
    return t
