from kit import rng

ID = "h19t4"
NAME = "Ledger with Holds and Scheduled Transfers"
LANG = "python"
PARAMS = ["queries"]
MINUTES = 40
TAGS = ["système à plusieurs commandes", "réservations qui expirent", "virements planifiés", "traitement des échéances avant chaque requête", "classement"]
IO = [("input", "array.array.string queries"), ("output", "array.string")]
DESC = """
<p>Implement the ledger of a payment app. Every query starts with a timestamp (digits); queries are sorted by timestamp. Process them in order and return one string per query. All amounts are integers.</p>
<p>An account has a <b>balance</b> and can have <b>holds</b> (money reserved for a card payment). A hold created at time <code>t</code> with a <code>ttl</code> is active while the current time is lower than <code>t + ttl</code>, and stops being active from <code>t + ttl</code> on. The <b>available</b> amount of an account at a time is its balance minus its active holds.</p>
<ul>
<li><code>[t, "OPEN", acc]</code>: <code>"true"</code>, or <code>"false"</code> if the account exists.</li>
<li><code>[t, "DEPOSIT", acc, amount]</code>: adds to the balance; returns the available amount.</li>
<li><code>[t, "HOLD", acc, hold_id, amount, ttl]</code>: creates a hold if the available amount is at least <code>amount</code> and <code>hold_id</code> was never used; returns the available amount after it.</li>
<li><code>[t, "CAPTURE", hold_id]</code>: if the hold is still active, the money leaves the account (the balance decreases and the hold disappears): <code>"true"</code>; else <code>"false"</code>.</li>
<li><code>[t, "SCHEDULE", from, to, amount, delay]</code>: plans a transfer for the time <code>t + delay</code> and returns its id: <code>"transfer1"</code> for the first scheduled transfer of the whole ledger, then <code>"transfer2"</code>, and so on. Refused with <code>""</code> if an account is unknown or if <code>from</code> equals <code>to</code> (no id is used).</li>
<li><code>[t, "CANCEL", transfer_id]</code>: <code>"true"</code> if the transfer is still planned (it is removed), else <code>"false"</code>.</li>
<li><code>[t, "TOP", n]</code>: the <code>n</code> accounts with the highest total of money sent (captured holds and executed transfers), as <code>"acc(total)"</code> items joined with <code>","</code>, highest first, then by account name. All accounts are ranked, even with a total of 0.</li>
</ul>
<p>A query on an unknown account or hold, and a refused <code>HOLD</code>, returns <code>""</code>.</p>
<p><b>Before</b> processing a query at time <code>t</code>, execute every planned transfer whose time is at most <code>t</code>, in order of their time, then id number. A transfer is executed if the available amount of the sender <b>at the transfer's time</b> is at least the amount: the money moves from one balance to the other. Otherwise it fails and is dropped.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(queries):
    # write your code here
    return []
"""
SOLUTION = """
def solution(queries):
    balance = {}
    sent = {}
    holds = {}            # hold_id -> [compte, montant, fin] ; supprimé une fois capturé
    used_hold_ids = {}
    planned = []          # [heure, numéro, from, to, montant]
    counter = 0

    def available(acc, at):
        total = balance[acc]
        for hid in holds:
            a, amount, end = holds[hid]
            if a == acc and at < end:
                total -= amount
        return total

    out = []
    for q in queries:
        t, op = int(q[0]), q[1]
        # 1. Exécuter les virements arrivés à échéance
        planned.sort()
        while len(planned) > 0 and planned[0][0] <= t:
            when, num, src, dst, amount = planned.pop(0)
            if available(src, when) >= amount:
                balance[src] -= amount
                balance[dst] += amount
                sent[src] += amount
        # 2. La requête
        if op == "OPEN":
            if q[2] in balance:
                out.append("false")
            else:
                balance[q[2]] = 0
                sent[q[2]] = 0
                out.append("true")
        elif op == "DEPOSIT":
            acc = q[2]
            if acc not in balance:
                out.append("")
            else:
                balance[acc] += int(q[3])
                out.append(str(available(acc, t)))
        elif op == "HOLD":
            acc, hid, amount, ttl = q[2], q[3], int(q[4]), int(q[5])
            if acc not in balance or hid in used_hold_ids or available(acc, t) < amount:
                out.append("")
            else:
                used_hold_ids[hid] = True
                holds[hid] = [acc, amount, t + ttl]
                out.append(str(available(acc, t)))
        elif op == "CAPTURE":
            hid = q[2]
            if hid in holds and t < holds[hid][2]:
                acc, amount, end = holds[hid]
                balance[acc] -= amount
                sent[acc] += amount
                del holds[hid]
                out.append("true")
            else:
                out.append("false")
        elif op == "SCHEDULE":
            src, dst, amount, delay = q[2], q[3], int(q[4]), int(q[5])
            if src not in balance or dst not in balance or src == dst:
                out.append("")
            else:
                counter += 1
                planned.append([t + delay, counter, src, dst, amount])
                out.append("transfer" + str(counter))
        elif op == "CANCEL":
            found = None
            for p in planned:
                if "transfer" + str(p[1]) == q[2]:
                    found = p
            if found is None:
                out.append("false")
            else:
                planned.remove(found)
                out.append("true")
        elif op == "TOP":
            ranking = []
            for acc in sent:
                ranking.append((-sent[acc], acc))
            ranking.sort()
            items = []
            for neg, acc in ranking[: int(q[2])]:
                items.append(acc + "(" + str(-neg) + ")")
            out.append(",".join(items))
    return out
"""
MUTANTS = [
    SOLUTION.replace("            if available(src, when) >= amount:", "            if available(src, t) >= amount:"),
    SOLUTION.replace("            if a == acc and at < end:", "            if a == acc and at <= end:"),
    SOLUTION.replace("        planned.sort()\n", ""),
    SOLUTION.replace("            if hid in holds and t < holds[hid][2]:", "            if hid in holds:"),
    SOLUTION.replace("                balance[src] -= amount\n                balance[dst] += amount\n                sent[src] += amount", "                balance[src] -= amount\n                balance[dst] += amount"),
]


def tests():
    t = [{"queries": [["1", "OPEN", "ana"], ["1", "OPEN", "ben"], ["2", "DEPOSIT", "ana", "100"], ["3", "HOLD", "ana", "h1", "70", "10"],
                      ["4", "SCHEDULE", "ana", "ben", "50", "5"], ["5", "SCHEDULE", "ana", "ben", "30", "11"], ["8", "HOLD", "ana", "h2", "40", "5"],
                      ["12", "CAPTURE", "h1"], ["13", "TOP", "2"], ["16", "DEPOSIT", "ben", "0"], ["17", "CAPTURE", "h2"], ["17", "TOP", "5"]]},
         {"queries": [["0", "OPEN", "a"], ["0", "OPEN", "b"], ["0", "DEPOSIT", "a", "10"], ["0", "SCHEDULE", "a", "b", "10", "3"],
                      ["1", "SCHEDULE", "a", "b", "10", "2"], ["2", "CANCEL", "transfer1"], ["2", "CANCEL", "transfer1"], ["3", "SCHEDULE", "a", "a", "1", "1"],
                      ["3", "HOLD", "zz", "h", "1", "1"], ["3", "TOP", "1"], ["4", "DEPOSIT", "a", "5"], ["4", "HOLD", "b", "h9", "10", "1"],
                      ["5", "HOLD", "b", "h9", "1", "1"], ["5", "CAPTURE", "h9"]]},
         {"queries": [["0", "OPEN", "a"], ["0", "OPEN", "b"], ["0", "DEPOSIT", "a", "100"], ["0", "HOLD", "a", "h1", "80", "10"],
                      ["1", "SCHEDULE", "a", "b", "50", "4"], ["2", "SCHEDULE", "a", "b", "10", "10"], ["3", "SCHEDULE", "a", "b", "5", "1"],
                      ["6", "DEPOSIT", "b", "0"], ["7", "SCHEDULE", "a", "b", "50", "1"], ["10", "DEPOSIT", "a", "0"], ["20", "TOP", "2"]]}]
    r = rng(4194)
    accs = ["ana", "ben", "cyd"]
    for _ in range(9):
        qs, tt, n_tr, hids = [], 0, 0, []
        for a in accs[: r.randint(2, 3)]:
            qs.append([str(tt), "OPEN", a])
        for i in range(r.randint(10, 60)):
            tt += r.choice([0, 1, 2, 5])
            op = r.choice(["DEPOSIT", "DEPOSIT", "HOLD", "CAPTURE", "SCHEDULE", "SCHEDULE", "CANCEL", "TOP", "OPEN"])
            a, b = r.choice(accs), r.choice(accs)
            if op == "DEPOSIT":
                qs.append([str(tt), op, a, str(r.choice([10, 50, 100]))])
            elif op == "HOLD":
                hid = f"h{r.randint(1, 8)}"
                hids.append(hid)
                qs.append([str(tt), op, a, hid, str(r.choice([10, 30, 60])), str(r.choice([1, 3, 10]))])
            elif op == "CAPTURE":
                qs.append([str(tt), op, r.choice(hids + ["hx"])])
            elif op == "SCHEDULE":
                qs.append([str(tt), op, a, b, str(r.choice([10, 40, 80])), str(r.choice([0, 1, 4, 9]))])
                n_tr += 1
            elif op == "CANCEL":
                qs.append([str(tt), op, f"transfer{r.randint(1, n_tr + 1)}"])
            elif op == "TOP":
                qs.append([str(tt), op, str(r.randint(1, 3))])
            else:
                qs.append([str(tt), op, a])
        t.append({"queries": qs})
    return t
