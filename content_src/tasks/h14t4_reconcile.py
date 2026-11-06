from kit import rng

ID = "h14t4"
NAME = "Bank Reconciliation"
LANG = "python"
PARAMS = ["bank", "ledger"]
MINUTES = 30
TAGS = ["appariement glouton", "tolérance de dates", "règles d'égalité", "dict par montant"]
IO = [("input", "array.array.integer bank"), ("input", "array.array.integer ledger"), ("output", "array.string")]
DESC = """
<p>Finance reconciles the bank statement with the accounting ledger. <code>bank</code> and <code>ledger</code> are lists of <code>[id, day, amount]</code> (integers; <code>amount</code> in cents, can be negative). Ids are unique inside each list.</p>
<p>Process the bank lines in order of <code>day</code>, then <code>id</code>. Each bank line is matched with at most one ledger entry that is <b>not matched yet</b>, has <b>exactly the same amount</b> and a day at most 3 days away (<code>|bank day - ledger day| &lt;= 3</code>). Among the candidates, take the one with the smallest day difference, then the earliest day, then the smallest id. A ledger entry is used at most once.</p>
<p>Your task is to return, in processing order, one string <code>"bank_id=ledger_id"</code> per match, then <code>"UNMATCHED_BANK ids"</code> and <code>"UNMATCHED_LEDGER ids"</code>, where <code>ids</code> are the ids without a match sorted in increasing order and joined with <code>","</code>, or <code>-</code> if there is none.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(bank, ledger):
    # write your code here
    return []
"""
SOLUTION = """
def solution(bank, ledger):
    # Les écritures du grand livre, regroupées par montant
    by_amount = {}
    for lid, d, amount in ledger:
        if amount not in by_amount:
            by_amount[amount] = []
        by_amount[amount].append([lid, d])
    used = {}

    order = []
    for bid, d, amount in bank:
        order.append([d, bid, amount])
    order.sort()

    out = []
    unmatched_bank = []
    for d, bid, amount in order:
        best = None                     # [écart, jour, id]
        for lid, ld in by_amount.get(amount, []):
            if lid in used:
                continue
            gap = abs(d - ld)
            if gap > 3:
                continue
            cand = [gap, ld, lid]
            if best is None or cand < best:
                best = cand
        if best is None:
            unmatched_bank.append(bid)
        else:
            used[best[2]] = True
            out.append(str(bid) + "=" + str(best[2]))

    unmatched_ledger = []
    for lid, d, amount in ledger:
        if lid not in used:
            unmatched_ledger.append(lid)

    def ids_text(ids):
        if len(ids) == 0:
            return "-"
        ids.sort()
        parts = []
        for x in ids:
            parts.append(str(x))
        return ",".join(parts)

    out.append("UNMATCHED_BANK " + ids_text(unmatched_bank))
    out.append("UNMATCHED_LEDGER " + ids_text(unmatched_ledger))
    return out
"""
MUTANTS = [
    SOLUTION.replace("            if gap > 3:", "            if gap >= 3:"),
    SOLUTION.replace("            cand = [gap, ld, lid]", "            cand = [gap, lid, ld]"),
    SOLUTION.replace("        order.append([d, bid, amount])\n    order.sort()", "        order.append([d, bid, amount])"),
    SOLUTION.replace("            gap = abs(d - ld)", "            gap = d - ld"),
]


def tests():
    t = [{"bank": [[1, 10, 5000], [2, 9, -1200], [3, 10, 5000], [4, 20, 777], [5, 15, 5000]],
          "ledger": [[100, 8, 5000], [101, 12, 5000], [102, 11, 5000], [103, 9, -1200], [104, 25, 777], [105, 13, 5000]]},
         {"bank": [[7, 5, 100], [8, 5, 100]], "ledger": [[1, 7, 100], [2, 3, 100], [3, 2, 100]]},
         {"bank": [], "ledger": [[1, 1, 1]]}]
    r = rng(4144)
    for k in range(9):
        nb = r.randint(3, 30) if k < 8 else 3000
        bank = [[i + 1, r.randint(0, 30 if k < 8 else 400), r.choice([100, 250, -250, 999, 5000])] for i in range(nb)]
        ledger = [[200 + i, max(0, b[1] + r.randint(-4, 4)), b[2]] for i, b in enumerate(bank) if r.random() < 0.8]
        ledger += [[900 + i, r.randint(0, 30), r.choice([100, 250, 7])] for i in range(r.randint(0, 5))]
        r.shuffle(bank)
        t.append({"bank": bank, "ledger": ledger})
    return t
