from kit import rng

ID = "p1m8"
NAME = "Top k words"
LANG = "python"
PARAMS = ["words", "k"]
MINUTES = 5
TAGS = ["dict", "sorted key", "Counter"]
SUMMARY_FR = "Compte les mots et renvoie les k plus fréquents sous forme [mot, nombre], du plus fréquent au moins fréquent ; à égalité, ordre alphabétique."
IO = [("input", "array.string words"), ("input", "integer k"), ("output", "array.array.string")]
DESC = """
<p>Given a list of words <code>words</code> and an integer <code>k</code>, return the <code>k</code> most frequent words as pairs <code>[word, count]</code>, from the most frequent to the least frequent. Words with the same count are sorted alphabetically. If there are fewer than <code>k</code> distinct words, return all of them.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(words, k):
    # write your code here
    return []
"""
SOLUTION = """
from collections import Counter


def solution(words, k):
    counts = Counter(words)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [[w, c] for w, c in ranked[:k]]
"""
MUTANTS = ["""
from collections import Counter
def solution(words, k):
    return [[w, c] for w, c in Counter(words).most_common(k)]
"""]
HINTS = ["Compte avec un dict (ou collections.Counter).",
         "sorted(items, key=lambda kv: (-kv[1], kv[0])) : le moins devant le nombre trie du plus grand au plus petit, puis le mot trie A à Z."]


def tests():
    t = [{"words": ["spark", "sql", "spark", "python", "sql", "spark"], "k": 2},
         {"words": ["b", "a", "c"], "k": 5}]
    r = rng(14)
    voc = ["kafka", "dbt", "spark", "sql", "etl", "s3", "bq"]
    for k in range(6):
        t.append({"words": [r.choice(voc) for _ in range(r.randint(0, 25))], "k": r.randint(1, 5)})
    t.append({"words": ["z", "y", "y", "z", "x"], "k": 2})
    return t
