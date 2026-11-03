from kit import rng

ID = "e04t4"
NAME = "Courier Shift Hours"
LANG = "python"
PARAMS = ["shifts"]
MINUTES = 20
TAGS = ["fusion d'intervalles", "tri", "parsing HH:MM", "passage de minuit"]
IO = [("input", "array.string shifts"), ("output", "array.array.string")]
DESC = """
<p>Couriers declare their shifts in a planning tool. You are given <code>shifts</code>, a list of strings of the form <code>"courier_id HH:MM-HH:MM"</code> (for example <code>"c7 08:00-12:30"</code>). All shifts are in the same day.</p>
<ul><li>A shift that ends at or before its start time goes past midnight: it ends at that time on the <b>next</b> day (for example <code>"22:00-01:00"</code> lasts 3 hours).</li><li>A courier can declare overlapping or touching shifts: time that is covered by several shifts is counted <b>once</b>.</li></ul>
<p>Your task is to return, for each courier, a pair <code>[courier_id, worked]</code> where <code>worked</code> is the total time worked formatted as <code>"HH:MM"</code> (hours can be greater than 24). Sort by worked time, longest first, then by <code>courier_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p><code>c1</code> works from <code>08:00</code> to <code>13:00</code> (the two first shifts overlap) and from <code>14:00</code> to <code>15:00</code>: 6 hours.</p>
"""
STARTER = """
def solution(shifts):
    # write your code here
    return []
"""
SOLUTION = """
def solution(shifts):
    by = {}
    for s in shifts:
        cid, span = s.split()
        a, b = span.split("-")
        start = int(a[:2]) * 60 + int(a[3:])
        end = int(b[:2]) * 60 + int(b[3:])
        if end <= start:
            end += 24 * 60
        by.setdefault(cid, []).append((start, end))
    out = []
    for cid, iv in by.items():
        iv.sort()
        total, cur_s, cur_e = 0, iv[0][0], iv[0][1]
        for s, e in iv[1:]:
            if s <= cur_e:
                cur_e = max(cur_e, e)
            else:
                total += cur_e - cur_s
                cur_s, cur_e = s, e
        total += cur_e - cur_s
        out.append((cid, total))
    out.sort(key=lambda x: (-x[1], x[0]))
    return [[cid, f"{m // 60:02d}:{m % 60:02d}"] for cid, m in out]
"""
MUTANTS = [
    """
def solution(shifts):
    by = {}
    for s in shifts:
        cid, span = s.split()
        a, b = span.split("-")
        st = int(a[:2]) * 60 + int(a[3:]); en = int(b[:2]) * 60 + int(b[3:])
        if en <= st: en += 1440
        by[cid] = by.get(cid, 0) + en - st
    out = sorted(by.items(), key=lambda x: (-x[1], x[0]))
    return [[c, f"{m // 60:02d}:{m % 60:02d}"] for c, m in out]
""",
    """
def solution(shifts):
    by = {}
    for s in shifts:
        cid, span = s.split()
        a, b = span.split("-")
        st = int(a[:2]) * 60 + int(a[3:]); en = int(b[:2]) * 60 + int(b[3:])
        by.setdefault(cid, []).append((st, en))
    out = []
    for cid, iv in by.items():
        iv.sort(); tot = 0; cs, ce = iv[0]
        for s, e in iv[1:]:
            if s <= ce: ce = max(ce, e)
            else: tot += ce - cs; cs, ce = s, e
        tot += ce - cs
        out.append((cid, tot))
    out.sort(key=lambda x: (-x[1], x[0]))
    return [[c, f"{m // 60:02d}:{m % 60:02d}"] for c, m in out]
""",
    """
def solution(shifts):
    by = {}
    for s in shifts:
        cid, span = s.split()
        a, b = span.split("-")
        st = int(a[:2]) * 60 + int(a[3:]); en = int(b[:2]) * 60 + int(b[3:])
        if en <= st: en += 1440
        by.setdefault(cid, []).append((st, en))
    out = []
    for cid, iv in by.items():
        tot = 0; cs, ce = iv[0]
        for s, e in iv[1:]:
            if s <= ce: ce = max(ce, e)
            else: tot += ce - cs; cs, ce = s, e
        tot += ce - cs
        out.append((cid, tot))
    out.sort(key=lambda x: (-x[1], x[0]))
    return [[c, f"{m // 60:02d}:{m % 60:02d}"] for c, m in out]
""",
]


def tests():
    t = [{"shifts": ["c1 08:00-12:00", "c2 09:00-11:30", "c1 10:00-13:00", "c1 14:00-15:00"]},
         {"shifts": ["k9 22:00-01:00", "k9 00:30-02:00", "a1 06:00-09:00", "a1 09:00-10:00"]},
         {"shifts": ["x 10:00-10:00"]},
         {"shifts": ["b 12:00-13:00", "a 12:00-13:00", "b 12:15-12:45"]}]
    r = rng(404)
    for _ in range(7):
        s = []
        for _ in range(r.randint(1, 9)):
            h1, m1 = r.randint(0, 23), r.choice([0, 15, 30, 45])
            h2, m2 = (h1 + r.randint(0, 6)) % 24, r.choice([0, 15, 30, 45])
            s.append(f"c{r.randint(1, 4)} {h1:02d}:{m1:02d}-{h2:02d}:{m2:02d}")
        t.append({"shifts": s})
    return t
