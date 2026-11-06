from kit import rng, day

ID = "h10t4"
NAME = "Prorated Subscription Invoices"
LANG = "python"
PARAMS = ["plans", "events"]
MINUTES = 35
TAGS = ["calendrier (jours par mois)", "prorata au jour près", "plusieurs événements le même jour", "arrondi entier", "datetime"]
IO = [("input", "dictionary plans"), ("input", "array.string events"), ("output", "array.string")]
DESC = """
<p><code>plans</code> gives the monthly price of each plan in cents. <code>events</code> is a list of strings <code>"YYYY-MM-DD customer ACTION"</code> or <code>"YYYY-MM-DD customer ACTION plan"</code>, sorted by date (several events can share a date; apply them in the order of the list):</p>
<ul><li><code>START plan</code>: the customer becomes active on this plan from this day included. If the customer is already active, it is the same as <code>CHANGE</code>.</li>
<li><code>CHANGE plan</code>: from this day included, the customer is on the new plan. Ignored if the customer is not active.</li>
<li><code>STOP</code>: the customer is not active any more from this day included (the last paid day is the day before). Ignored if the customer is not active.</li></ul>
<p>A day is paid with the plan the customer has <b>at the end</b> of that day (after all the events of the day). The price of one day of a plan in a month is the monthly price divided by the number of days of that month (28 to 31). Customers who are still active are billed until the last day of the month of the <b>latest date</b> in <code>events</code>.</p>
<p>The invoice of a customer for a month is the sum of its paid days, rounded to the nearest cent at the end (a half cent is rounded up). Your task is to return one string <code>"customer,YYYY-MM,cents"</code> per customer and month with at least one paid day, sorted by customer, then month.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(plans, events):
    # write your code here
    return []
"""
SOLUTION = """
import datetime


def days_in_month(d):
    nxt = (d.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    return (nxt - datetime.timedelta(days=1)).day


def solution(plans, events):
    if len(events) == 0:
        return []
    # 1. Les événements de chaque jour, dans l'ordre
    by_day = {}
    for e in events:
        p = e.split()
        d = datetime.date.fromisoformat(p[0])
        if d not in by_day:
            by_day[d] = []
        by_day[d].append(p[1:])

    first = min(by_day)
    last = max(by_day)
    end = last.replace(day=days_in_month(last))      # dernier jour du dernier mois

    plan_of = {}          # client actif -> plan
    total = {}            # (client, "YYYY-MM") -> somme des prix mensuels des jours payés
    d = first
    while d <= end:
        for ev in by_day.get(d, []):
            customer, action = ev[0], ev[1]
            if action == "START":
                plan_of[customer] = ev[2]
            elif action == "CHANGE":
                if customer in plan_of:
                    plan_of[customer] = ev[2]
            elif action == "STOP":
                if customer in plan_of:
                    del plan_of[customer]
        month = d.isoformat()[:7]
        for customer in plan_of:
            k = (customer, month)
            if k not in total:
                total[k] = 0
            total[k] += plans[plan_of[customer]]
        d += datetime.timedelta(days=1)

    out = []
    for customer, month in sorted(total):
        dim = days_in_month(datetime.date.fromisoformat(month + "-01"))
        # somme / jours du mois, arrondi au centime (0,5 vers le haut), en entiers
        cents = (2 * total[(customer, month)] + dim) // (2 * dim)
        out.append(customer + "," + month + "," + str(cents))
    return out
"""
MUTANTS = [
    SOLUTION.replace("                if customer in plan_of:\n                    plan_of[customer] = ev[2]", "                plan_of[customer] = ev[2]"),
    SOLUTION.replace("cents = (2 * total[(customer, month)] + dim) // (2 * dim)", "cents = total[(customer, month)] // dim"),
    SOLUTION.replace("dim = days_in_month(datetime.date.fromisoformat(month + \"-01\"))", "dim = 30"),
    SOLUTION.replace("    end = last.replace(day=days_in_month(last))      # dernier jour du dernier mois", "    end = last"),
]


def tests():
    plans = {"basic": 3000, "pro": 9000, "team": 15500}
    t = [{"plans": plans, "events": ["2026-01-10 acme START basic", "2026-01-20 acme CHANGE pro", "2026-02-01 bolt START team",
                                     "2026-02-14 acme STOP", "2026-02-14 bolt CHANGE basic", "2026-02-14 bolt CHANGE team", "2026-03-03 bolt STOP"]},
         {"plans": plans, "events": ["2026-02-28 x START pro", "2026-02-28 y CHANGE pro", "2026-03-01 x START basic", "2026-03-01 x STOP",
                                     "2026-03-01 x START pro", "2026-03-31 z STOP"]}]
    r = rng(4104)
    for _ in range(9):
        ev = []
        for _ in range(r.randint(3, 25)):
            c = r.choice(["acme", "bolt", "cyan"])
            a = r.choice(["START", "START", "CHANGE", "STOP"])
            ev.append([r.randint(0, 200), f"{c} {a}" + ("" if a == "STOP" else " " + r.choice(list(plans)))])
        ev.sort(key=lambda x: x[0])
        t.append({"plans": plans, "events": [f"{day(d, '2026-01-15')} {s}" for d, s in ev]})
    return t
