from kit import rng

ID = "h12t4"
NAME = "Price History Lookups"
LANG = "python"
PARAMS = ["changes", "queries"]
MINUTES = 35
TAGS = ["recherche binaire (bisect)", "historique trié", "doublons corrigés", "intervalle de temps", "beaucoup de requêtes"]
IO = [("input", "array.string changes"), ("input", "array.string queries"), ("output", "array.string")]
DESC = """
<p><code>changes</code> is the price log of a shop, a list of strings <code>"product,time,price"</code> (integers), <b>not sorted</b>. A price is in force from its time until the next change of the same product. When the same product has several entries with the same time, the entry that appears <b>last</b> in the list is the right one.</p>
<p>Answer each query of <code>queries</code> with a string:</p>
<ul><li><code>"PRICE product t"</code>: the price in force at time <code>t</code> (the latest change at or before <code>t</code>), or <code>"-1"</code> if there is none.</li>
<li><code>"MIN product t1 t2"</code> (<code>t1 &lt;= t2</code>): the lowest price in force at any moment from <code>t1</code> to <code>t2</code> included, that is the price in force at <code>t1</code> and the prices of the changes made after <code>t1</code> and up to <code>t2</code>. <code>"-1"</code> if no price is in force at any moment of that period.</li>
<li><code>"CHANGES product t1 t2"</code>: the number of <b>real</b> changes with a time from <code>t1</code> to <code>t2</code> included. A change is real when its price differs from the price in force just before it; the very first price of a product is a real change.</li></ul>
<p>There can be up to 15 000 changes and 15 000 queries: scanning the whole log for every query is too slow.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(changes, queries):
    # write your code here
    return []
"""
SOLUTION = """
import bisect


def solution(changes, queries):
    # 1. Dernière valeur pour chaque (produit, heure)
    last = {}
    for line in changes:
        product, time, price = line.split(",")
        last[(product, int(time))] = int(price)
    # 2. Pour chaque produit : heures triées et prix correspondants
    times, prices = {}, {}
    for product, time in sorted(last):
        if product not in times:
            times[product] = []
            prices[product] = []
        times[product].append(time)
        prices[product].append(last[(product, time)])

    out = []
    for q in queries:
        p = q.split()
        product = p[1]
        ts = times.get(product, [])
        ps = prices.get(product, [])
        if p[0] == "PRICE":
            i = bisect.bisect_right(ts, int(p[2])) - 1      # dernier changement <= t
            out.append(str(ps[i]) if i >= 0 else "-1")
        elif p[0] == "MIN":
            t1, t2 = int(p[2]), int(p[3])
            i = bisect.bisect_right(ts, t1) - 1             # prix en vigueur à t1
            if i < 0:
                i = 0
            best = None
            while i < len(ts) and ts[i] <= t2:
                if best is None or ps[i] < best:
                    best = ps[i]
                i += 1
            out.append(str(best) if best is not None else "-1")
        else:
            t1, t2 = int(p[2]), int(p[3])
            i = bisect.bisect_left(ts, t1)
            count = 0
            while i < len(ts) and ts[i] <= t2:
                if i == 0 or ps[i] != ps[i - 1]:
                    count += 1
                i += 1
            out.append(str(count))
    return out
"""
MUTANTS = [
    SOLUTION.replace("i = bisect.bisect_right(ts, int(p[2])) - 1      # dernier changement <= t", "i = bisect.bisect_left(ts, int(p[2])) - 1"),
    SOLUTION.replace("            i = bisect.bisect_right(ts, t1) - 1             # prix en vigueur à t1\n            if i < 0:\n                i = 0", "            i = bisect.bisect_left(ts, t1)"),
    SOLUTION.replace("                if i == 0 or ps[i] != ps[i - 1]:", "                if True:"),
    SOLUTION.replace("        last[(product, int(time))] = int(price)", "        if (product, int(time)) not in last:\n            last[(product, int(time))] = int(price)"),
]


def tests():
    t = [{"changes": ["A,10,100", "A,5,120", "A,20,100", "A,30,90", "A,30,95", "B,0,7"],
          "queries": ["PRICE A 4", "PRICE A 5", "PRICE A 29", "PRICE A 31", "MIN A 12 25", "MIN A 0 4", "MIN A 25 40", "CHANGES A 0 100",
                      "CHANGES A 15 25", "PRICE C 1", "MIN B 3 3"]},
         {"changes": ["X,1,5", "X,2,5", "X,3,4"], "queries": ["CHANGES X 1 3", "CHANGES X 2 2", "MIN X 2 2", "MIN X 0 1", "MIN X 0 0"]}]
    r = rng(4124)
    for k in range(9):
        big = k == 8
        prods = ["A", "B", "C", "D"]
        ch = [f"{r.choice(prods)},{r.randint(0, 50000 if big else 60)},{r.choice([90, 95, 100, 120])}" for _ in range(15000 if big else r.randint(3, 30))]
        qs = []
        for _ in range(15000 if big else r.randint(5, 30)):
            a = r.randint(0, 50000 if big else 60)
            b = a + r.choice([0, 1, 5, 20])
            kind = r.choice(["PRICE", "PRICE", "MIN", "CHANGES"])
            qs.append(f"PRICE {r.choice(prods)} {a}" if kind == "PRICE" else f"{kind} {r.choice(prods + ['Z'])} {a} {b}")
        t.append({"changes": ch, "queries": qs})
    return t
