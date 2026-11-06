from kit import table, tables, rng, ts

ID = "h05t3"
NAME = "Overdraft Episodes"
LANG = "sql"
MINUTES = 20
TAGS = ["solde cumulé", "îlots", "LAG avec valeur par défaut", "FILTER"]
DESC = """
<p>The table <b>transactions</b> has the columns <code>tx_id</code>, <code>account_id</code>, <code>ts</code> (timestamp), <code>amount</code> (numeric, negative for a debit) and <code>status</code>. Only transactions with the status <code>'settled'</code> change the balance; <code>'pending'</code> and <code>'failed'</code> ones are ignored.</p>
<p>Every account starts at a balance of 0. Process the settled transactions of an account in order of <code>ts</code>, then <code>tx_id</code>, and compute the balance after each of them. An <b>overdraft episode</b> starts with a transaction after which the balance is negative while it was not negative just before (the very first transaction of an account can start an episode). The episode lasts while the balance stays negative and ends with the first transaction after which the balance is 0 or more again: that transaction is the <b>recovery</b>.</p>
<p>Your task is to return one row per episode with the columns <code>account_id</code>, <code>started_at</code> (ts of the transaction that started it), <code>recovered_at</code> (ts of the recovery, <code>NULL</code> if the account is still negative), <code>lowest_balance</code> (the lowest balance reached during the episode) and <code>txs_in_episode</code> (number of transactions after which the balance was negative in this episode), sorted by <code>account_id</code>, then <code>started_at</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH t AS (
  SELECT account_id, tx_id, ts,
         SUM(amount) OVER (PARTITION BY account_id ORDER BY ts, tx_id) AS bal
  FROM transactions
  WHERE status = 'settled'
), f AS (
  SELECT *, bal < 0 AS neg,
         LAG(bal < 0, 1, false) OVER (PARTITION BY account_id ORDER BY ts, tx_id) AS prev_neg
  FROM t
), g AS (
  SELECT *, SUM(CASE WHEN neg AND NOT prev_neg THEN 1 ELSE 0 END)
              OVER (PARTITION BY account_id ORDER BY ts, tx_id) AS ep
  FROM f
)
SELECT account_id,
       MIN(ts) FILTER (WHERE neg) AS started_at,
       MIN(ts) FILTER (WHERE NOT neg) AS recovered_at,
       MIN(bal) AS lowest_balance,
       COUNT(*) FILTER (WHERE neg) AS txs_in_episode
FROM g
WHERE ep > 0
GROUP BY account_id, ep
ORDER BY account_id, started_at;
"""
MUTANTS = [
    SOLUTION.replace("WHERE status = 'settled'", "WHERE status <> 'failed'"),
    SOLUTION.replace("LAG(bal < 0, 1, false)", "LAG(bal < 0)"),
    SOLUTION.replace("MIN(ts) FILTER (WHERE NOT neg) AS recovered_at", "MIN(ts) FILTER (WHERE bal > 0) AS recovered_at"),
    SOLUTION.replace("ORDER BY ts, tx_id) AS bal", "ORDER BY ts) AS bal"),
]
T = "tx_id INT, account_id INT, ts TIMESTAMP, amount NUMERIC(10,2), status TEXT"


def tests():
    t = [tables(transactions=table(T, [
        [1, 1, ts(0), 100, "settled"], [2, 1, ts(60), -150, "settled"], [3, 1, ts(70), -20, "settled"], [4, 1, ts(80), 300, "pending"],
        [5, 1, ts(90), 70, "settled"], [6, 1, ts(100), -1, "settled"], [7, 2, ts(0), -40, "settled"], [8, 2, ts(10), 40, "failed"],
        [9, 2, ts(20), 15, "settled"]])),
         tables(transactions=table(T, [[1, 5, ts(0), 10, "settled"], [3, 5, ts(30), -40, "settled"], [2, 5, ts(30), 25, "settled"],
                                       [4, 5, ts(40), -5, "settled"], [5, 5, ts(50), 0.5, "settled"]]))]
    r = rng(4053)
    for _ in range(8):
        rows, n = [], 0
        for a in range(1, r.randint(2, 5)):
            m = 0
            for _ in range(r.randint(3, 14)):
                n += 1
                m += r.choice([0, 5, 30, 600])
                rows.append([n, a, ts(m), r.choice([-80, -50, -25, -10, 10, 20, 35, 60, 100]),
                             r.choice(["settled"] * 6 + ["pending", "failed"])])
        r.shuffle(rows)
        t.append(tables(transactions=table(T, rows)))
    return t
