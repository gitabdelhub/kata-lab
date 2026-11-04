from kit import rng

ID = "d12"
NAME = "Top K Search Terms"
LANG = "python"
PARAMS = ["terms", "k"]
MINUTES = 12
TAGS = ["DSA", "comptage", "tri à clé multiple", "départage"]
IO = [("input", "array.string terms"), ("input", "integer k"), ("output", "array.string")]
SUMMARY_FR = "Les k termes les plus fréquents, du plus fréquent au moins fréquent ; à égalité, ordre alphabétique."
HINTS = ["Counter pour compter, puis sorted avec la clé (-compte, terme).", "most_common(k) ne départage pas par ordre alphabétique."]
DESC = """
<p><code>terms</code> is the list of search terms typed by users today. Your task is to return the <code>k</code> most frequent terms, most frequent first. Terms with the same count are sorted alphabetically. If there are fewer than <code>k</code> distinct terms, return them all.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(terms, k):
    # write your code here
    return []
"""
SOLUTION = """
from collections import Counter


def solution(terms, k):
    c = Counter(terms)
    return sorted(c, key=lambda w: (-c[w], w))[:k]
"""
ALT = ["""
def solution(terms, k):
    d = {}
    for w in terms: d[w] = d.get(w, 0) + 1
    out = []
    for _ in range(min(k, len(d))):
        best = None
        for w, n in d.items():
            if w in out: continue
            if best is None or n > d[best] or (n == d[best] and w < best): best = w
        out.append(best)
    return out
"""]
MUTANTS = ["""
from collections import Counter
def solution(terms, k):
    return [w for w, _ in Counter(terms).most_common(k)]
""", """
from collections import Counter
def solution(terms, k):
    c = Counter(terms)
    return sorted(c, key=lambda w: (c[w], w), reverse=True)[:k]
"""]


def tests():
    t = [{"terms": ["spark", "sql", "spark", "kafka", "sql", "dbt"], "k": 2}, {"terms": ["b", "a", "c"], "k": 2}, {"terms": ["x"], "k": 3}]
    r = rng(2012)
    for _ in range(8):
        t.append({"terms": [r.choice(["sql", "spark", "kafka", "dbt", "airflow", "bigquery"]) for _ in range(r.randint(1, 15))], "k": r.randint(1, 4)})
    return t
