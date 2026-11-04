from kit import rng

ID = "d26"
NAME = "Table Name Autocomplete"
LANG = "python"
PARAMS = ["tables", "prefixes"]
MINUTES = 18
TAGS = ["DSA", "trie (arbre de préfixes)", "dictionnaire de dictionnaires", "autocomplétion"]
IO = [("input", "array.string tables"), ("input", "array.string prefixes"), ("output", "array.array.string")]
SUMMARY_FR = "Pour chaque préfixe tapé, proposer au plus 3 noms de tables qui commencent par ce préfixe, les plus petits par ordre alphabétique. Construis un trie."
HINTS = ["Trie = dict de dicts, un niveau par lettre. Stocke dans chaque nœud la liste triée des 3 plus petits mots qui passent par là.", "Trie les noms (et enlève les doublons) avant de les insérer : il suffit alors de garder les 3 premiers arrivés dans chaque nœud."]
DESC = """
<p>A SQL editor suggests table names while you type. You are given <code>tables</code> (names can repeat; count each name once) and the <code>prefixes</code> typed by users. Your task is to return, for each prefix, the list of at most <b>3</b> table names that start with this prefix, the smallest first in alphabetical order (an empty list if none).</p>
<p>Build a trie (prefix tree) once, so each query is fast even with many tables.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(tables, prefixes):
    # write your code here
    return []
"""
SOLUTION = """
def solution(tables, prefixes):
    root = {"#": []}
    for w in sorted(set(tables)):
        node = root
        if len(node["#"]) < 3:
            node["#"].append(w)
        for ch in w:
            node = node.setdefault(ch, {"#": []})
            if len(node["#"]) < 3:
                node["#"].append(w)
    out = []
    for p in prefixes:
        node = root
        for ch in p:
            node = node.get(ch)
            if node is None:
                break
        out.append(list(node["#"]) if node else [])
    return out
"""
ALT = ["""
def solution(tables, prefixes):
    ws = sorted(set(tables))
    return [[w for w in ws if w.startswith(p)][:3] for p in prefixes]
"""]
MUTANTS = ["""
def solution(tables, prefixes):
    return [[w for w in sorted(tables) if w.startswith(p)][:3] for p in prefixes]
""", """
def solution(tables, prefixes):
    ws = sorted(set(tables))
    return [[w for w in ws if w.startswith(p)] for p in prefixes]
""", """
def solution(tables, prefixes):
    ws = sorted(set(tables))
    return [[w for w in ws if p in w][:3] for p in prefixes]
"""]


def tests():
    t = [{"tables": ["orders", "order_items", "orgs", "customers", "orders_archive", "ops_log"], "prefixes": ["or", "ord", "c", "x", "", "o"]},
         {"tables": ["a", "a", "ab"], "prefixes": ["a", "ab", "abc"]}]
    r = rng(2026)
    for _ in range(7):
        ws = ["".join(r.choice("abc") for _ in range(r.randint(1, 4))) for _ in range(r.randint(1, 12))]
        t.append({"tables": ws, "prefixes": ["".join(r.choice("abc") for _ in range(r.randint(0, 3))) for _ in range(r.randint(1, 5))]})
    return t
