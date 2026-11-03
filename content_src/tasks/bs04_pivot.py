from kit import table, tables, rng, BLSQL

ID = "bs04"
NAME = "Quarterly Expense Pivot"
LANG = "sql"
MINUTES = 15
TAGS = ["pivot", "SUM(CASE WHEN)", "COALESCE", "0 si absent"]
SOURCE = BLSQL + " · Pivoting Numeric Data"
SUMMARY_FR = "Transformer des lignes (catégorie, mois, montant) en un tableau avec une colonne par mois (jan, feb, mar) et le total, 0 quand il n'y a rien."
HINTS = ["Une colonne par mois : SUM(CASE WHEN month = 1 THEN amount ELSE 0 END) AS jan, etc.",
         "Les montants NULL ne comptent pas, et une catégorie sans dépense au T1 n'apparaît pas."]
DESC = """
<p>The finance team wants the first quarter expenses as a pivot table. You have the table <b>expenses</b>, with one row per expense:</p>
<ul><li><code>category</code> - the expense category;</li><li><code>spent_on</code> - the date of the expense;</li><li><code>amount</code> - the amount (numeric, can be <code>NULL</code> when it was not entered yet; a <code>NULL</code> amount counts as <code>0</code>).</li></ul>
<p>Your task is to return one row per category that has at least one expense between <code>2026-01-01</code> and <code>2026-03-31</code> (both included), with the columns <code>category</code>, <code>jan</code>, <code>feb</code>, <code>mar</code> (the sum of the amounts of each month, <code>0</code> if there is none) and <code>q1_total</code>. Expenses outside the first quarter of 2026 are ignored. Sort by <code>q1_total</code> descending, then <code>category</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
SELECT category,
       SUM(CASE WHEN EXTRACT(MONTH FROM spent_on) = 1 THEN COALESCE(amount, 0) ELSE 0 END) AS jan,
       SUM(CASE WHEN EXTRACT(MONTH FROM spent_on) = 2 THEN COALESCE(amount, 0) ELSE 0 END) AS feb,
       SUM(CASE WHEN EXTRACT(MONTH FROM spent_on) = 3 THEN COALESCE(amount, 0) ELSE 0 END) AS mar,
       SUM(COALESCE(amount, 0)) AS q1_total
FROM expenses
WHERE spent_on BETWEEN DATE '2026-01-01' AND DATE '2026-03-31'
GROUP BY category
ORDER BY q1_total DESC, category;
"""
ALT = ["""
WITH c AS (SELECT DISTINCT category FROM expenses WHERE spent_on >= '2026-01-01' AND spent_on < '2026-04-01'),
m AS (SELECT category, date_trunc('month', spent_on)::date AS mo, SUM(amount) AS s FROM expenses
      WHERE spent_on >= '2026-01-01' AND spent_on < '2026-04-01' GROUP BY 1, 2)
SELECT c.category,
       COALESCE(j.s, 0) AS jan, COALESCE(f.s, 0) AS feb, COALESCE(r.s, 0) AS mar,
       COALESCE(j.s, 0) + COALESCE(f.s, 0) + COALESCE(r.s, 0) AS q1_total
FROM c
LEFT JOIN m j ON j.category = c.category AND j.mo = '2026-01-01'
LEFT JOIN m f ON f.category = c.category AND f.mo = '2026-02-01'
LEFT JOIN m r ON r.category = c.category AND r.mo = '2026-03-01'
ORDER BY q1_total DESC, c.category;
"""]
MUTANTS = [
    """
SELECT category, SUM(CASE WHEN EXTRACT(MONTH FROM spent_on) = 1 THEN amount END) AS jan, SUM(CASE WHEN EXTRACT(MONTH FROM spent_on) = 2 THEN amount END) AS feb,
       SUM(CASE WHEN EXTRACT(MONTH FROM spent_on) = 3 THEN amount END) AS mar, SUM(amount) AS q1_total
FROM expenses WHERE spent_on BETWEEN DATE '2026-01-01' AND DATE '2026-03-31' GROUP BY category ORDER BY q1_total DESC, category;
""",
    """
SELECT category, SUM(CASE WHEN EXTRACT(MONTH FROM spent_on) = 1 THEN COALESCE(amount, 0) ELSE 0 END) AS jan, SUM(CASE WHEN EXTRACT(MONTH FROM spent_on) = 2 THEN COALESCE(amount, 0) ELSE 0 END) AS feb,
       SUM(CASE WHEN EXTRACT(MONTH FROM spent_on) = 3 THEN COALESCE(amount, 0) ELSE 0 END) AS mar, SUM(COALESCE(amount, 0)) AS q1_total
FROM expenses GROUP BY category ORDER BY q1_total DESC, category;
""",
]
E = "category VARCHAR(20), spent_on DATE, amount NUMERIC(10,2)"


def tests():
    t = [tables(expenses=table(E, [["travel", "2026-01-12", 300], ["travel", "2026-03-02", 120.5], ["cloud", "2026-01-31", 80], ["cloud", "2026-02-01", 80],
                                   ["cloud", "2026-02-15", None], ["office", "2025-12-31", 999], ["office", "2026-04-01", 50]])),
         tables(expenses=table(E, [["a", "2026-03-31", 10], ["b", "2026-02-28", 10], ["c", "2026-01-01", None]]))]
    r = rng(204)
    for _ in range(6):
        rows = [[r.choice(["travel", "cloud", "office", "food"]), f"2026-{r.choice([1, 2, 3, 3, 4]):02d}-{r.randint(1, 28):02d}" if r.random() < 0.9 else "2025-12-30",
                 r.choice([None, round(r.uniform(5, 500), 2), 100])] for _ in range(r.randint(1, 12))]
        t.append(tables(expenses=table(E, rows)))
    return t
