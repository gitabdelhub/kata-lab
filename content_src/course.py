"""Le parcours : phases, séances, réflexes (leçons), cartes de révision, examens.

Écrit docs/content/catalog.json (appelé par tools/build.py).
"""
import json
import os

# ---------------------------------------------------------------- réflexes
# Chaque réflexe = une leçon courte (exemple guidé) + un mini-exo à faire de mémoire + 4 cartes.
REFLEXES = [
    {
        "id": "r1", "lang": "PySpark", "title": "when / otherwise", "mini": "p1m1",
        "why": "Une colonne qui dépend de conditions : c'est dans presque toutes les tasks PySpark. Au vrai test, tu ne savais plus l'écrire : on le rend automatique.",
        "body": [
            "Les <code>when</code> s'enchaînent avec un point. Spark les teste <b>dans l'ordre</b> et le premier vrai gagne.",
            "Sans <code>otherwise</code>, une ligne qui ne passe aucun <code>when</code> vaut <b>null</b>.",
            "Un <b>null ne passe aucun when</b> (null &lt; 15 n'est ni vrai ni faux). Traite-le en premier avec <code>isNull()</code>.",
            "Plusieurs conditions : <code>&amp;</code> (et), <code>|</code> (ou), <code>~</code> (non), et <b>des parenthèses autour de chaque condition</b>.",
        ],
        "code": 'from pyspark.sql import functions as F\n\nm = F.col("minutes")\ndf = df.withColumn("bucket",\n    F.when(m.isNull(), "unknown")\n     .when((m < 0) | (m > 600), "invalid")\n     .when(m < 15, "short")\n     .when(m < 45, "medium")\n     .otherwise("long"))',
        "traps": ["Oublier les parenthèses : <code>m &lt; 0 | m &gt; 600</code> plante.", "Mettre <code>m &lt; 45</code> avant <code>m &lt; 15</code> : tout devient medium.", "Écrire <code>and</code> / <code>or</code> de Python au lieu de <code>&amp;</code> / <code>|</code>."],
        "cards": [
            ["Que vaut une ligne qui ne passe aucun when, sans otherwise ?", "null"],
            ["Comment écrire « minutes est null » en PySpark ?", "F.col(\"minutes\").isNull()"],
            ["Écris la condition « a < 0 ou a > 10 ».", "(F.col(\"a\") < 0) | (F.col(\"a\") > 10), avec les parenthèses"],
            ["Dans quel ordre Spark teste les when ?", "Dans l'ordre écrit. Le premier vrai gagne."],
        ],
    },
    {
        "id": "r2", "lang": "PySpark", "title": "Nettoyer : trim, lower, try_cast", "mini": "p1m2",
        "why": "Les tasks « fichiers » donnent des données sales exprès : en-têtes avec espaces, montants avec virgule, texte à la place d'un nombre.",
        "body": [
            "Noms de colonnes : on les corrige en Python puis <code>df.toDF(*noms)</code>.",
            "Valeurs texte : <code>F.trim</code>, <code>F.lower</code>, <code>F.upper</code>, <code>F.regexp_replace(col, motif, remplacement)</code>.",
            "Conversion : avec Spark 4, <code>.cast(\"double\")</code> sur <code>\"n/a\"</code> <b>plante</b>. <code>F.expr(\"try_cast(x AS DOUBLE)\")</code> renvoie null à la place.",
            "Remplacer un null : <code>F.coalesce(col, F.lit(0.0))</code>.",
        ],
        "code": 'from pyspark.sql import functions as F\n\ndf = raw.toDF(*[c.strip().lower() for c in raw.columns])\ntxt = F.regexp_replace(F.trim("amount"), ",", ".")\ndf = (df.withColumn("status", F.lower(F.trim("status")))\n        .withColumn("_t", txt)\n        .withColumn("amount", F.coalesce(F.expr("try_cast(_t AS DOUBLE)"), F.lit(0.0)))\n        .drop("_t"))',
        "traps": ["Comparer <code>status == \"completed\"</code> sans trim ni lower.", "Utiliser cast au lieu de try_cast sur du texte sale.", "Oublier que le CSV lit tout en texte (string)."],
        "cards": [
            ["Comment renommer toutes les colonnes d'un coup ?", "df.toDF(*[c.strip().lower() for c in df.columns])"],
            ["Que fait try_cast quand la valeur n'est pas un nombre ?", "Il renvoie null (cast, lui, plante en Spark 4)."],
            ["Remplacer null par 0.0 ?", "F.coalesce(col, F.lit(0.0))"],
            ["Remplacer la virgule décimale par un point ?", "F.regexp_replace(col, \",\", \".\")"],
        ],
    },
    {
        "id": "r3", "lang": "PySpark", "title": "groupBy + agg", "mini": "p1m3",
        "why": "Le cœur des tasks data : une ligne par clé avec des compteurs, des sommes, des taux.",
        "body": [
            "<code>df.groupBy(\"cle\").agg(F.count(\"*\").alias(\"n\"), F.sum(\"x\").alias(\"total\"))</code> : toujours un <code>alias</code>.",
            "<b>Compter sous condition</b> : <code>F.sum(F.when(cond, 1).otherwise(0))</code>. <b>Sommer sous condition</b> : <code>F.sum(F.when(cond, F.col(\"x\")))</code>.",
            "<code>F.count(\"col\")</code> ignore les null, <code>F.count(\"*\")</code> compte tout. <code>F.countDistinct</code> pour les valeurs distinctes.",
            "Un taux : divise deux agrégats puis <code>F.round(..., 2)</code>. En PySpark, / donne toujours un décimal.",
        ],
        "code": 'done = F.col("status") == "completed"\nkpi = (rides.groupBy("city")\n       .agg(F.count("*").alias("rides"),\n            F.sum(F.when(done, 1).otherwise(0)).alias("completed"),\n            F.round(F.sum(F.when(done, F.col("fare"))), 2).alias("revenue"),\n            F.countDistinct("driver_id").alias("drivers"))\n       .orderBy(F.col("revenue").desc(), "city"))',
        "traps": ["Sommer fare sur toutes les lignes au lieu des seules terminées.", "Oublier le tri demandé (desc puis asc).", "Un groupe sans valeur donne null : coalesce si la consigne veut 0."],
        "cards": [
            ["Compter les lignes où status = 'cancelled' dans un agg ?", "F.sum(F.when(F.col(\"status\") == \"cancelled\", 1).otherwise(0))"],
            ["Différence entre F.count(\"x\") et F.count(\"*\") ?", "count(\"x\") ignore les null de x, count(\"*\") compte toutes les lignes."],
            ["Trier par total décroissant puis nom ?", ".orderBy(F.col(\"total\").desc(), \"nom\")"],
            ["Nombre de valeurs distinctes ?", "F.countDistinct(\"col\")"],
        ],
    },
    {
        "id": "r4", "lang": "PySpark", "title": "Window : row_number, lag", "mini": "p1m4",
        "why": "Dédoublonner, garder la dernière version, comparer à la ligne précédente : les fenêtres reviennent dans presque tous les examens.",
        "body": [
            "Une fenêtre = <code>Window.partitionBy(groupe).orderBy(tri)</code>. On l'applique avec <code>.over(w)</code> : <b>les lignes restent</b>, contrairement à groupBy.",
            "<b>Garder une ligne par groupe</b> : <code>F.row_number().over(w)</code>, puis <code>filter(\"rn = 1\")</code>. Le tri de la fenêtre décide laquelle.",
            "<b>Ligne précédente</b> : <code>F.lag(\"col\").over(w)</code> (null pour la première). Suivante : <code>F.lead</code>.",
            "<b>Somme cumulée</b> : <code>F.sum(\"x\").over(w.rowsBetween(Window.unboundedPreceding, 0))</code>.",
        ],
        "code": 'from pyspark.sql.window import Window\n\nw = Window.partitionBy("ride_id").orderBy("received_at", "source")\nrides = (raw.withColumn("rn", F.row_number().over(w))\n            .filter("rn = 1").drop("rn"))\n\nw2 = Window.partitionBy("driver_id").orderBy("started_at")\nrides = rides.withColumn("prev_start", F.lag("started_at").over(w2))',
        "traps": ["<code>dropDuplicates</code> garde une copie au hasard : pas bon si la consigne dit laquelle garder.", "Oublier <code>.desc()</code> pour « la plus récente ».", "Oublier un critère d'égalité dans orderBy (deux lignes à la même date)."],
        "cards": [
            ["Garder la ligne la plus récente par commande ?", "row_number() sur Window.partitionBy(\"order_id\").orderBy(F.col(\"updated_at\").desc()), puis rn = 1"],
            ["Valeur de la ligne précédente dans le groupe ?", "F.lag(\"col\").over(w)"],
            ["Pourquoi éviter dropDuplicates pour dédoublonner ?", "On ne choisit pas quelle copie il garde."],
            ["Différence en minutes entre deux timestamps ?", "(F.unix_timestamp(a) - F.unix_timestamp(b)) / 60"],
        ],
    },
    {
        "id": "r5", "lang": "PySpark", "title": "Lire un dossier de fichiers", "mini": "p1m5",
        "why": "Tes deux premières questions du vrai test étaient de ce type : un dossier, des fichiers, des infos dans le nom des fichiers.",
        "body": [
            "<code>spark.read.option(\"header\", True).csv(dossier)</code> lit tous les fichiers du dossier. Pour les sous-dossiers : <code>.option(\"recursiveFileLookup\", \"true\")</code>.",
            "Le nom du fichier de chaque ligne : <code>F.col(\"_metadata.file_name\")</code> (chemin complet : <code>_metadata.file_path</code>). On extrait la ville ou la date avec <code>F.regexp_extract</code>.",
            "<b>Piège majeur</b> : si les fichiers n'ont <b>pas les colonnes dans le même ordre</b>, Spark lit par position et mélange tout. Il faut alors lire <b>fichier par fichier</b> (<code>os.walk</code>) et assembler avec <code>unionByName</code>.",
            "JSON : <code>spark.read.json(dossier)</code> fusionne les champs de tous les fichiers ; un champ absent partout n'existe pas (teste <code>\"col\" in df.columns</code>).",
        ],
        "code": 'import os\nfrom functools import reduce\n\nparts = []\nfor root, _, files in os.walk(input_dir):\n    for name in sorted(files):\n        d = spark.read.option("header", True).csv(os.path.join(root, name))\n        d = d.toDF(*[c.strip().lower() for c in d.columns])\n        parts.append(d.withColumn("source", F.lit(name)))\ndf = reduce(lambda a, b: a.unionByName(b), parts)',
        "traps": ["Prendre la ville dans le contenu au lieu du nom du fichier.", "Couper le nom au premier _ alors qu'une ville peut en contenir (el_jadida).", "Lire un dossier dont les colonnes changent d'ordre en une seule fois."],
        "cards": [
            ["Nom du fichier d'origine de chaque ligne ?", "F.col(\"_metadata.file_name\")"],
            ["Les fichiers ont leurs colonnes dans des ordres différents : que faire ?", "Lire fichier par fichier, nettoyer les noms, puis unionByName."],
            ["Extraire la date de « rabat_2026-03-01.csv » ?", "F.regexp_extract(nom, r\"_(\\d{4}-\\d{2}-\\d{2})\\.csv$\", 1) puis F.to_date"],
            ["Lire aussi les sous-dossiers ?", ".option(\"recursiveFileLookup\", \"true\") ou os.walk"],
        ],
    },
    {
        "id": "r6", "lang": "SQL", "title": "Division entière et PARTITION BY", "mini": "p1m6",
        "why": "Ton erreur la plus fréquente en octobre. En PostgreSQL, 1 / 3 vaut 0 : un taux faux, tous les tests ratés.",
        "body": [
            "<b>entier / entier = division entière</b> : <code>1 / 3 = 0</code>. Écris <code>100.0 * a / b</code> ou <code>a::numeric / b</code>.",
            "<code>ROUND(x, 2)</code> marche sur <b>numeric</b>. <code>ROUND(double precision, 2)</code> n'existe pas : caste en <code>::numeric</code>.",
            "Diviser par 0 plante : <code>a / NULLIF(b, 0)</code> donne null à la place.",
            "<code>SUM(x) OVER (PARTITION BY groupe)</code> garde toutes les lignes et ajoute le total du groupe : parfait pour une part en %.",
            "<code>COUNT(*) FILTER (WHERE cond)</code> compte sous condition. <code>CASE WHEN ... THEN ... ELSE ... END</code> : n'oublie ni THEN ni END.",
        ],
        "code": "SELECT category, name, revenue,\n       ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY category), 2) AS share_pct,\n       CASE WHEN revenue >= 100 THEN 'big' ELSE 'small' END AS size\nFROM product_revenue\nORDER BY category, share_pct DESC;",
        "traps": ["<code>100 * (a / b)</code> : la division entière se fait avant la multiplication.", "<code>ROUND(avg_double, 2)</code> plante : caste en numeric.", "Oublier PARTITION BY : le total devient celui de toute la table."],
        "cards": [
            ["Combien vaut 7 / 2 en PostgreSQL ?", "3 (division entière). 7.0 / 2 vaut 3.5."],
            ["Éviter une division par zéro ?", "a / NULLIF(b, 0)"],
            ["Part d'une ligne dans le total de sa catégorie ?", "x / SUM(x) OVER (PARTITION BY category)"],
            ["Compter sous condition en SQL ?", "COUNT(*) FILTER (WHERE cond), ou SUM(CASE WHEN cond THEN 1 ELSE 0 END)"],
        ],
    },
    {
        "id": "r7", "lang": "PySpark", "title": "Grilles : split + posexplode", "mini": "p1m7",
        "why": "Le premier exo de ton vrai test : un tableau de lettres écrites en colonnes verticales. On en fait un réflexe.",
        "body": [
            "Découper un texte : <code>F.split(\"text\", \" \")</code> (mots) ou <code>F.split(\"text\", \"\")</code> (caractères).",
            "<code>F.posexplode(tableau).alias(\"pos\", \"val\")</code> : une ligne par élément, avec sa position (qui commence à 0).",
            "Une grille stockée ligne par ligne : chaque caractère a (numéro de ligne, position). <b>La position = la colonne.</b> Pour lire de droite à gauche : <code>longueur - pos</code>.",
            "<b>collect_list ne garantit pas l'ordre.</b> Collecte des <code>F.struct(\"line_no\", \"ch\")</code>, trie avec <code>F.sort_array</code>, puis <code>F.transform</code> + <code>F.array_join</code>.",
        ],
        "code": 'cells = (lines.select("line_no",\n             F.posexplode(F.split("text", "")).alias("pos", "ch")))\ncols = (cells.groupBy("pos")\n         .agg(F.sort_array(F.collect_list(F.struct("line_no", "ch"))).alias("c"))\n         .select("pos", F.array_join(F.transform("c", lambda x: x["ch"]), "").alias("text")))',
        "traps": ["Oublier que posexplode commence à 0.", "Faire confiance à l'ordre de collect_list.", "Lire la consigne trop vite : de droite à gauche ou de gauche à droite ? Dessine la grille."],
        "cards": [
            ["Une ligne par caractère avec sa position ?", "F.posexplode(F.split(\"text\", \"\")).alias(\"pos\", \"ch\")"],
            ["collect_list garde-t-il l'ordre ?", "Non. Trie des struct avec F.sort_array, puis extrais le champ."],
            ["Coller un tableau de lettres en un mot ?", "F.array_join(tableau, \"\")"],
            ["Numéro de colonne depuis la droite ?", "longueur de la ligne - pos"],
        ],
    },
    {
        "id": "r8", "lang": "Python", "title": "Méthode ENTRÉE, CLÉ, RÈGLES, SORTIE", "mini": "p1m8",
        "why": "Les tasks Python de CodeSignal sont des simulations avec beaucoup de règles. La méthode évite de se perdre.",
        "body": [
            "<b>ENTRÉE</b> : qu'est-ce que je reçois exactement (trié ? doublons ? vide ?). <b>CLÉ</b> : par quoi je regroupe (un dict). <b>RÈGLES</b> : je les numérote dans l'ordre de la consigne. <b>SORTIE</b> : format exact et tri.",
            "Regrouper : <code>d.setdefault(k, []).append(v)</code> ou <code>collections.defaultdict(list)</code>. Compter : <code>collections.Counter</code>.",
            "Trier sur plusieurs critères : <code>sorted(items, key=lambda x: (-x[1], x[0]))</code> (le moins pour décroissant sur un nombre).",
            "Avant de soumettre : teste à la main le cas vide, un seul élément, et les bornes (égal, strictement plus grand).",
        ],
        "code": "from collections import Counter\n\ndef solution(words, k):\n    counts = Counter(words)\n    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))\n    return [[w, c] for w, c in ranked[:k]]",
        "traps": ["<code>most_common</code> ne trie pas les égalités par ordre alphabétique.", "Le return dans la boucle au lieu d'après.", "Oublier la dernière session / le dernier groupe après la boucle."],
        "cards": [
            ["Les 4 mots de la méthode Python ?", "ENTRÉE, CLÉ, RÈGLES, SORTIE"],
            ["Trier par nombre décroissant puis nom croissant ?", "sorted(items, key=lambda x: (-x[1], x[0]))"],
            ["Regrouper des valeurs par clé ?", "d.setdefault(k, []).append(v)"],
            ["Les 3 cas à tester à la main avant de soumettre ?", "Vide, un seul élément, les bornes (égal / strictement)."],
        ],
    },
]

# Cartes « méthode » données dès la séance 1
METHOD_CARDS = [
    ["UMPIRE : que veut dire chaque lettre ?", "Understand (comprendre), Match (reconnaître le pattern), Plan, Implement, Review (relire), Evaluate (tester les cas limites)."],
    ["Les 2 premières minutes d'un examen ?", "Lire les 4 tasks, repérer la plus facile, et écrire le plan (le temps par task)."],
    ["Stratégie CodeSignal pour ne jamais avoir 0 ?", "Une version simple qui passe quelques tests, SUBMIT tôt, puis améliorer et resoumettre."],
    ["Que faire si une task bloque plus de 10 minutes ?", "Soumettre ce qui marche, passer à la suivante, revenir à la fin."],
]

TASKS = {r["id"]: ex for r, ex in zip(REFLEXES, ["p1x1", "p1x2", "p1x3", "p1x4", "p1x5", "p1x6", "p1x7", "p1x8"])}

SESSIONS_P1 = [
    {"id": f"p1s{i + 1}", "title": r["title"], "reflex": r["id"], "steps": [
        {"type": "review", "title": "Révision éclair", "sub": "Cartes à retrouver de mémoire", "min": 5},
        {"type": "learn", "reflex": r["id"], "title": "Réflexe du jour : " + r["title"], "sub": "Exemple guidé, puis mini-exo de mémoire", "min": 10},
        {"type": "exo", "task": TASKS[r["id"]], "title": "Exo chronométré", "sub": "Tests automatiques, note sur 100", "min": 15},
    ]}
    for i, r in enumerate(REFLEXES)
]
SESSIONS_P1.append({"id": "p1s9", "title": "Mini-examen", "steps": [
    {"type": "review", "title": "Révision éclair", "sub": "Cartes à retrouver de mémoire", "min": 5},
    {"type": "exam", "exam": "e00", "title": "Mini-examen chronométré", "sub": "2 tasks, 30 min, mode strict", "min": 30},
    {"type": "analysis", "exam": "e00", "title": "Analyse guidée", "sub": "Comprendre tes erreurs, 10 min", "min": 10},
]})

# ---------------- Phase 2 : tasks au format examen, indices qui s'effacent ----------------
# 6 semaines x 3 séances : A = PySpark (fichiers), B = SQL + Python (banques), C = examen complet (week-end)
P2_SPARK = ["p2x1", "p2x2", "p2x3", "p2x4", "p2x5", "p2x6"]
P2_SQL = ["bs03", "bs05", "bs04", "bs01", "bs07", "bs06"]
P2_PY = ["bp08", "bp01", "bp02", "bp05", "bp07", "bp03"]
P2_EXAMS = ["e04", "e05", "e06", "e07", "e08", "e09"]
REVIEW = {"type": "review", "title": "Révision éclair", "sub": "Cartes et exos ratés, de mémoire", "min": 5}


def _hints(w):
    return None if w < 2 else 1 if w < 4 else 0


import dsa as _dsa
_D = _dsa.DSA


def _dsa_session(sid, k, label):
    d = _D[k]
    return {"id": sid, "title": f"{label} · DSA {k + 1} sur 13 : {d['title']}", "steps": [
        {"type": "dsa", "dsa": d["id"], "title": "Fiche DSA : " + d["title"], "sub": "Mini cours et exemple guidé, à réécrire de mémoire", "min": 8},
        {"type": "exo", "task": d["exos"][0], "title": "Exo DSA 1", "sub": "Pattern du jour, avec les vrais tests", "min": 11},
        {"type": "exo", "task": d["exos"][1], "title": "Exo DSA 2", "sub": "Même pattern, autre problème", "min": 11}]}


SESSIONS_P2 = []
for w in range(6):
    h = _hints(w)
    lab = "tous les indices" if h is None else "1 indice" if h == 1 else "sans indice"
    SESSIONS_P2.append({"id": f"p2s{3 * w + 1}", "title": f"Semaine {w + 1} · PySpark fichiers", "steps": [
        dict(REVIEW),
        {"type": "exo", "task": P2_SPARK[w], "hints": h, "title": "Task PySpark chronométrée", "sub": "Format examen, " + lab, "min": 22}]})
    SESSIONS_P2.append({"id": f"p2s{3 * w + 2}", "title": f"Semaine {w + 1} · SQL et Python", "steps": [
        dict(REVIEW),
        {"type": "exo", "task": P2_SQL[w], "hints": h, "title": "Task SQL chronométrée", "sub": "Banque Beyond-LeetCode-SQL, " + lab, "min": 13},
        {"type": "exo", "task": P2_PY[w], "hints": h, "title": "Task Python chronométrée", "sub": "Banque exercism, " + lab, "min": 12}]})
    SESSIONS_P2.append(_dsa_session(f"p2d{w + 1}", w, f"Semaine {w + 1}"))
    SESSIONS_P2.append({"id": f"p2s{3 * w + 3}", "title": f"Semaine {w + 1} · Examen complet", "steps": [
        dict(REVIEW),
        {"type": "exam", "exam": P2_EXAMS[w], "title": "Examen complet chronométré", "sub": "4 tasks, au niveau du vrai test", "min": 70},
        {"type": "analysis", "exam": P2_EXAMS[w], "title": "Analyse guidée", "sub": "Comprendre tes erreurs, 15 min", "min": 15}]})

# ---------------- Phase 3 : examens complets en mode strict, analyse, refaire ----------------
P3_EXAMS = ["e10", "e16", "e11", "e12", "e17", "e13", "e14", "e18", "e15"]
P3_BANK = ["bs02", "bp04", "bs08", "bp06", "bs09", "bp09", "bs10", "bp10"]
SESSIONS_P3 = []
for i, ex in enumerate(P3_EXAMS):
    SESSIONS_P3.append({"id": f"p3s{2 * i + 1}", "title": f"Examen {i + 1} sur 9 · conditions réelles", "steps": [
        dict(REVIEW),
        {"type": "exam", "exam": ex, "title": "Examen complet, mode strict", "sub": "4 tasks, 70 min, pas de pause ni d'indice", "min": 70},
        {"type": "analysis", "exam": ex, "title": "Analyse guidée", "sub": "Comprendre tes erreurs, 15 min", "min": 15}]})
    steps = [{"type": "review", "title": "Refaire tes tasks ratées", "sub": "Les tests ratés de l'examen, de mémoire", "min": 20}]
    if i < len(P3_BANK):
        lang = "SQL" if P3_BANK[i].startswith("bs") else "Python"
        steps.append({"type": "exo", "task": P3_BANK[i], "hints": 0, "title": f"Task {lang} sans indice", "sub": "Banque réelle, comme le jour J", "min": 13})
    SESSIONS_P3.append({"id": f"p3s{2 * i + 2}", "title": f"Après l'examen {i + 1} · refaire", "steps": steps})
    if 6 + i < len(_D):
        SESSIONS_P3.append(_dsa_session(f"p3d{i + 1}", 6 + i, f"Semaine {i + 7}"))

PHASES = [
    {"id": "p1", "name": "Phase 1 · Réflexes", "dates": "15 au 31 janvier · 3 séances de 30 min par semaine", "opens": "2027-01-15",
     "note": "Un geste par séance : exemple guidé, mini-exo de mémoire, puis un exo chronométré.", "sessions": SESSIONS_P1},
    {"id": "p2", "name": "Phase 2 · Tasks guidées sous chrono", "dates": "1er février au 15 mars · 4 × 30 min par semaine, pendant ton PFE", "opens": "2027-02-01",
     "note": "Une task au format de l'examen par séance, PySpark, SQL et Python mélangés, avec des indices qui disparaissent peu à peu. Une séance DSA par semaine : un pattern, sa fiche et 2 exos.", "sessions": SESSIONS_P2},
    {"id": "p3", "name": "Phase 3 · Examens complets", "dates": "16 mars au 30 avril · 9 examens, chacun suivi d'une séance pour refaire", "opens": "2027-03-16",
     "note": "Un examen complet en mode strict, puis une analyse guidée et une séance pour refaire tes tests ratés. Aucun indice. Et chaque semaine, une séance DSA (patterns 7 à 13).", "sessions": SESSIONS_P3},
]

EXAMS = [
    {"id": "e00", "title": "Mini-examen · Delivery & Retention", "minutes": 30, "tasks": ["e00t1", "e00t2"], "mini": True},
    {"id": "e01", "title": "Practice Assessment · Ride Hailing Ops", "minutes": 70, "tasks": ["e01t1", "e01t2", "e01t3", "e01t4"]},
    {"id": "e02", "title": "Practice Assessment · Warehouse Files", "minutes": 70, "tasks": ["e02t1", "e02t2", "e02t3", "e02t4"]},
    {"id": "e03", "title": "Practice Assessment · Clinic Appointments", "minutes": 70, "tasks": ["e03t1", "e03t2", "e03t3", "e03t4"]},
    {"id": "e04", "title": "Practice Assessment · Food Delivery Ops", "minutes": 70, "tasks": ["e04t1", "e04t2", "e04t3", "e04t4"]},
    {"id": "e05", "title": "Practice Assessment · Payments Reconciliation", "minutes": 70, "tasks": ["e05t1", "e05t2", "e05t3", "e05t4"]},
    {"id": "e06", "title": "Practice Assessment · Service Logs", "minutes": 70, "tasks": ["e06t1", "e06t2", "e06t3", "e06t4"]},
    {"id": "e07", "title": "Practice Assessment · Energy Meters", "minutes": 70, "tasks": ["e07t1", "e07t2", "e07t3", "e07t4"]},
    {"id": "e08", "title": "Practice Assessment · Marketplace Catalog", "minutes": 70, "tasks": ["e08t1", "e08t2", "e08t3", "e08t4"]},
    {"id": "e09", "title": "Practice Assessment · Airline Operations", "minutes": 70, "tasks": ["e09t1", "e09t2", "e09t3", "e09t4"]},
    {"id": "e10", "title": "Practice Assessment · SaaS Subscriptions", "minutes": 70, "tasks": ["e10t1", "e10t2", "e10t3", "e10t4"]},
    {"id": "e11", "title": "Practice Assessment · Logistics & Payments", "minutes": 70, "tasks": ["e11t1", "e11t2", "e11t3", "e11t4"]},
    {"id": "e12", "title": "Practice Assessment · Retail Revenue", "minutes": 70, "tasks": ["e12t1", "e12t2", "e12t3", "e12t4"]},
    {"id": "e13", "title": "Practice Assessment · Customer Master Data", "minutes": 70, "tasks": ["e13t1", "e13t2", "e13t3", "e13t4"]},
    {"id": "e14", "title": "Practice Assessment · Payments Cleanup", "minutes": 70, "tasks": ["e14t1", "e14t2", "e14t3", "e14t4"]},
    {"id": "e15", "title": "Practice Assessment · Full Rehearsal", "minutes": 70, "tasks": ["e15t1", "e15t2", "e15t3", "e15t4"]},
    {"id": "e16", "title": "Practice Assessment · Retail Data Lake", "minutes": 70, "tasks": ["e16t1", "e16t2", "e16t3", "e16t4"]},
    {"id": "e17", "title": "Practice Assessment · Streaming Platform", "minutes": 70, "tasks": ["e17t1", "e17t2", "e17t3", "e17t4"]},
    {"id": "e18", "title": "Practice Assessment · Supply Chain", "minutes": 70, "tasks": ["e18t1", "e18t2", "e18t3", "e18t4"]},
]

# Temps conseillé par task (stratégie d'examen), en minutes, pour 70 min
PLAN_70 = [12, 18, 15, 22]

LINKS = [
    {"name": "PostgreSQL Exercises", "url": "https://pgexercises.com/", "what": "SQL, exercices progressifs sur une vraie base"},
    {"name": "LeetCode SQL 50", "url": "https://leetcode.com/studyplan/top-sql-50/", "what": "SQL, 50 classiques d'entretien"},
    {"name": "DataLemur", "url": "https://datalemur.com/questions", "what": "SQL d'entretien data, gratuit en partie"},
    {"name": "CodeSignal Learn", "url": "https://learn.codesignal.com/", "what": "L'interface officielle pour t'habituer"},
]


def write(out, index):
    for ex in EXAMS:
        for t in ex["tasks"]:
            assert t in index, f"task manquante : {t}"
    exams = {e["id"] for e in EXAMS}
    for ph in PHASES:
        for s in ph["sessions"]:
            for st in s["steps"]:
                if st.get("task"):
                    assert st["task"] in index, st["task"]
                if st.get("exam"):
                    assert st["exam"] in exams, st["exam"]
    exam_tasks = {t for e in EXAMS for t in e["tasks"]}
    cat = {
        "version": 1,
        "phases": PHASES,
        "reflexes": REFLEXES,
        "method_cards": METHOD_CARDS,
        "exams": EXAMS,
        "plan70": PLAN_70,
        "tasks": index,
        "library": [t for t in sorted(index) if t not in exam_tasks],
        "links": LINKS,
        "live": __import__("live").check(index),
        "dsa": __import__("dsa").check(index),
    }
    with open(os.path.join(out, "catalog.json"), "w", encoding="utf-8") as fh:
        json.dump(cat, fh, ensure_ascii=False, separators=(",", ":"))
