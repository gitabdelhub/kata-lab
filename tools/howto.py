"""Consignes pratiques générées pour chaque task, à partir de ses vraies sorties attendues.

- io_lines(t, tests) : lignes [input] / [output] en anglais, au format du vrai test,
  pour les tasks qui n'en ont pas déjà (PySpark, SQL).
- howto_html(t, tests) : l'encadré « Comment faire, exactement » en français :
  où écrire, ce que la fonction reçoit, ce qu'elle doit renvoyer (colonnes exactes,
  ordre des lignes, types), comment lancer les tests et ce qu'on doit voir.

Tout est déduit des tests eux-mêmes (colonnes, ordre, types) : l'encadré ne peut pas
contredire la correction.
"""
import json
import re


def esc(x):
    return str(x).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def c(x):
    return f"<code>{esc(x)}</code>"


def user_func(t):
    """Nom et paramètres de la fonction que l'élève complète (lus dans le code de départ)."""
    if t["lang"] == "sql":
        return None, None
    src = t["starter"]
    if t.get("project"):
        main = t["project"]["main"]
        m = re.search(r"# ==== " + re.escape(main) + r" ====\n(.*?)(?=\n# ==== |\Z)", src, re.S)
        src = m.group(1) if m else src
    m = re.search(r"^def (\w+)\((.*?)\)", src, re.M | re.S)
    if not m:
        return t["entry"], ", ".join(t["params"])
    args = [a.split(":")[0].split("=")[0].strip() for a in m.group(2).split(",") if a.strip()]
    return m.group(1), ", ".join(args)


def tables_of(tests):
    return [x["expected"] for x in tests if "columns" in x["expected"]]


def kinds(tests):
    """Ce qu'on trouve dans les sorties attendues : booléens, null, décimaux, dates."""
    k = set()
    for e in tables_of(tests):
        for r in e["rows"]:
            for v in r:
                if v is None:
                    k.add("null")
                elif isinstance(v, bool):
                    k.add("bool")
                elif isinstance(v, float) and abs(v - round(v)) > 1e-9:
                    k.add("float")
                elif isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
                    k.add("date")
                elif isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", v):
                    k.add("ts")
    return k


def multi_rows(tests):
    return any(len(e["rows"]) > 1 for e in tables_of(tests))


def param_kind(t, p, inp):
    v = inp.get(p)
    if isinstance(v, dict) and "__df__" in v:
        return "df"
    if isinstance(v, dict) and "__dir__" in v:
        return "dir"
    return "value"


# ---------------------------------------------------------------- [input] / [output]
def io_lines(t, tests):
    if t["io"] or t["wrapper"] or not tests:
        return []
    inp, exp = tests[0]["input"], tests[0]["expected"]
    out = []
    if t["lang"] == "sql":
        out.append(("input", "tables " + ", ".join(f"<code>{esc(n)}</code>" for n in inp["tables"])))
    else:
        for p in t["params"]:
            if p == "spark":
                continue
            k = param_kind(t, p, inp)
            if k == "df":
                out.append(("input", f"DataFrame {esc(p)}"))
            elif k == "dir":
                out.append(("input", f"string {esc(p)} (the path of a folder)"))
    if "columns" in exp:
        cols = ", ".join(f"<code>{esc(x)}</code>" for x in exp["columns"])
        what = "the result of one query" if t["lang"] == "sql" else "DataFrame"
        if not multi_rows(tests):
            order = ""
        elif t["ordered"]:
            order = "; rows in the order given by the statement"
        else:
            order = "; row order does not matter"
        out.append(("output", f"{what} with exactly the columns {cols}, in this order{order}"))
    return out


# ---------------------------------------------------------------- encadré français
FILE = {"pyspark": "solution.py", "sql": "query.sql", "python": "solution.py"}


def li(items):
    return "<ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>"


def where_block(t, tests):
    lang, inp = t["lang"], tests[0]["input"]
    fn, args = user_func(t)
    steps = []
    if lang == "sql":
        names = ", ".join(c(n) for n in inp["tables"])
        steps.append(f"Écris dans l'éditeur à droite, fichier {c('query.sql')}. Efface le commentaire de départ si tu veux.")
        steps.append(f"Écris <b>une seule requête</b> qui commence par {c('SELECT')} (ou {c('WITH')}). "
                     f"Les tables {names} existent déjà, remplies avec les données du test : pas de {c('CREATE TABLE')} ni d'{c('INSERT')}.")
        steps.append(f"Le moteur est PostgreSQL. Si tu écris plusieurs requêtes, seul le résultat de la dernière est noté.")
        return steps
    if t.get("project"):
        main = t["project"]["main"]
        others = [f for f in t["project"]["files"] if f != main]
        steps.append(f"Le code est réparti en plusieurs fichiers, listés à gauche de l'éditeur sous <b>Code</b>. Clique sur un nom pour l'ouvrir.")
        steps.append(f"Les tests appellent {c(fn + '(' + args + ')')}, dans {c(main)}. "
                     f"Écris les fonctions d'aide dans {', '.join(c(o) for o in others)} et importe-les comme dans le code de départ "
                     f"({c('from pipeline.… import …')}) : ces imports marchent ici.")
    else:
        steps.append(f"Écris dans l'éditeur à droite, fichier {c(FILE[lang])}.")
        steps.append(f"Complète la fonction {c(fn + '(' + args + ')')}. Garde son nom et ses paramètres : "
                     f"ce sont les tests qui l'appellent, avec leurs propres données. N'écris pas d'appel à la fonction toi-même.")
    if lang == "pyspark":
        dfs = [p for p in t["params"] if p != "spark" and param_kind(t, p, inp) == "df"]
        dirs = [p for p in t["params"] if p != "spark" and param_kind(t, p, inp) == "dir"]
        if "spark" in t["params"]:
            steps.append(f"{c('spark')} est une SparkSession déjà prête : ne crée pas la tienne.")
        if dfs:
            steps.append(f"{', '.join(c(p) for p in dfs)} {'est un DataFrame déjà chargé' if len(dfs) == 1 else 'sont des DataFrames déjà chargés'} : "
                         f"ses colonnes sont celles de l'énoncé (onglet <b>Input</b> d'un test pour les voir).")
        for p in dirs:
            steps.append(f"{c(p)} est le <b>chemin d'un dossier</b> (une chaîne). Ses fichiers sont listés à gauche de l'éditeur sous <b>Files</b> : "
                         f"clique sur un fichier pour le lire (lecture seule), puis sur {c(t['project']['main'].split('/')[-1] if t.get('project') else FILE[lang])} pour revenir à ton code. "
                         f"Lis les fichiers à partir de {c(p)}, jamais d'un chemin écrit à la main : chaque test donne un autre dossier.")
    if lang == "python" and t.get("wrapper"):
        if "class TreeNode" in t["wrapper"] or "class ListNode" in t["wrapper"]:
            steps.append("La classe de l'énoncé (" + c("TreeNode" if "TreeNode" in t["wrapper"] else "ListNode")
                         + ") est déjà définie : ne la réécris pas. Dans les tests, les listes et les arbres sont affichés comme des listes Python.")
        else:
            steps.append("Les fonctions décrites dans l'énoncé (l'API) sont fournies par les tests, qui les passent à ta fonction : tu écris seulement ta fonction et tu les appelles.")
    return steps


def return_block(t, tests):
    lang, exp = t["lang"], tests[0]["expected"]
    steps = []
    if lang != "sql":
        steps.append(f"Ta fonction doit <b>renvoyer</b> le résultat avec {c('return')}. "
                     f"Un {c('print')} ou un {c('show()')} ne compte pas : il sort seulement dans l'onglet <b>Console Output</b>."
                     if lang == "pyspark" else
                     f"Ta fonction doit <b>renvoyer</b> le résultat avec {c('return')}. "
                     f"Un {c('print')} ne compte pas : il sort seulement dans l'onglet <b>Console Output</b>.")
    if "columns" in exp and not (lang == "pyspark" and t.get("wrapper")):
        cols = ", ".join(c(x) for x in exp["columns"])
        n = len(exp["columns"])
        what = "Le résultat de ta requête" if lang == "sql" else "Le DataFrame renvoyé"
        steps.append(f"{what} doit avoir <b>exactement {n} colonne{'s' if n > 1 else ''}</b>, avec ces noms et dans cet ordre : {cols}. "
                     f"Une colonne en plus (une colonne de calcul oubliée), un nom différent ou un autre ordre et le test est faux, même si les valeurs sont justes. "
                     + (f"Nomme chaque colonne calculée avec {c('AS')}." if lang == "sql" else f"Finis par un {c('select(...)')} de ces colonnes."))
        if multi_rows(tests):
            if t["ordered"]:
                steps.append("<b>L'ordre des lignes compte</b> : trie exactement comme l'énoncé le demande"
                             + (f" ({c('ORDER BY')} à la fin de la requête)." if lang == "sql" else f" ({c('orderBy')} à la fin)."))
            else:
                steps.append("L'ordre des lignes ne compte pas : les tests trient les deux tables avant de comparer.")
        k = kinds(tests)
        typ = []
        if "float" in k:
            typ.append("les nombres sont comparés à 0,000001 près : arrondis seulement là où l'énoncé le demande, et au nombre de décimales demandé")
        if "bool" in k:
            typ.append(f"les colonnes {c('true')} / {c('false')} doivent être de vrais booléens, pas 1 / 0 ni du texte")
        if "null" in k:
            typ.append(f"une case vide attendue s'écrit {c('null')} : ce n'est ni {c('0')} ni une chaîne vide")
        if "date" in k or "ts" in k:
            typ.append("les dates s'affichent " + ("AAAA-MM-JJ" if "date" in k else "") + (" et " if "date" in k and "ts" in k else "")
                       + ("AAAA-MM-JJ HH:MM:SS pour une date avec heure" if "ts" in k else ""))
        if typ:
            steps.append("Valeurs : " + " ; ".join(typ) + ".")
    elif lang == "pyspark" and t.get("wrapper"):
        steps.append("Renvoie exactement ce que demande la partie <b>Output</b> de l'énoncé. Dans les résultats des tests, les DataFrames renvoyés "
                     f"sont montrés dans une seule table, avec une colonne {c('output')} qui dit d'où vient chaque ligne.")
    elif lang == "python":
        v = exp.get("value")
        if t.get("wrapper") and isinstance(v, dict) and "result" in v:
            extra = f" et {c('sleeps')} les attentes demandées" if "sleeps" in v else ""
            steps.append(f"Dans les résultats des tests, {c('result')} est ce que ta fonction a renvoyé, et {c('calls')} la liste des appels qu'elle a faits à l'API{extra}. "
                         "Les deux doivent être identiques à « Expected return value » : un appel en trop ou dans le mauvais ordre suffit pour que le test soit faux.")
        else:
            kind = {list: "une liste", dict: "un dictionnaire", bool: f"un booléen ({c('True')} ou {c('False')})", int: "un nombre entier",
                    float: "un nombre", str: "une chaîne de caractères"}.get(type(v))
            if kind and not t.get("wrapper"):
                steps.append(f"Ici, la valeur attendue est {kind} : compare ce que tu renvoies à « Expected return value » dans les résultats.")
            steps.append("La comparaison est exacte (même type, mêmes valeurs, même ordre dans une liste), sauf les nombres décimaux, comparés à 0,000001 près.")
    return steps


def run_block(t, tests):
    nv = min(t["visible_n"], len(tests))
    nh = len(tests) - nv
    steps = []
    if t["lang"] == "pyspark":
        steps.append("Spark tourne dans ton Codespace : au premier RUN TESTS de la séance, attends qu'il soit prêt (1 à 2 minutes). Ensuite chaque lancement prend quelques secondes.")
    steps.append(f"Clique <b>RUN TESTS</b> (ou {c('Ctrl + Entrée')}) : " + (f"tes {nv} tests visibles tournent." if nv > 1 else "ton test visible tourne."))
    steps.append(f"Quand c'est bon, tu vois en vert <b>« Tests passed: {nv}/{nv}. »</b>. Sinon, ouvre le test marqué <b>Wrong answer</b> : "
                 "compare « Expected return value » et « Your return value », et clique <b>VIEW DIFF</b> pour colorer les cases différentes. "
                 "<b>Runtime error</b> veut dire que ton code a planté : le message est dans le test.")
    steps.append(f"Clique <b>SUBMIT</b> : ta note sur 100 compte aussi {nh} test{'s' if nh > 1 else ''} caché{'s' if nh > 1 else ''}. "
                 "Soumets dès que quelques tests passent, puis améliore et resoumets : c'est la dernière soumission qui compte.")
    return steps


def howto_html(t, tests):
    if not tests:
        return ""
    parts = [
        ("Où écrire", where_block(t, tests)),
        ("Ce que tu dois renvoyer", return_block(t, tests)),
        ("Lancer et vérifier", run_block(t, tests)),
    ]
    body = "".join(f"<h5>{h}</h5>{li(s)}" for h, s in parts if s)
    return body

