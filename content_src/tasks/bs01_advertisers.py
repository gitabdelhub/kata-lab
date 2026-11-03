from kit import table, tables, rng, BLSQL

ID = "bs01"
NAME = "Advertiser Daily Status"
LANG = "sql"
MINUTES = 15
TAGS = ["FULL JOIN", "CASE WHEN", "nouveaux utilisateurs"]
SOURCE = BLSQL + " · Advertiser Status"
SUMMARY_FR = "Mettre à jour le statut de chaque annonceur à partir des paiements du jour : pas payé = CHURN, payé après CHURN = RESURRECT, payé et inconnu hier = NEW, sinon EXISTING."
HINTS = ["Il faut tous les annonceurs d'hier ET les nouveaux qui ont payé aujourd'hui : FULL OUTER JOIN sur user_id.",
         "Ordre du CASE : d'abord 'pas payé', puis 'statut d'hier = CHURN', puis 'inconnu hier', sinon EXISTING."]
DESC = """
<p>An ads platform tracks the status of its advertisers every day. You have two tables.</p>
<p><b>advertisers</b> contains the status of each known advertiser at the end of yesterday:</p>
<ul><li><code>user_id</code> - the advertiser (unique);</li><li><code>status</code> - one of <code>'NEW'</code>, <code>'EXISTING'</code>, <code>'CHURN'</code>, <code>'RESURRECT'</code>.</li></ul>
<p><b>daily_pay</b> contains one row per payment made <b>today</b> (an advertiser can pay several times, and only advertisers who paid appear):</p>
<ul><li><code>user_id</code> - the advertiser;</li><li><code>paid</code> - the amount paid (integer).</li></ul>
<p>The new status of an advertiser is computed as follows:</p>
<ul><li>an advertiser that did <b>not</b> pay today becomes <code>'CHURN'</code>;</li><li>an advertiser that paid today and whose status yesterday was <code>'CHURN'</code> becomes <code>'RESURRECT'</code>;</li><li>an advertiser that paid today and is <b>not</b> in <code>advertisers</code> is <code>'NEW'</code>;</li><li>any other advertiser that paid today becomes <code>'EXISTING'</code>.</li></ul>
<p>Your task is to return the columns <code>user_id</code> and <code>status</code> with the new status of every advertiser (known yesterday or new today), sorted by <code>user_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
SELECT user_id, status FROM advertisers;
"""
SOLUTION = """
WITH paid AS (SELECT DISTINCT user_id FROM daily_pay)
SELECT COALESCE(a.user_id, p.user_id) AS user_id,
       CASE WHEN p.user_id IS NULL THEN 'CHURN'
            WHEN a.status = 'CHURN' THEN 'RESURRECT'
            WHEN a.user_id IS NULL THEN 'NEW'
            ELSE 'EXISTING' END AS status
FROM advertisers a
FULL OUTER JOIN paid p ON p.user_id = a.user_id
ORDER BY user_id;
"""
ALT = ["""
SELECT user_id, status FROM (
  SELECT a.user_id,
         CASE WHEN NOT EXISTS (SELECT 1 FROM daily_pay d WHERE d.user_id = a.user_id) THEN 'CHURN'
              WHEN a.status = 'CHURN' THEN 'RESURRECT' ELSE 'EXISTING' END AS status
  FROM advertisers a
  UNION ALL
  SELECT DISTINCT d.user_id, 'NEW' FROM daily_pay d
  WHERE d.user_id NOT IN (SELECT user_id FROM advertisers)
) x ORDER BY user_id;
"""]
MUTANTS = [
    """
SELECT a.user_id, CASE WHEN p.user_id IS NULL THEN 'CHURN' WHEN a.status = 'CHURN' THEN 'RESURRECT' ELSE 'EXISTING' END AS status
FROM advertisers a LEFT JOIN (SELECT DISTINCT user_id FROM daily_pay) p ON p.user_id = a.user_id ORDER BY a.user_id;
""",
    """
SELECT COALESCE(a.user_id, p.user_id) AS user_id,
       CASE WHEN p.user_id IS NULL THEN 'CHURN' WHEN a.user_id IS NULL THEN 'NEW' ELSE 'EXISTING' END AS status
FROM advertisers a FULL OUTER JOIN (SELECT DISTINCT user_id FROM daily_pay) p ON p.user_id = a.user_id ORDER BY user_id;
""",
    """
SELECT COALESCE(a.user_id, p.user_id) AS user_id,
       CASE WHEN p.user_id IS NULL THEN 'CHURN' WHEN a.status = 'CHURN' THEN 'RESURRECT' WHEN a.user_id IS NULL THEN 'NEW' ELSE 'EXISTING' END AS status
FROM advertisers a FULL OUTER JOIN daily_pay p ON p.user_id = a.user_id ORDER BY user_id;
""",
]
A = "user_id VARCHAR(20), status VARCHAR(10)"
D = "user_id VARCHAR(20), paid INT"
ST = ["NEW", "EXISTING", "CHURN", "RESURRECT"]


def tests():
    t = [tables(advertisers=table(A, [["bing", "NEW"], ["yahoo", "NEW"], ["alibaba", "EXISTING"], ["baidu", "EXISTING"], ["target", "CHURN"],
                                      ["tesla", "CHURN"], ["morgan", "RESURRECT"], ["chase", "RESURRECT"]]),
                daily_pay=table(D, [["yahoo", 45], ["alibaba", 100], ["target", 13], ["morgan", 600], ["fitdata", 25], ["fitdata", 5]])),
         tables(advertisers=table(A, [["a1", "CHURN"], ["a2", "EXISTING"]]), daily_pay=table(D, [["a1", 10], ["a3", 7]]))]
    r = rng(201)
    for k in range(6):
        users = [f"u{i:02d}" for i in range(12)]
        known = r.sample(users, r.randint(2, 8))
        adv = [[u, r.choice(ST)] for u in known]
        pay = [[r.choice(users), r.randint(1, 99)] for _ in range(r.randint(0, 10))]
        t.append(tables(advertisers=table(A, adv), daily_pay=table(D, pay)))
    return t
