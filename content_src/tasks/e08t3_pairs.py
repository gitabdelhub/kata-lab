from kit import table, tables, rng

ID = "e08t3"
NAME = "Frequently Bought Together"
LANG = "sql"
MINUTES = 15
TAGS = ["auto-jointure", "paires a < b", "DISTINCT avant de compter", "HAVING"]
DESC = """
<p>The recommendation team looks for products that are often bought together. You have the table <b>order_items</b> with the columns <code>order_id</code>, <code>product_id</code> and <code>qty</code>. The same product can appear on several lines of the same order.</p>
<p>Two different products form a <b>pair</b> in an order if both appear in this order. Each pair is written once, with <code>product_a &lt; product_b</code> in alphabetical order.</p>
<p>Your task is to return the pairs that appear together in <b>at least 2 different orders</b>, with the columns <code>product_a</code>, <code>product_b</code> and <code>orders</code> (number of distinct orders that contain both), sorted by <code>orders</code> descending, then <code>product_a</code>, then <code>product_b</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH d AS (SELECT DISTINCT order_id, product_id FROM order_items)
SELECT a.product_id AS product_a, b.product_id AS product_b, COUNT(*) AS orders
FROM d a
JOIN d b ON a.order_id = b.order_id AND a.product_id < b.product_id
GROUP BY a.product_id, b.product_id
HAVING COUNT(*) >= 2
ORDER BY orders DESC, product_a, product_b;
"""
MUTANTS = [
    """
SELECT a.product_id AS product_a, b.product_id AS product_b, COUNT(*) AS orders
FROM order_items a JOIN order_items b ON a.order_id = b.order_id AND a.product_id < b.product_id
GROUP BY a.product_id, b.product_id HAVING COUNT(*) >= 2 ORDER BY orders DESC, product_a, product_b;
""",
    """
WITH d AS (SELECT DISTINCT order_id, product_id FROM order_items)
SELECT a.product_id AS product_a, b.product_id AS product_b, COUNT(*) AS orders
FROM d a JOIN d b ON a.order_id = b.order_id AND a.product_id <> b.product_id
GROUP BY a.product_id, b.product_id HAVING COUNT(*) >= 2 ORDER BY orders DESC, product_a, product_b;
""",
]
I = "order_id INT, product_id VARCHAR(10), qty INT"


def tests():
    t = [tables(order_items=table(I, [[1, "bread", 1], [1, "milk", 2], [1, "eggs", 1], [2, "milk", 1], [2, "bread", 1], [2, "bread", 3],
                                      [3, "milk", 1], [3, "eggs", 6], [4, "eggs", 1], [4, "bread", 1], [4, "milk", 1], [5, "tea", 1]])),
         tables(order_items=table(I, [[1, "a", 1], [1, "a", 1], [1, "b", 1], [2, "b", 1], [2, "a", 2], [2, "a", 1], [3, "a", 1]]))]
    r = rng(803)
    for _ in range(7):
        rows = []
        for o in range(1, r.randint(3, 12)):
            for p in r.sample(["bread", "milk", "eggs", "tea", "jam", "rice"], r.randint(1, 4)):
                for _ in range(r.choice([1, 1, 2])):
                    rows.append([o, p, r.randint(1, 5)])
        t.append(tables(order_items=table(I, rows)))
    return t
