from kit import table, tables, rng, BLSQL

ID = "bs05"
NAME = "Credit Limit Bands"
LANG = "sql"
MINUTES = 12
TAGS = ["classes (bins)", "CASE WHEN", "bornes décimales", "LEFT JOIN pour les classes vides"]
SOURCE = BLSQL + " · Group by Bins"
SUMMARY_FR = "Compter les clients par tranche de plafond de crédit, en affichant aussi les tranches vides (0), et sans trou entre les bornes (50000.50 doit tomber quelque part)."
HINTS = ["Écris les tranches avec < et >=, jamais BETWEEN 0 AND 50000 puis BETWEEN 50001 AND ... : 50000.50 tomberait dans le vide.",
         "Pour afficher les tranches vides, pars d'une liste des 3 tranches (VALUES) et fais un LEFT JOIN."]
DESC = """
<p>The risk team groups customers by credit limit. You have the table <b>customers</b> with the columns <code>customer_name</code> and <code>credit_limit</code> (numeric, never <code>NULL</code>, can have cents).</p>
<p>The bands are:</p>
<ul><li><code>'0-50k'</code>: from 0 to 50,000 included;</li><li><code>'50k-100k'</code>: more than 50,000 and up to 100,000 included;</li><li><code>'100k+'</code>: more than 100,000.</li></ul>
<p>Your task is to return the columns <code>credit_band</code> and <code>customers</code> (the number of customers in the band), with the three bands always present (a band without customers has <code>0</code>), in the order of the list above.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH bands(credit_band, lo, hi, pos) AS (
  VALUES ('0-50k', -1::numeric, 50000::numeric, 1), ('50k-100k', 50000, 100000, 2), ('100k+', 100000, NULL, 3)
)
SELECT b.credit_band, COUNT(c.customer_name) AS customers
FROM bands b
LEFT JOIN customers c ON c.credit_limit > b.lo AND (b.hi IS NULL OR c.credit_limit <= b.hi)
GROUP BY b.credit_band, b.pos
ORDER BY b.pos;
"""
ALT = ["""
SELECT '0-50k' AS credit_band, (SELECT COUNT(*) FROM customers WHERE credit_limit <= 50000) AS customers
UNION ALL SELECT '50k-100k', (SELECT COUNT(*) FROM customers WHERE credit_limit > 50000 AND credit_limit <= 100000)
UNION ALL SELECT '100k+', (SELECT COUNT(*) FROM customers WHERE credit_limit > 100000);
"""]
MUTANTS = [
    """
SELECT CASE WHEN credit_limit BETWEEN 0 AND 50000 THEN '0-50k' WHEN credit_limit BETWEEN 50001 AND 100000 THEN '50k-100k' ELSE '100k+' END AS credit_band, COUNT(*) AS customers
FROM customers GROUP BY 1 ORDER BY MIN(credit_limit);
""",
    """
SELECT CASE WHEN credit_limit <= 50000 THEN '0-50k' WHEN credit_limit <= 100000 THEN '50k-100k' ELSE '100k+' END AS credit_band, COUNT(*) AS customers
FROM customers GROUP BY 1 ORDER BY MIN(credit_limit);
""",
]
C = "customer_name VARCHAR(40), credit_limit NUMERIC(12,2)"


def tests():
    t = [tables(customers=table(C, [["Atelier", 21000], ["Signal Gifts", 71800], ["Aus Collectors", 117300], ["La Rochelle", 118200], ["Baane", 81700], ["Mini Wheels", 50000.5]])),
         tables(customers=table(C, [["A", 0], ["B", 50000], ["C", 100000]]))]
    r = rng(205)
    for k in range(6):
        vals = [50000, 50000.01, 100000, 100000.5, 0, 49999.99]
        rows = [[f"c{i}", r.choice(vals) if r.random() < 0.4 else round(r.uniform(0, 160000 if k % 2 else 90000), 2)] for i in range(r.randint(1, 10))]
        t.append(tables(customers=table(C, rows)))
    return t
