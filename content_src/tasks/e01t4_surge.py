from kit import rng

ID = "e01t4"
NAME = "Surge Window Detector"
LANG = "python"
PARAMS = ["requests", "window"]
MINUTES = 20
TAGS = ["comptage", "division", "dict", "bornes"]
IO = [("input", "array.integer requests"), ("input", "integer window"), ("output", "array.array.integer")]
DESC = """
<p>The pricing team turns on "surge pricing" when demand is unusually high. You are given the timestamps (in seconds, not sorted) of all ride requests of one day in <code>requests</code>, and a window size <code>window</code> in seconds.</p>
<p>Time is split into aligned windows <code>[0, window)</code>, <code>[window, 2 * window)</code>, and so on. Consider every window from the one that contains the <b>smallest</b> timestamp to the one that contains the <b>largest</b> timestamp, both included, <b>including windows with no request</b>. The <b>average demand</b> is the number of requests divided by the number of these windows.</p>
<p>A window is a <b>surge window</b> if its number of requests is <b>strictly greater</b> than twice the average demand.</p>
<p>Your task is to return the list of surge windows as pairs <code>[start, end]</code>, where <code>end = start + window</code>, sorted by <code>start</code>. If <code>requests</code> is empty, return an empty list.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>The windows go from <code>[0, 600)</code> to <code>[3000, 3600)</code>: 6 windows for 9 requests, so the average is <code>1.5</code>. Only <code>[600, 1200)</code> has more than <code>3</code> requests.</p>
"""
STARTER = """
def solution(requests, window):
    # write your code here
    return []
"""
SOLUTION = """
def solution(requests, window):
    if not requests:
        return []
    counts = {}
    for ts in requests:
        k = ts // window
        counts[k] = counts.get(k, 0) + 1
    first, last = min(counts), max(counts)
    n_windows = last - first + 1
    avg = len(requests) / n_windows
    return [[k * window, (k + 1) * window] for k in range(first, last + 1) if counts.get(k, 0) > 2 * avg]
"""
MUTANTS = [
    """
def solution(requests, window):
    if not requests:
        return []
    counts = {}
    for ts in requests:
        counts[ts // window] = counts.get(ts // window, 0) + 1
    avg = len(requests) / len(counts)
    return [[k * window, (k + 1) * window] for k in sorted(counts) if counts[k] > 2 * avg]
""",
    """
def solution(requests, window):
    if not requests:
        return []
    counts = {}
    for ts in requests:
        counts[ts // window] = counts.get(ts // window, 0) + 1
    first, last = min(counts), max(counts)
    avg = len(requests) // (last - first + 1)
    return [[k * window, (k + 1) * window] for k in range(first, last + 1) if counts.get(k, 0) > 2 * avg]
""",
    """
def solution(requests, window):
    if not requests:
        return []
    counts = {}
    for ts in requests:
        counts[ts // window] = counts.get(ts // window, 0) + 1
    first, last = min(counts), max(counts)
    avg = len(requests) / (last - first + 1)
    return [[k * window, (k + 1) * window] for k in range(first, last + 1) if counts.get(k, 0) >= 2 * avg]
""",
]


def tests():
    t = [{"requests": [700, 30, 610, 650, 3500, 1199, 800, 2000, 900], "window": 600},
         {"requests": [5, 5, 5, 5], "window": 600}]
    r = rng(33)
    t.append({"requests": [], "window": 60})
    t.append({"requests": [0, 1, 2, 3, 600, 1200], "window": 600})
    t.append({"requests": [0, 59, 60, 120, 121, 122, 123, 124, 125, 300], "window": 60})
    for k in range(7):
        base = r.randint(0, 5000)
        req = [base + r.randint(0, 3000) for _ in range(r.randint(1, 40))]
        if k != 3:
            hot = base + r.randint(0, 3000)
            req += [hot + r.randint(0, 50) for _ in range(r.randint(5, 20))]
        r.shuffle(req)
        t.append({"requests": req, "window": r.choice([60, 300, 600])})
    return t
