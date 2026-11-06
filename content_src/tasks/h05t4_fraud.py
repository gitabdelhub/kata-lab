from kit import rng

ID = "h05t4"
NAME = "Card Fraud Rules"
LANG = "python"
PARAMS = ["transactions"]
MINUTES = 30
TAGS = ["fenêtres glissantes", "plusieurs règles", "moyenne des transactions précédentes", "état par carte"]
IO = [("input", "array.string transactions"), ("output", "array.string")]
DESC = """
<p>You are given <code>transactions</code>, a list of strings <code>"tx_id,card,time,amount,country"</code> sorted by <code>time</code> (an integer number of seconds; several transactions can share the same time). <code>amount</code> is a number with up to 2 decimals.</p>
<p>A transaction is checked against three rules. Each rule only looks at the <b>earlier</b> transactions of the <b>same card</b> (earlier in the list), including transactions that were flagged:</p>
<ul><li><code>VELOCITY</code>: the card already has at least 3 transactions with a time in <code>[time - 60, time]</code>.</li>
<li><code>AMOUNT</code>: the card already has at least 3 transactions, and the amount is strictly greater than 5 times the average amount of <b>all</b> its earlier transactions.</li>
<li><code>TRAVEL</code>: the card has an earlier transaction in a <b>different</b> country with a time in <code>[time - 1800, time]</code>.</li></ul>
<p>Your task is to return, in the order of the input, one string <code>"tx_id:RULES"</code> for each transaction that breaks at least one rule, where <code>RULES</code> are the names of the broken rules sorted alphabetically and joined with <code>+</code> (for example <code>"t9:AMOUNT+TRAVEL"</code>).</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(transactions):
    # write your code here
    return []
"""
SOLUTION = """
def solution(transactions):
    history = {}     # carte -> liste de [time, amount, country] des transactions précédentes
    total = {}       # carte -> somme des montants précédents
    out = []
    for line in transactions:
        tx_id, card, time, amount, country = line.split(",")
        time = int(time)
        amount = float(amount)
        if card not in history:
            history[card] = []
            total[card] = 0.0
        past = history[card]

        rules = []
        # AMOUNT : au moins 3 transactions avant, et plus de 5 fois la moyenne
        if len(past) >= 3 and amount > 5 * (total[card] / len(past)):
            rules.append("AMOUNT")
        # TRAVEL et VELOCITY : on regarde les transactions récentes (on part de la fin)
        recent = 0
        travel = False
        j = len(past) - 1
        while j >= 0 and past[j][0] >= time - 1800:
            if past[j][0] >= time - 60:
                recent += 1
            if past[j][2] != country:
                travel = True
            j -= 1
        if travel:
            rules.append("TRAVEL")
        if recent >= 3:
            rules.append("VELOCITY")

        if len(rules) > 0:
            rules.sort()
            out.append(tx_id + ":" + "+".join(rules))
        past.append([time, amount, country])
        total[card] += amount
    return out
"""
MUTANTS = [
    SOLUTION.replace("if len(past) >= 3 and amount > 5", "if len(past) >= 3 and amount >= 5"),
    SOLUTION.replace("            if past[j][0] >= time - 60:", "            if past[j][0] > time - 60:"),
    SOLUTION.replace("        past.append([time, amount, country])\n        total[card] += amount", "        if len(rules) == 0:\n            past.append([time, amount, country])\n            total[card] += amount"),
    SOLUTION.replace("if recent >= 3:", "if recent > 3:"),
    SOLUTION.replace("j = len(past) - 1\n        while j >= 0 and past[j][0] >= time - 1800:", "j = len(past) - 1\n        while j >= 0 and past[j][0] >= time - 60:"),
]


def tests():
    t = [{"transactions": ["t1,A,0,10,MA", "t2,A,20,12.5,MA", "t3,A,40,9,MA", "t4,A,60,80,MA", "t5,B,100,5,FR", "t6,A,1000,200,ES",
                           "t7,B,2000,5,MA", "t8,A,2800,30,MA", "t9,A,2830,900,FR"]},
         {"transactions": ["x1,C,0,1,SN", "x2,C,0,1,SN", "x3,C,0,1,SN", "x4,C,0,5,SN", "x5,C,0,5.01,SN", "x6,C,61,3,SN"]},
         {"transactions": []}]
    r = rng(4054)
    for k in range(9):
        tx, tt = [], 0
        n = r.randint(5, 40) if k < 8 else 4000
        for i in range(n):
            tt += r.choice([0, 5, 20, 30, 60, 61, 300, 1799, 2000])
            tx.append(f"t{i + 1},{r.choice('ABCD')},{tt},{r.choice([3, 10, 12.5, 20, 49.99, 150, 900])},{r.choice(['MA', 'MA', 'MA', 'FR', 'SN'])}")
        t.append({"transactions": tx})
    return t
