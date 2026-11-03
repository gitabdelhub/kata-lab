from kit import table, tables, rng

ID = "p1m6"
NAME = "Conversion rate per channel"
LANG = "sql"
MINUTES = 5
TAGS = ["division entière", "ROUND numeric", "COUNT FILTER"]
SUMMARY_FR = "Par canal : nombre de visites, nombre d'achats, taux = achats / visites en pourcentage arrondi à 1 décimale. Attention à la division entière. Trie par canal."
DESC = """
<p>You have the table <b>visits</b>, with one row per visit of the website:</p>
<ul><li><code>visit_id</code> - the ID of the visit;</li><li><code>channel</code> - where the visitor came from (<code>"ads"</code>, <code>"seo"</code>, ...);</li><li><code>purchased</code> - <code>true</code> if the visit ended with a purchase.</li></ul>
<p>Your task is to return, for each channel, <code>channel</code>, <code>visits</code>, <code>purchases</code> and <code>conversion_pct</code>, the percentage of visits with a purchase rounded to 1 decimal. Sort by <code>channel</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
SELECT channel,
       COUNT(*) AS visits,
       COUNT(*) FILTER (WHERE purchased) AS purchases,
       ROUND(100.0 * COUNT(*) FILTER (WHERE purchased) / COUNT(*), 1) AS conversion_pct
FROM visits
GROUP BY channel
ORDER BY channel;
"""
MUTANTS = ["""
SELECT channel, COUNT(*) AS visits, COUNT(*) FILTER (WHERE purchased) AS purchases,
       ROUND(100 * (COUNT(*) FILTER (WHERE purchased) / COUNT(*)), 1) AS conversion_pct
FROM visits GROUP BY channel ORDER BY channel;
"""]
HINTS = ["En PostgreSQL, entier / entier = division entière : 1 / 3 vaut 0. Multiplie d'abord par 100.0.",
         "ROUND(x, 1) marche sur numeric : 100.0 * a / b est numeric, c'est bon. ROUND(double precision, 1) n'existe pas."]
C = "visit_id INT, channel TEXT, purchased BOOLEAN"


def tests():
    t = [tables(visits=table(C, [[1, "ads", True], [2, "ads", False], [3, "ads", False], [4, "seo", True], [5, "seo", True], [6, "email", False]])),
         tables(visits=table(C, [[1, "social", False], [2, "social", True], [3, "social", False]]))]
    r = rng(10)
    for k in range(4):
        t.append(tables(visits=table(C, [[i, r.choice(["ads", "seo", "email", "social"]), r.random() < 0.3] for i in range(20 + 10 * k)])))
    return t
