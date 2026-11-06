from kit import rng

ID = "h11t4"
NAME = "Warehouse Lots with Expiry"
LANG = "python"
PARAMS = ["operations"]
MINUTES = 30
TAGS = ["premier périmé, premier sorti", "lots partiels", "pertes à la date", "ordre de traitement dans la journée"]
IO = [("input", "array.string operations"), ("output", "array.string")]
DESC = """
<p>A warehouse stores products in lots. <code>operations</code> is a list of strings sorted by day (an integer):</p>
<ul><li><code>"day RECEIVE sku lot qty expiry"</code>: a new lot of <code>qty</code> units arrives; it can be sold up to its <code>expiry</code> day included.</li>
<li><code>"day SHIP sku qty"</code>: an order asks for <code>qty</code> units. The units are taken from the lot with the earliest expiry, then (same expiry) from the lot received first, then the next lot, and so on. If there is not enough stock, ship everything that is available. Return <code>"shipped/requested"</code>, for example <code>"7/10"</code>.</li>
<li><code>"day COUNT sku"</code>: return the number of units in stock for the sku, as a string.</li></ul>
<p>Before the operations of a day are processed, every lot whose expiry is <b>before</b> that day is thrown away: its remaining units are <b>waste</b> for its sku. Days without operations do not need to be processed one by one (the result is the same).</p>
<p>Your task is to return the strings of the <code>SHIP</code> and <code>COUNT</code> operations in order, followed by one string <code>"WASTE sku units"</code> for every sku with at least one wasted unit, sorted by sku. Lots still in stock after the last operation are not waste.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(operations):
    # write your code here
    return []
"""
SOLUTION = """
def solution(operations):
    lots = {}        # sku -> liste de [expiry, ordre d'arrivée, quantité restante]
    waste = {}
    out = []
    arrival = 0
    current_day = None
    for op in operations:
        p = op.split()
        d = int(p[0])
        if d != current_day:
            current_day = d
            # Jeter les lots périmés (expiry < jour)
            for sku in lots:
                keep = []
                for lot in lots[sku]:
                    if lot[0] < d:
                        if lot[2] > 0:
                            waste[sku] = waste.get(sku, 0) + lot[2]
                    else:
                        keep.append(lot)
                lots[sku] = keep
        action, sku = p[1], p[2]
        if sku not in lots:
            lots[sku] = []
        if action == "RECEIVE":
            arrival += 1
            lots[sku].append([int(p[5]), arrival, int(p[4])])
            lots[sku].sort()
        elif action == "SHIP":
            want = int(p[3])
            shipped = 0
            for lot in lots[sku]:
                if shipped == want:
                    break
                take = min(lot[2], want - shipped)
                lot[2] -= take
                shipped += take
            out.append(str(shipped) + "/" + str(want))
        elif action == "COUNT":
            total = 0
            for lot in lots[sku]:
                total += lot[2]
            out.append(str(total))
    for sku in sorted(waste):
        if waste[sku] > 0:
            out.append("WASTE " + sku + " " + str(waste[sku]))
    return out
"""
MUTANTS = [
    SOLUTION.replace("                    if lot[0] < d:", "                    if lot[0] <= d:"),
    SOLUTION.replace("            lots[sku].append([int(p[5]), arrival, int(p[4])])\n            lots[sku].sort()", "            lots[sku].append([int(p[5]), arrival, int(p[4])])"),
    SOLUTION.replace("            lots[sku].sort()", "            lots[sku].sort(reverse=True)"),
    SOLUTION.replace("    for sku in sorted(waste):", "    for sku in lots:\n        for lot in lots[sku]:\n            waste[sku] = waste.get(sku, 0) + lot[2]\n    for sku in sorted(waste):"),
]


def tests():
    t = [{"operations": ["1 RECEIVE milk L1 10 5", "1 RECEIVE milk L2 5 3", "2 SHIP milk 7", "3 COUNT milk", "4 COUNT milk", "4 RECEIVE milk L3 4 9",
                         "6 SHIP milk 20", "6 RECEIVE eggs E1 12 6", "7 COUNT eggs", "8 SHIP eggs 1"]},
         {"operations": ["0 RECEIVE a X 3 2", "0 RECEIVE a Y 3 2", "2 SHIP a 4", "2 COUNT a", "3 COUNT a", "3 COUNT b"]}]
    r = rng(4114)
    for k in range(9):
        ops, d = [], 0
        for i in range(r.randint(6, 60) if k < 8 else 2500):
            d += r.choice([0, 0, 1, 2, 4])
            sku = r.choice(["milk", "eggs", "bread"])
            a = r.choice(["RECEIVE", "RECEIVE", "SHIP", "SHIP", "COUNT"])
            if a == "RECEIVE":
                ops.append(f"{d} RECEIVE {sku} L{i} {r.randint(1, 20)} {d + r.choice([0, 1, 3, 7])}")
            elif a == "SHIP":
                ops.append(f"{d} SHIP {sku} {r.randint(1, 25)}")
            else:
                ops.append(f"{d} COUNT {sku}")
        t.append({"operations": ops})
    return t
