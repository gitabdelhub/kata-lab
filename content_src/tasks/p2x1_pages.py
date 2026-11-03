from kit import folder, rng

ID = "p2x1"
NAME = "Scanned Notebook Pages"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 22
TAGS = ["lire un dossier", "ordre des lignes", "grille verticale", "droite à gauche"]
SUMMARY_FR = "Chaque fichier .txt du dossier est une page écrite en colonnes verticales, de droite à gauche. Pour chaque page, reconstruire le texte de chaque colonne (sans les '.'), colonne 1 = la plus à droite. Les lignes d'un fichier peuvent avoir des longueurs différentes. Ignorer les fichiers qui ne finissent pas par .txt."
HINTS = ["L'ordre des lignes compte : lis chaque fichier avec open() (ou wholetext) plutôt que spark.read.text, qui ne garantit pas l'ordre.",
         "Une ligne courte n'a rien dans les colonnes de gauche : aligne les lignes à DROITE (rjust avec '.') avant de lire les colonnes.",
         "Construis une liste de tuples (page, col_no, text) en Python puis spark.createDataFrame(rows, 'page string, col_no int, text string')."]
DESC = """
<p>An archive scanned old notebooks. Each page was written <b>vertically</b>: the writer wrote every column from top to bottom and moved from the <b>rightmost</b> column to the left. The scanner saved each page as a text file in <code>input_dir</code>, one line of the page per line of the file:</p>
<pre class="exv">input_dir/
  &lt;notebook&gt;/
    &lt;page&gt;.txt</pre>
<p>Rules:</p>
<ol><li>Only files ending with <code>.txt</code> are pages; other files (for example <code>README.md</code>) are ignored. The page id is <code>&lt;notebook&gt;/&lt;page&gt;</code> without the extension, for example <code>"nb1/p01"</code>.</li>
<li>Empty cells are written with a dot <code>"."</code>. Trailing spaces at the end of a line must be removed, and empty lines are ignored.</li>
<li>Lines can have <b>different lengths</b>. The text is aligned on the <b>right</b> side of the page: a short line has no character in the leftmost columns, which is the same as a dot.</li>
<li>Columns are numbered from right to left: the last character of the longest line is in column <code>1</code>.</li>
<li>The text of a column is made of its characters read from the top line to the bottom line, without the dots. Columns that contain only dots are not returned.</li></ol>
<p>Your task is to return a DataFrame with the columns <code>page</code> (string), <code>col_no</code> (integer) and <code>text</code> (string), sorted by <code>page</code>, then <code>col_no</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>In <code>nb1/p01</code>, the last characters of the lines, from top to bottom, are <code>S</code>, <code>P</code>, <code>A</code>, <code>R</code>, <code>K</code>. The second line <code>QP</code> is short: it is aligned to the right, so <code>Q</code> is in column <code>2</code>, not in column <code>3</code>.</p>
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.text(input_dir)
"""
SOLUTION = """
import os


def solve(spark, input_dir):
    rows = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if not name.endswith(".txt"):
                continue
            path = os.path.join(root, name)
            page = os.path.relpath(path, input_dir)[:-4].replace(os.sep, "/")
            with open(path, encoding="utf-8") as fh:
                lines = [l.rstrip() for l in fh.read().split("\\n")]
            lines = [l for l in lines if l]
            if not lines:
                continue
            width = max(len(l) for l in lines)
            grid = [l.rjust(width, ".") for l in lines]
            for k in range(width):
                col = width - 1 - k
                text = "".join(l[col] for l in grid if l[col] != ".")
                if text:
                    rows.append((page, k + 1, text))
    return spark.createDataFrame(rows, "page string, col_no int, text string").orderBy("page", "col_no")
"""
MUTANTS = [
    """
import os
def solve(spark, input_dir):
    rows = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if not name.endswith(".txt"):
                continue
            path = os.path.join(root, name)
            page = os.path.relpath(path, input_dir)[:-4]
            lines = [l.rstrip() for l in open(path).read().split("\\n") if l.strip()]
            width = max(len(l) for l in lines)
            grid = [l.ljust(width, ".") for l in lines]
            for k in range(width):
                text = "".join(l[width - 1 - k] for l in grid if l[width - 1 - k] != ".")
                if text:
                    rows.append((page, k + 1, text))
    return spark.createDataFrame(rows, "page string, col_no int, text string").orderBy("page", "col_no")
""",
    """
import os
def solve(spark, input_dir):
    rows = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if not name.endswith(".txt"):
                continue
            path = os.path.join(root, name)
            page = os.path.relpath(path, input_dir)[:-4]
            lines = [l.rstrip() for l in open(path).read().split("\\n") if l.strip()]
            width = max(len(l) for l in lines)
            grid = [l.rjust(width, ".") for l in lines]
            for k in range(width):
                text = "".join(l[k] for l in grid if l[k] != ".")
                if text:
                    rows.append((page, k + 1, text))
    return spark.createDataFrame(rows, "page string, col_no int, text string").orderBy("page", "col_no")
""",
    """
import os
def solve(spark, input_dir):
    rows = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            path = os.path.join(root, name)
            page = os.path.relpath(path, input_dir).rsplit(".", 1)[0]
            lines = [l.rstrip() for l in open(path).read().split("\\n") if l.strip()]
            width = max(len(l) for l in lines)
            grid = [l.rjust(width, ".") for l in lines]
            for k in range(width):
                text = "".join(l[width - 1 - k] for l in grid if l[width - 1 - k] != ".")
                if text:
                    rows.append((page, k + 1, text))
    return spark.createDataFrame(rows, "page string, col_no int, text string").orderBy("page", "col_no")
""",
]


def page(cols, trailing=False):
    """cols : textes des colonnes, colonne 1 (droite) d'abord. Écrit la page ligne par ligne, alignée à droite."""
    h = max(len(c) for c in cols)
    grid = [c.ljust(h, ".") for c in cols]
    lines = ["".join(grid[k][i] for k in reversed(range(len(cols)))) for i in range(h)]
    lines = [l.lstrip(".") if i % 2 and len(l) > 1 else l for i, l in enumerate(lines)]
    return "\n".join(l + ("   " if trailing and i == 0 else "") for i, l in enumerate(lines)) + "\n"


def tests():
    t = [folder({"nb1/p01.txt": "D.S\nQP\nT.A\nA.R\n..K\n", "nb1/p02.txt": page(["ETL", "SQL"]), "nb1/README.md": "scanned by robot 7\n"}),
         folder({"z/p9.txt": "\n  \nAB  \n.C\n\n", "a/p1.txt": page(["HELLO", "", "HI"], True)})]
    r = rng(301)
    words = ["DATA", "SPARK", "FILE", "JOIN", "WINDOW", "LAG", "ROW", "SQL", "NULL", "TRIM"]
    for k in range(6):
        files = {}
        for nb in r.sample(["nb1", "nb2", "nb3"], r.randint(1, 2)):
            for p in r.sample(["p01", "p02", "p03", "p10"], r.randint(1, 3)):
                cols = [r.choice(words + [""]) for _ in range(r.randint(1, 5))]
                if not any(cols):
                    cols[0] = "OK"
                files[f"{nb}/{p}.txt"] = page(cols, r.random() < 0.3)
        if k % 2:
            files["notes.csv"] = "a,b\n1,2\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
