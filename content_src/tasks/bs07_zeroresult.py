from kit import table, tables, rng, BLSQL

ID = "bs07"
NAME = "Zero-Result Search Rate"
LANG = "sql"
MINUTES = 15
TAGS = ["moyenne pondérée", "NULL dans les agrégats", "NULLIF", "ROUND"]
SOURCE = BLSQL + " · Invalid Search"
SUMMARY_FR = "Calculer par pays le nombre total de recherches et le pourcentage moyen de recherches sans résultat, pondéré par le nombre de recherches, en ignorant les catégories où le pourcentage est inconnu."
HINTS = ["Pondéré : SUM(num_search * pct) / SUM(num_search) mais le dénominateur ne doit compter QUE les lignes où pct n'est pas NULL.",
         "Si aucune ligne n'a de pourcentage, le résultat est NULL : NULLIF(dénominateur, 0) évite la division par zéro."]
DESC = """
<p>A search engine stores daily statistics per country and search category in the table <b>search_category</b>:</p>
<ul><li><code>country</code>, <code>search_cat</code> - the pair (unique);</li><li><code>num_search</code> - the number of searches (integer, can be <code>NULL</code> when the counter failed);</li><li><code>zero_result_pct</code> - the percentage of these searches that returned no result (numeric, can be <code>NULL</code> when it was not measured).</li></ul>
<p>For each country, compute:</p>
<ul><li><code>num_search</code>: the total number of searches (rows with a <code>NULL</code> count are ignored; <code>0</code> if there is none);</li><li><code>zero_result_pct</code>: the <b>weighted average</b> of <code>zero_result_pct</code>, using <code>num_search</code> as weights, computed only on the rows where both values are known, rounded to <code>2</code> decimals. It is <code>NULL</code> if the country has no such row or if the sum of the weights is <code>0</code>.</li></ul>
<p>Your task is to return <code>country</code>, <code>num_search</code> and <code>zero_result_pct</code>, sorted by <code>country</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
SELECT country,
       COALESCE(SUM(num_search), 0) AS num_search,
       ROUND(SUM(num_search * zero_result_pct)
             / NULLIF(SUM(CASE WHEN zero_result_pct IS NOT NULL THEN num_search END), 0), 2) AS zero_result_pct
FROM search_category
GROUP BY country
ORDER BY country;
"""
ALT = ["""
WITH k AS (SELECT country, SUM(num_search::numeric * zero_result_pct) AS w, SUM(num_search) AS n
           FROM search_category WHERE num_search IS NOT NULL AND zero_result_pct IS NOT NULL GROUP BY country),
t AS (SELECT country, SUM(num_search) AS total FROM search_category GROUP BY country)
SELECT t.country, COALESCE(t.total, 0) AS num_search, CASE WHEN k.n > 0 THEN ROUND(k.w / k.n, 2) END AS zero_result_pct
FROM t LEFT JOIN k USING (country) ORDER BY t.country;
"""]
MUTANTS = [
    """
SELECT country, COALESCE(SUM(num_search), 0) AS num_search, ROUND(SUM(num_search * zero_result_pct) / NULLIF(SUM(num_search), 0), 2) AS zero_result_pct
FROM search_category GROUP BY country ORDER BY country;
""",
    """
SELECT country, COALESCE(SUM(num_search), 0) AS num_search, ROUND(AVG(zero_result_pct), 2) AS zero_result_pct
FROM search_category GROUP BY country ORDER BY country;
""",
]
S = "country VARCHAR(5), search_cat VARCHAR(10), num_search INT, zero_result_pct NUMERIC(5,1)"


def tests():
    t = [tables(search_category=table(S, [["CN", "dog", 9700000, None], ["CN", "home", 1200000, 13], ["CN", "tax", 1200, 99], ["MA", "jobs", 5000, 20],
                                          ["MA", "news", 15000, 4], ["TG", "food", None, 50], ["TG", "jobs", 0, 10]])),
         tables(search_category=table(S, [["FR", "a", 100, 10], ["FR", "b", 300, 30], ["FR", "c", None, None], ["US", "a", 50, None]]))]
    r = rng(207)
    for _ in range(6):
        rows = []
        for c in r.sample(["CN", "MA", "TG", "FR", "SN"], r.randint(1, 4)):
            for cat in r.sample(["dog", "home", "tax", "jobs", "news"], r.randint(1, 4)):
                rows.append([c, cat, r.choice([None, 0, r.randint(1, 100000), r.randint(1, 900)]), r.choice([None, round(r.uniform(0, 100), 1), 0])])
        t.append(tables(search_category=table(S, rows)))
    return t
