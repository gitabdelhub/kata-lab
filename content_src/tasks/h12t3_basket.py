from kit import table, tables, rng

ID = "h12t3"
NAME = "Frequently Bought Together"
LANG = "sql"
MINUTES = 25
TAGS = ["auto-jointure", "paires a < b", "doublons dans une commande", "division entière", "ROW_NUMBER par catégorie"]
DESC = """
<p>The table <b>order_items</b> has the columns <code>order_id</code>, <code>product_id</code> and <code>qty</code>; the same product can appear on several lines of the same order. The table <b>products</b> has the columns <code>product_id</code> and <code>category</code>.</p>
<p>For a pair of different products <code>(a, b)</code> with <code>a &lt; b</code> (text order), the <b>support</b> is the number of orders that contain both products (an order counts once, whatever the quantities). Only pairs with a support of at least 2 are kept.</p>
<p>The <b>lift</b> of a pair is <code>support * N / (orders_a * orders_b)</code>, where <code>N</code> is the total number of orders in the table and <code>orders_a</code>, <code>orders_b</code> are the numbers of orders that contain each product. Round it to 2 decimals.</p>
<p>The pairs are grouped by the category of product <code>a</code>. In each category, rank them by support (highest first), then lift (highest first), then <code>product_a</code>, then <code>product_b</code>, and keep the first 3.</p>
<p>Your task is to return the columns <code>category</code>, <code>product_a</code>, <code>product_b</code>, <code>support</code>, <code>lift</code> and <code>rnk</code> (1 to 3), sorted by <code>category</code>, then <code>rnk</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH oi AS (
  SELECT DISTINCT order_id, product_id FROM order_items
), n AS (
  SELECT COUNT(DISTINCT order_id) AS n FROM oi
), pc AS (
  SELECT product_id, COUNT(*) AS c FROM oi GROUP BY product_id
), p AS (
  SELECT a.product_id AS pa, b.product_id AS pb, COUNT(*) AS support
  FROM oi a JOIN oi b ON a.order_id = b.order_id AND a.product_id < b.product_id
  GROUP BY a.product_id, b.product_id
  HAVING COUNT(*) >= 2
), l AS (
  SELECT pr.category, p.pa AS product_a, p.pb AS product_b, p.support,
         ROUND(p.support * n.n::numeric / (ca.c * cb.c), 2) AS lift
  FROM p
  JOIN pc ca ON ca.product_id = p.pa
  JOIN pc cb ON cb.product_id = p.pb
  JOIN products pr ON pr.product_id = p.pa
  CROSS JOIN n
), r AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY category ORDER BY support DESC, lift DESC, product_a, product_b) AS rnk
  FROM l
)
SELECT category, product_a, product_b, support, lift, rnk
FROM r
WHERE rnk <= 3
ORDER BY category, rnk;
"""
MUTANTS = [
    SOLUTION.replace("SELECT DISTINCT order_id, product_id FROM order_items", "SELECT order_id, product_id FROM order_items"),
    SOLUTION.replace("ROUND(p.support * n.n::numeric / (ca.c * cb.c), 2)", "ROUND(p.support * n.n / (ca.c * cb.c), 2)"),
    SOLUTION.replace("ORDER BY support DESC, lift DESC, product_a, product_b", "ORDER BY support DESC, product_a, product_b"),
    SOLUTION.replace("HAVING COUNT(*) >= 2", "HAVING COUNT(*) >= 1"),
]
OI = "order_id INT, product_id TEXT, qty INT"
PR = "product_id TEXT, category TEXT"


def tests():
    prods = [["P1", "food"], ["P2", "food"], ["P3", "drinks"], ["P4", "drinks"], ["P5", "home"], ["P6", "food"]]
    t = [tables(order_items=table(OI, [[1, "P1", 1], [1, "P3", 2], [1, "P3", 1], [2, "P1", 1], [2, "P3", 1], [2, "P4", 1],
                                       [3, "P3", 1], [3, "P4", 3], [4, "P1", 1], [4, "P2", 1], [5, "P1", 2], [5, "P2", 1], [5, "P3", 1],
                                       [6, "P5", 1]]),
                products=table(PR, prods)),
         tables(order_items=table(OI, [[1, "P5", 1], [1, "P6", 1], [2, "P5", 1], [2, "P6", 1], [3, "P2", 1]]), products=table(PR, prods))]
    r = rng(4123)
    for _ in range(8):
        rows = []
        for o in range(1, r.randint(6, 25)):
            for p in r.sample([x[0] for x in prods], r.randint(1, 4)):
                for _ in range(r.choice([1, 1, 2])):
                    rows.append([o, p, r.randint(1, 3)])
        t.append(tables(order_items=table(OI, rows), products=table(PR, prods)))
    return t
