from kit import rng

ID = "h20t4"
NAME = "Token Bucket Limiter with Plans"
LANG = "python"
PARAMS = ["plans", "requests"]
MINUTES = 35
TAGS = ["seau à jetons", "recharge en continu", "changement de plan", "temps d'attente arrondi au-dessus", "calcul entier"]
IO = [("input", "dictionary plans"), ("input", "array.string requests"), ("output", "array.string")]
DESC = """
<p>An API gateway limits its clients with token buckets. <code>plans</code> maps a plan name to <code>[capacity, rate]</code>: a bucket holds at most <code>capacity</code> tokens and gains <code>rate</code> tokens per second (integers). <code>requests</code> is a list of strings sorted by time (integer seconds):</p>
<ul><li><code>"t REGISTER client plan"</code>: creates the client with a <b>full</b> bucket. Returns <code>"OK"</code>, or <code>"EXISTS"</code> if the client already exists (nothing changes).</li>
<li><code>"t CALL client cost"</code>: the call is accepted if the bucket has at least <code>cost</code> tokens; they are removed and the answer is <code>"ACCEPT remaining"</code>. Otherwise the answer is <code>"REJECT wait"</code>, where <code>wait</code> is the smallest whole number of seconds after which the bucket would have enough tokens if nothing else happened, or <code>"REJECT never"</code> if <code>cost</code> is greater than the capacity or if the plan earns no token (<code>rate</code> = 0). A rejected call removes nothing.</li>
<li><code>"t PLAN client plan"</code>: switches the client to another plan from time <code>t</code>. The tokens earned until <code>t</code> are computed with the old plan, then the bucket keeps its tokens, cut down to the new capacity if needed. Returns the number of tokens after the switch.</li></ul>
<p>Before any operation on a client at time <code>t</code>, its bucket is refilled: <code>tokens = min(capacity, tokens + (t - last) * rate)</code>, where <code>last</code> is the time of its previous refill (its registration for the first one). An operation on an unknown client returns <code>"UNKNOWN"</code>.</p>
<p>Your task is to return one string per request.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(plans, requests):
    # write your code here
    return []
"""
SOLUTION = """
def solution(plans, requests):
    clients = {}      # client -> [plan, jetons, dernière recharge]
    out = []
    for line in requests:
        p = line.split()
        t, op, client = int(p[0]), p[1], p[2]
        if op == "REGISTER":
            if client in clients:
                out.append("EXISTS")
            else:
                clients[client] = [p[3], plans[p[3]][0], t]
                out.append("OK")
            continue
        if client not in clients:
            out.append("UNKNOWN")
            continue
        c = clients[client]
        capacity, rate = plans[c[0]]
        # Recharge jusqu'à t avec le plan actuel
        c[1] = min(capacity, c[1] + (t - c[2]) * rate)
        c[2] = t
        if op == "CALL":
            cost = int(p[3])
            if c[1] >= cost:
                c[1] -= cost
                out.append("ACCEPT " + str(c[1]))
            elif cost > capacity or rate == 0:
                out.append("REJECT never")
            else:
                missing = cost - c[1]
                wait = (missing + rate - 1) // rate       # division arrondie au-dessus
                out.append("REJECT " + str(wait))
        elif op == "PLAN":
            c[0] = p[3]
            new_capacity = plans[p[3]][0]
            if c[1] > new_capacity:
                c[1] = new_capacity
            out.append(str(c[1]))
    return out
"""
MUTANTS = [
    SOLUTION.replace("                wait = (missing + rate - 1) // rate       # division arrondie au-dessus", "                wait = missing // rate"),
    SOLUTION.replace("        c[1] = min(capacity, c[1] + (t - c[2]) * rate)", "        c[1] = c[1] + (t - c[2]) * rate"),
    SOLUTION.replace("            if c[1] >= cost:\n                c[1] -= cost\n                out.append(\"ACCEPT \" + str(c[1]))\n            elif cost > capacity or rate == 0:", "            if cost > capacity or rate == 0:\n                out.append(\"REJECT never\")\n            elif c[1] >= cost:\n                c[1] -= cost\n                out.append(\"ACCEPT \" + str(c[1]))\n            elif False:"),
    SOLUTION.replace("            if c[1] > new_capacity:\n                c[1] = new_capacity\n", ""),
    SOLUTION.replace("                clients[client] = [p[3], plans[p[3]][0], t]", "                clients[client] = [p[3], 0, t]"),
]


def tests():
    plans = {"free": [10, 1], "pro": [100, 5], "burst": [50, 0]}
    t = [{"plans": plans, "requests": ["0 REGISTER ana free", "0 CALL ana 4", "1 CALL ana 7", "2 CALL ana 8", "5 CALL ana 30", "6 PLAN ana pro",
                                       "6 CALL ana 30", "10 CALL ana 30", "10 PLAN ana free", "11 CALL bob 1", "11 REGISTER ana pro", "20 PLAN ana burst",
                                       "30 CALL ana 11"]},
         {"plans": {"x": [3, 2], "y": [0, 0]}, "requests": ["0 REGISTER a x", "0 CALL a 3", "0 CALL a 3", "1 CALL a 3", "1 CALL a 0", "2 CALL a 3",
                                                            "2 REGISTER b y", "3 CALL b 0", "3 CALL b 1"]}]
    r = rng(4204)
    for _ in range(9):
        reqs, tt = [], 0
        for c in ["ana", "bob", "cyd"][: r.randint(1, 3)]:
            reqs.append(f"0 REGISTER {c} {r.choice(['free', 'pro', 'burst'])}")
        for _ in range(r.randint(8, 60)):
            tt += r.choice([0, 0, 1, 2, 7])
            c = r.choice(["ana", "bob", "cyd", "dan"])
            op = r.choice(["CALL"] * 6 + ["PLAN", "REGISTER"])
            if op == "CALL":
                reqs.append(f"{tt} CALL {c} {r.choice([0, 1, 3, 9, 10, 11, 40, 120])}")
            else:
                reqs.append(f"{tt} {op} {c} {r.choice(['free', 'pro', 'burst'])}")
        t.append({"plans": plans, "requests": reqs})
    return t
