from kit import table, tables, rng, ts

ID = "h14t3"
NAME = "Match Refunds to Payments"
LANG = "sql"
MINUTES = 20
TAGS = ["appariement 1 pour 1", "ROW_NUMBER des deux côtés", "LEFT JOIN", "statuts", "minutes entre deux horodatages"]
DESC = """
<p>The table <b>payments</b> has the columns <code>payment_id</code>, <code>customer_id</code>, <code>paid_at</code> (timestamp), <code>amount</code> and <code>status</code> (<code>'ok'</code> or <code>'failed'</code>; failed payments do not exist for this report). The table <b>refunds</b> has the columns <code>refund_id</code>, <code>customer_id</code>, <code>refunded_at</code> (timestamp) and <code>amount</code>.</p>
<p>Refunds are matched to payments <b>one to one</b>, by customer and exact amount: for a customer and an amount, the 1st refund (by <code>refunded_at</code>, then <code>refund_id</code>) is matched with the 1st payment (by <code>paid_at</code>, then <code>payment_id</code>), the 2nd refund with the 2nd payment, and so on.</p>
<p>Each refund gets a <code>status</code>:</p>
<ul><li><code>'NO_PAYMENT'</code> when there is no payment with its rank;</li>
<li><code>'REFUND_BEFORE_PAYMENT'</code> when the matched payment is not strictly before the refund (suspicious);</li>
<li><code>'MATCHED'</code> otherwise.</li></ul>
<p>Your task is to return one row per refund with the columns <code>refund_id</code>, <code>customer_id</code>, <code>amount</code>, <code>payment_id</code> and <code>minutes_after_payment</code> (whole minutes from the payment to the refund) — both <code>NULL</code> unless the status is <code>'MATCHED'</code> — and <code>status</code>, sorted by <code>refund_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH p AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id, amount ORDER BY paid_at, payment_id) AS k
  FROM payments WHERE status = 'ok'
), r AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id, amount ORDER BY refunded_at, refund_id) AS k
  FROM refunds
)
SELECT r.refund_id, r.customer_id, r.amount,
       CASE WHEN p.paid_at < r.refunded_at THEN p.payment_id END AS payment_id,
       CASE WHEN p.paid_at < r.refunded_at THEN (EXTRACT(EPOCH FROM r.refunded_at - p.paid_at) / 60)::int END AS minutes_after_payment,
       CASE WHEN p.payment_id IS NULL THEN 'NO_PAYMENT'
            WHEN p.paid_at >= r.refunded_at THEN 'REFUND_BEFORE_PAYMENT'
            ELSE 'MATCHED' END AS status
FROM r
LEFT JOIN p ON p.customer_id = r.customer_id AND p.amount = r.amount AND p.k = r.k
ORDER BY r.refund_id;
"""
MUTANTS = [
    SOLUTION.replace("FROM payments WHERE status = 'ok'", "FROM payments"),
    SOLUTION.replace("ORDER BY paid_at, payment_id) AS k", "ORDER BY paid_at DESC, payment_id) AS k"),
    SOLUTION.replace("p.paid_at < r.refunded_at THEN p.payment_id", "p.paid_at <= r.refunded_at THEN p.payment_id").replace("WHEN p.paid_at >= r.refunded_at", "WHEN p.paid_at > r.refunded_at").replace("p.paid_at < r.refunded_at THEN (EXTRACT", "p.paid_at <= r.refunded_at THEN (EXTRACT"),
    SOLUTION.replace("PARTITION BY customer_id, amount ORDER BY refunded_at", "PARTITION BY customer_id ORDER BY refunded_at").replace("PARTITION BY customer_id, amount ORDER BY paid_at", "PARTITION BY customer_id ORDER BY paid_at"),
]
P = "payment_id INT, customer_id INT, paid_at TIMESTAMP, amount NUMERIC(10,2), status TEXT"
R = "refund_id INT, customer_id INT, refunded_at TIMESTAMP, amount NUMERIC(10,2)"


def tests():
    t = [tables(payments=table(P, [[1, 1, ts(0), 50, "ok"], [2, 1, ts(30), 50, "ok"], [3, 1, ts(40), 20, "failed"], [4, 2, ts(500), 99.9, "ok"],
                                   [5, 1, ts(45), 20, "ok"]]),
                refunds=table(R, [[10, 1, ts(100), 50], [11, 1, ts(90), 50], [12, 1, ts(200), 50], [13, 2, ts(400), 99.9], [14, 1, ts(41), 20]])),
         tables(payments=table(P, [[1, 3, ts(0), 10, "ok"]]), refunds=table(R, [[1, 3, ts(0), 10], [2, 4, ts(5), 10]]))]
    r = rng(4143)
    for _ in range(8):
        pays, refs = [], []
        for i in range(r.randint(4, 20)):
            pays.append([i + 1, r.randint(1, 3), ts(r.randint(0, 300)), r.choice([10, 20, 49.99]), r.choice(["ok"] * 5 + ["failed"])])
        for i in range(r.randint(2, 12)):
            refs.append([100 + i, r.randint(1, 3), ts(r.choice([r.randint(0, 300), r.randint(200, 600)])), r.choice([10, 20, 49.99])])
        t.append(tables(payments=table(P, pays), refunds=table(R, refs)))
    return t
