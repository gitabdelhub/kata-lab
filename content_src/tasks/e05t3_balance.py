from kit import table, tables, rng

ID = "e05t3"
NAME = "First Overdraft per Account"
LANG = "sql"
MINUTES = 15
TAGS = ["somme cumulée", "SUM OVER ORDER BY", "départage par id", "première occurrence"]
DESC = """
<p>A bank wants to know when each account went into overdraft for the first time. You have two tables.</p>
<p><b>accounts</b>: <code>account_id</code> and <code>opening_balance</code> (numeric).</p>
<p><b>movements</b>: <code>movement_id</code> (integer, unique), <code>account_id</code>, <code>booked_at</code> (timestamp) and <code>amount</code> (numeric, positive for a deposit, negative for a withdrawal). Movements are applied in order of <code>booked_at</code>, then <code>movement_id</code> when two movements have the same time.</p>
<p>The balance after a movement is the opening balance plus the sum of all movements of the account up to this one, included.</p>
<p>Your task is to return, for every account whose balance becomes <b>strictly negative</b> at least once, the first movement that made it negative, with the columns <code>account_id</code>, <code>movement_id</code>, <code>booked_at</code> and <code>balance</code> (the balance after this movement), sorted by <code>account_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH b AS (
  SELECT m.account_id, m.movement_id, m.booked_at,
         a.opening_balance + SUM(m.amount) OVER (PARTITION BY m.account_id ORDER BY m.booked_at, m.movement_id
                                                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS balance
  FROM movements m JOIN accounts a ON a.account_id = m.account_id
),
f AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY booked_at, movement_id) AS rn
  FROM b WHERE balance < 0
)
SELECT account_id, movement_id, booked_at, balance FROM f WHERE rn = 1 ORDER BY account_id;
"""
MUTANTS = [
    """
WITH b AS (SELECT m.account_id, m.movement_id, m.booked_at, a.opening_balance + SUM(m.amount) OVER (PARTITION BY m.account_id ORDER BY m.booked_at) AS balance
  FROM movements m JOIN accounts a ON a.account_id = m.account_id),
f AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY booked_at, movement_id) AS rn FROM b WHERE balance < 0)
SELECT account_id, movement_id, booked_at, balance FROM f WHERE rn = 1 ORDER BY account_id;
""",
    """
WITH b AS (SELECT m.account_id, m.movement_id, m.booked_at, SUM(m.amount) OVER (PARTITION BY m.account_id ORDER BY m.booked_at, m.movement_id) AS balance FROM movements m),
f AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY booked_at, movement_id) AS rn FROM b WHERE balance < 0)
SELECT account_id, movement_id, booked_at, balance FROM f WHERE rn = 1 ORDER BY account_id;
""",
    """
WITH b AS (SELECT m.account_id, m.movement_id, m.booked_at, a.opening_balance + SUM(m.amount) OVER (PARTITION BY m.account_id ORDER BY m.booked_at, m.movement_id) AS balance
  FROM movements m JOIN accounts a ON a.account_id = m.account_id),
f AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY booked_at, movement_id) AS rn FROM b WHERE balance <= 0)
SELECT account_id, movement_id, booked_at, balance FROM f WHERE rn = 1 ORDER BY account_id;
""",
]
A = "account_id VARCHAR(5), opening_balance NUMERIC(10,2)"
M = "movement_id INT, account_id VARCHAR(5), booked_at TIMESTAMP, amount NUMERIC(10,2)"


def tests():
    t = [tables(accounts=table(A, [["A1", 100], ["A2", 0], ["A3", 50]]),
                movements=table(M, [[1, "A1", "2026-03-01 09:00:00", -60], [2, "A1", "2026-03-01 10:00:00", -50], [3, "A1", "2026-03-02 10:00:00", 200],
                                    [4, "A1", "2026-03-03 10:00:00", -400], [5, "A2", "2026-03-01 08:00:00", 30], [7, "A2", "2026-03-01 12:00:00", -30],
                                    [6, "A2", "2026-03-01 12:00:00", -10], [8, "A3", "2026-03-04 08:00:00", -50]])),
         tables(accounts=table(A, [["Z", 10]]), movements=table(M, [[2, "Z", "2026-01-01 00:00:00", 5], [1, "Z", "2026-01-01 00:00:00", -12]]))]
    r = rng(503)
    for _ in range(7):
        acc = [[f"A{i}", r.choice([0, 20, 50, 100.5])] for i in range(1, r.randint(2, 6))]
        mv = []
        for i in range(1, r.randint(4, 20)):
            mv.append([i, r.choice(acc)[0], f"2026-03-0{r.randint(1, 4)} {r.choice(['09', '12', '12', '18'])}:00:00", r.choice([-120, -60, -10.5, -30, 20, 40, 100, -1])])
        r.shuffle(mv)
        t.append(tables(accounts=table(A, acc), movements=table(M, mv)))
    return t
