from kit import table, tables, rng

ID = "p1x6"
NAME = "Product share of category revenue"
LANG = "sql"
MINUTES = 15
TAGS = ["PARTITION BY", "division entière", "CASE WHEN", "JOIN"]
SUMMARY_FR = "Revenu par produit (quantité × prix, seulement les commandes non annulées), puis sa part dans le revenu de sa catégorie en %, arrondie à 2 décimales (SUM() OVER (PARTITION BY category)). Ajoute un label : top si part >= 50, core si >= 20, sinon tail. Produits sans vente exclus. Trie par catégorie, part décroissante, produit."
DESC = """
<p>You are given two tables.</p>
<p><b>products</b>: <code>product_id</code> (integer), <code>name</code> (text), <code>category</code> (text).</p>
<p><b>order_lines</b>: <code>order_id</code> (integer), <code>product_id</code> (integer), <code>quantity</code> (integer), <code>unit_price</code> (integer, in dirhams), <code>cancelled</code> (boolean).</p>
<p>Your task is to compute, for each product that has at least one non-cancelled line:</p>
<ol><li><code>revenue</code> - the sum of <code>quantity * unit_price</code> over its non-cancelled lines;</li><li><code>share_pct</code> - its revenue divided by the revenue of all products of the same category, in percent, rounded to 2 decimals;</li><li><code>label</code> - <code>'top'</code> if <code>share_pct</code> is at least <code>50</code>, <code>'core'</code> if it is at least <code>20</code>, otherwise <code>'tail'</code>.</li></ol>
<p>Return <code>category</code>, <code>name</code>, <code>revenue</code>, <code>share_pct</code> and <code>label</code>, sorted by <code>category</code>, then <code>share_pct</code> descending, then <code>name</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH rev AS (
  SELECT p.category, p.name, SUM(l.quantity * l.unit_price) AS revenue
  FROM order_lines l
  JOIN products p ON p.product_id = l.product_id
  WHERE NOT l.cancelled
  GROUP BY p.category, p.product_id, p.name
), share AS (
  SELECT category, name, revenue,
         ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY category), 2) AS share_pct
  FROM rev
)
SELECT category, name, revenue, share_pct,
       CASE WHEN share_pct >= 50 THEN 'top'
            WHEN share_pct >= 20 THEN 'core'
            ELSE 'tail' END AS label
FROM share
ORDER BY category, share_pct DESC, name;
"""
MUTANTS = [
    """
WITH rev AS (SELECT p.category, p.name, SUM(l.quantity * l.unit_price) AS revenue FROM order_lines l JOIN products p ON p.product_id = l.product_id WHERE NOT l.cancelled GROUP BY p.category, p.product_id, p.name),
share AS (SELECT category, name, revenue, ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS share_pct FROM rev)
SELECT category, name, revenue, share_pct, CASE WHEN share_pct >= 50 THEN 'top' WHEN share_pct >= 20 THEN 'core' ELSE 'tail' END AS label FROM share ORDER BY category, share_pct DESC, name;
""",
    """
WITH rev AS (SELECT p.category, p.name, SUM(l.quantity * l.unit_price) AS revenue FROM order_lines l JOIN products p ON p.product_id = l.product_id WHERE NOT l.cancelled GROUP BY p.category, p.product_id, p.name),
tot AS (SELECT category, SUM(l.quantity * l.unit_price) AS total FROM order_lines l JOIN products p ON p.product_id = l.product_id WHERE NOT l.cancelled GROUP BY category),
share AS (SELECT r.category, r.name, r.revenue, ROUND(100 * r.revenue / t.total, 2) AS share_pct FROM rev r JOIN tot t ON t.category = r.category)
SELECT category, name, revenue, share_pct, CASE WHEN share_pct >= 50 THEN 'top' WHEN share_pct >= 20 THEN 'core' ELSE 'tail' END AS label FROM share ORDER BY category, share_pct DESC, name;
""",
]
HINTS = ["Fais-le en deux CTE : d'abord le revenu par produit (GROUP BY), puis la part avec SUM(revenue) OVER (PARTITION BY category).",
         "Si tu calcules le total de la catégorie dans une autre CTE, SUM(quantity * unit_price) est un bigint : 100 * revenue / total devient une division entière. Écris 100.0 * revenue / total.",
         "Le CASE vient après le calcul de share_pct : mets-le dans le SELECT final, avec WHEN ... THEN ... ELSE ... END."]
P = "product_id INT, name TEXT, category TEXT"
L = "order_id INT, product_id INT, quantity INT, unit_price INT, cancelled BOOLEAN"


def tests():
    t = [tables(products=table(P, [[1, "Tea", "drinks"], [2, "Coffee", "drinks"], [3, "Juice", "drinks"], [4, "Bread", "bakery"], [5, "Cake", "bakery"]]),
                order_lines=table(L, [[10, 1, 6, 15, False], [10, 2, 1, 30, False], [11, 3, 5, 10, False], [12, 2, 5, 30, True], [13, 4, 4, 3, False], [13, 5, 1, 7, True]])),
         tables(products=table(P, [[1, "A", "x"], [2, "B", "x"], [3, "C", "x"]]),
                order_lines=table(L, [[1, 1, 1, 1, False], [2, 2, 1, 1, False], [3, 3, 1, 1, False]]))]
    r = rng(11)
    for k in range(5):
        prods = [[i, f"P{i:02d}", r.choice(["drinks", "bakery", "dairy"])] for i in range(1, 7 + k)]
        lines = [[o, r.randint(1, 6 + k), r.randint(1, 5), r.randint(2, 40), r.random() < 0.2] for o in range(1, 15 + 4 * k)]
        t.append(tables(products=table(P, prods), order_lines=table(L, lines)))
    return t
