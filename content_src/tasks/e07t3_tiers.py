from kit import table, tables, rng

ID = "e07t3"
NAME = "Tiered Electricity Bills"
LANG = "sql"
MINUTES = 18
TAGS = ["jointure sur intervalle", "LEAST / GREATEST", "tranches", "LEFT JOIN client sans conso"]
DESC = """
<p>An electricity provider bills its customers with a <b>tiered</b> price. You have two tables.</p>
<p><b>usage</b>: <code>customer_id</code>, <code>month</code> (date, the first day of the month) and <code>kwh</code> (numeric). A customer has at most one row per month.</p>
<p><b>tiers</b>: <code>tier</code> (integer), <code>from_kwh</code> (numeric), <code>to_kwh</code> (numeric, <code>NULL</code> for the last tier, which has no upper limit) and <code>price</code> (numeric, price of one kWh in this tier). Tiers do not overlap and cover all values from <code>0</code>.</p>
<p>Each kWh is billed at the price of the tier it falls in: for a usage of <code>u</code> kWh, the quantity billed in a tier is the part of <code>[0, u]</code> that is inside <code>[from_kwh, to_kwh]</code>, which is <code>LEAST(u, to_kwh) - from_kwh</code> when it is positive, and <code>0</code> otherwise. A fixed fee of <code>20</code> is added to every bill, including bills with a usage of <code>0</code>.</p>
<p>Your task is to return, for every row of <code>usage</code>, the columns <code>customer_id</code>, <code>month</code>, <code>kwh</code> and <code>bill</code> (rounded to 2 decimals), sorted by <code>month</code>, then <code>customer_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>For <code>250</code> kWh with the tiers <code>[0, 100]</code> at <code>0.9</code>, <code>[100, 200]</code> at <code>1.1</code> and <code>[200, ∞)</code> at <code>1.5</code>: <code>100 * 0.9 + 100 * 1.1 + 50 * 1.5 + 20 = 295</code>.</p>
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
SELECT u.customer_id, u.month, u.kwh,
       ROUND(20 + COALESCE(SUM(GREATEST(LEAST(u.kwh, COALESCE(t.to_kwh, u.kwh)) - t.from_kwh, 0) * t.price), 0), 2) AS bill
FROM usage u
CROSS JOIN tiers t
GROUP BY u.customer_id, u.month, u.kwh
ORDER BY u.month, u.customer_id;
"""
MUTANTS = [
    """
SELECT u.customer_id, u.month, u.kwh, ROUND(20 + u.kwh * t.price, 2) AS bill
FROM usage u JOIN tiers t ON u.kwh >= t.from_kwh AND (t.to_kwh IS NULL OR u.kwh < t.to_kwh) ORDER BY u.month, u.customer_id;
""",
    """
SELECT u.customer_id, u.month, u.kwh, ROUND(20 + SUM(GREATEST(u.kwh - t.from_kwh, 0) * t.price), 2) AS bill
FROM usage u CROSS JOIN tiers t GROUP BY u.customer_id, u.month, u.kwh ORDER BY u.month, u.customer_id;
""",
    """
SELECT u.customer_id, u.month, u.kwh, ROUND(SUM(GREATEST(LEAST(u.kwh, COALESCE(t.to_kwh, u.kwh)) - t.from_kwh, 0) * t.price), 2) AS bill
FROM usage u CROSS JOIN tiers t WHERE u.kwh > t.from_kwh GROUP BY u.customer_id, u.month, u.kwh ORDER BY u.month, u.customer_id;
""",
]
U = "customer_id VARCHAR(5), month DATE, kwh NUMERIC(10,2)"
T = "tier INT, from_kwh NUMERIC(10,2), to_kwh NUMERIC(10,2), price NUMERIC(6,3)"
TIERS = [[1, 0, 100, 0.9], [2, 100, 200, 1.1], [3, 200, None, 1.5]]


def tests():
    t = [tables(usage=table(U, [["C1", "2026-03-01", 250], ["C2", "2026-03-01", 80], ["C3", "2026-03-01", 0], ["C1", "2026-02-01", 200], ["C4", "2026-02-01", 100.5]]), tiers=table(T, TIERS)),
         tables(usage=table(U, [["A", "2026-01-01", 1000]]), tiers=table(T, [[1, 0, 50, 2], [2, 50, None, 1]]))]
    r = rng(703)
    for _ in range(7):
        rows = [[f"C{i}", f"2026-0{r.randint(1, 3)}-01", r.choice([0, 50, 100, 150, 200, 201, round(r.uniform(0, 600), 2)])] for i in range(1, r.randint(2, 9))]
        tiers = TIERS if r.random() < 0.5 else [[1, 0, 150, 0.8], [2, 150, 300, 1.2], [3, 300, 500, 1.6], [4, 500, None, 2.0]]
        t.append(tables(usage=table(U, rows), tiers=table(T, tiers)))
    return t
