from kit import table, tables, rng, ts

ID = "h08t3"
NAME = "Price Validity Periods"
LANG = "sql"
MINUTES = 20
TAGS = ["historique (SCD2)", "DISTINCT ON", "doublons d'horodatage", "LAG / LEAD", "faux changements"]
DESC = """
<p>The table <b>price_changes</b> is the change log of a marketplace: <code>change_id</code>, <code>product_id</code>, <code>changed_at</code> (timestamp) and <code>price</code>. We want to turn it into validity periods (one row per price that was really in force).</p>
<p>Rules, in this order:</p>
<ol><li>When a product has several log entries at the same <code>changed_at</code>, only the one with the highest <code>change_id</code> is real (the others were corrected immediately).</li>
<li>An entry whose price is equal to the price in force just before it (previous kept entry of the same product) is not a real change and is dropped; the period of the previous price simply continues.</li>
<li>A period starts at the <code>changed_at</code> of a real change (<code>valid_from</code>) and ends at the <code>changed_at</code> of the next real change of the same product (<code>valid_to</code>). The current price has <code>valid_to</code> = <code>NULL</code>.</li></ol>
<p>Your task is to return the columns <code>product_id</code>, <code>price</code>, <code>valid_from</code>, <code>valid_to</code> and <code>days_valid</code> (the number of calendar days between the date of <code>valid_from</code> and the date of <code>valid_to</code>, <code>NULL</code> for the current price), sorted by <code>product_id</code>, then <code>valid_from</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH d AS (
  SELECT DISTINCT ON (product_id, changed_at) product_id, changed_at, price
  FROM price_changes
  ORDER BY product_id, changed_at, change_id DESC
), l AS (
  SELECT *, LAG(price) OVER (PARTITION BY product_id ORDER BY changed_at) AS prev_price FROM d
), r AS (
  SELECT product_id, price, changed_at AS valid_from
  FROM l
  WHERE prev_price IS NULL OR prev_price <> price
)
SELECT product_id, price, valid_from,
       LEAD(valid_from) OVER w AS valid_to,
       (LEAD(valid_from) OVER w)::date - valid_from::date AS days_valid
FROM r
WINDOW w AS (PARTITION BY product_id ORDER BY valid_from)
ORDER BY product_id, valid_from;
"""
MUTANTS = [
    SOLUTION.replace("ORDER BY product_id, changed_at, change_id DESC", "ORDER BY product_id, changed_at, change_id"),
    SOLUTION.replace("WHERE prev_price IS NULL OR prev_price <> price", "WHERE true"),
    SOLUTION.replace("""), r AS (
  SELECT product_id, price, changed_at AS valid_from
  FROM l
  WHERE prev_price IS NULL OR prev_price <> price
)
SELECT product_id, price, valid_from,
       LEAD(valid_from) OVER w AS valid_to,
       (LEAD(valid_from) OVER w)::date - valid_from::date AS days_valid
FROM r""", """), r AS (
  SELECT product_id, price, changed_at AS valid_from, prev_price,
         LEAD(changed_at) OVER (PARTITION BY product_id ORDER BY changed_at) AS nxt
  FROM l
)
SELECT product_id, price, valid_from, nxt AS valid_to, nxt::date - valid_from::date AS days_valid
FROM r WHERE prev_price IS NULL OR prev_price <> price"""),
    SOLUTION.replace("(LEAD(valid_from) OVER w)::date - valid_from::date", "EXTRACT(DAY FROM LEAD(valid_from) OVER w - valid_from)::int"),
]
T = "change_id INT, product_id TEXT, changed_at TIMESTAMP, price NUMERIC(10,2)"


def tests():
    t = [tables(price_changes=table(T, [
        [1, "P1", ts(0), 10.00], [2, "P1", ts(1500), 12.00], [3, "P1", ts(1500), 11.50], [4, "P1", ts(3000), 11.50],
        [5, "P1", ts(4500), 9.99], [6, "P2", ts(100), 5.00], [7, "P2", ts(1000), 5.00]])),
         tables(price_changes=table(T, [[1, "A", ts(0), 1.00], [2, "A", ts(10), 2.00], [3, "A", ts(1430), 1.00], [4, "A", ts(1450), 1.00]]))]
    r = rng(4083)
    for _ in range(8):
        rows, n = [], 0
        for p in ["P1", "P2", "P3"][: r.randint(1, 3)]:
            m = r.randint(0, 600)
            for _ in range(r.randint(2, 10)):
                m += r.choice([0, 0, 30, 700, 1440, 3000])
                n += 1
                rows.append([n, p, ts(m), r.choice([9.99, 10.00, 12.50, 12.50, 15.00])])
        r.shuffle(rows)
        t.append(tables(price_changes=table(T, rows)))
    return t
