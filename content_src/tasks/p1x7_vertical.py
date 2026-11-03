from kit import df, rng

ID = "p1x7"
NAME = "Vertical notebook decoder"
LANG = "pyspark"
PARAMS = ["spark", "lines_df"]
MINUTES = 20
TAGS = ["split", "posexplode", "collect_list ordonné", "grille"]
SUMMARY_FR = "Le texte est écrit en colonnes verticales : on lit chaque colonne de haut en bas, et les colonnes de droite à gauche (comme un cahier japonais). Les lignes du DataFrame sont les lignes de la page. Reconstruis le texte de chaque colonne (sans les points de remplissage), colonne 1 = la plus à droite."
DESC = """
<p>A scanned notebook page was written <b>vertically</b>: the writer wrote each column from top to bottom, and moved from the <b>rightmost</b> column to the left, like in a Japanese notebook. The scanner, however, stored the page line by line, from top to bottom.</p>
<p><code>lines_df</code> has the columns <code>line_no</code> (integer, <code>1</code> is the top line) and <code>text</code> (string). All lines have the same length. Empty cells of the page are written with a dot <code>"."</code>.</p>
<p>Your task is to rebuild what the writer wrote, one row per column of the page:</p>
<ol><li>columns are numbered from right to left: the rightmost character of each line belongs to column <code>1</code>;</li><li>the text of a column is made of its characters read from the top line to the bottom line, with the dots removed;</li><li>columns that contain only dots are not returned.</li></ol>
<p>Return <code>col_no</code> and <code>text</code>, sorted by <code>col_no</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>The rightmost characters, read from top to bottom, are <code>D</code>, <code>A</code>, <code>T</code>, <code>A</code>: column <code>1</code> is <code>"DATA"</code>.</p>
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, lines_df: DataFrame) -> DataFrame:
    # write your code here
    return lines_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, lines_df):
    width = F.length("text")
    cells = (lines_df
             .select("line_no", width.alias("w"), F.posexplode(F.split("text", "")).alias("pos", "ch"))
             .withColumn("col_no", F.col("w") - F.col("pos"))
             .filter(F.col("ch") != "."))
    return (cells.groupBy("col_no")
            .agg(F.sort_array(F.collect_list(F.struct("line_no", "ch"))).alias("cells"))
            .select("col_no", F.array_join(F.transform("cells", lambda c: c["ch"]), "").alias("text"))
            .orderBy("col_no"))
"""
MUTANTS = ["""
from pyspark.sql import functions as F
def solve(spark, lines_df):
    cells = lines_df.select("line_no", F.posexplode(F.split("text", "")).alias("pos", "ch")).withColumn("col_no", F.col("pos") + 1).filter(F.col("ch") != ".")
    return cells.groupBy("col_no").agg(F.sort_array(F.collect_list(F.struct("line_no", "ch"))).alias("cells")).select("col_no", F.array_join(F.transform("cells", lambda c: c["ch"]), "").alias("text")).orderBy("col_no")
""", """
from pyspark.sql import functions as F
def solve(spark, lines_df):
    w = F.length("text")
    cells = lines_df.select("line_no", w.alias("w"), F.posexplode(F.split("text", "")).alias("pos", "ch")).withColumn("col_no", F.col("w") - F.col("pos"))
    return cells.groupBy("col_no").agg(F.sort_array(F.collect_list(F.struct("line_no", "ch"))).alias("cells")).select("col_no", F.array_join(F.transform("cells", lambda c: c["ch"]), "").alias("text")).orderBy("col_no")
"""]
HINTS = [
    "Découpe chaque ligne en caractères : F.posexplode(F.split(\"text\", \"\")) donne (pos, ch). pos = 0 à gauche.",
    "Numéro de colonne depuis la droite : longueur - pos. Puis groupBy(\"col_no\").",
    "collect_list ne garantit pas l'ordre. Collecte des struct(line_no, ch), trie avec F.sort_array, puis F.transform(..., lambda c: c[\"ch\"]) et F.array_join(..., \"\").",
]
S = "line_no INT, text STRING"


def page(cols, height):
    # cols : liste de mots, colonne 1 = la plus à droite
    width = len(cols)
    grid = [["."] * width for _ in range(height)]
    for j, word in enumerate(cols):
        x = width - 1 - j
        for i, ch in enumerate(word[:height]):
            grid[i][x] = ch
    return [[i + 1, "".join(row)] for i, row in enumerate(grid)]


def tests():
    t = [df(S, page(["DATA", "SPARK", "SQL"], 5)), df(S, page(["HI", "", "YO"], 3))]
    r = rng(13)
    vocab = ["ROW", "JOIN", "TEA", "MINT", "CITY", "RIDE", "FILE", "KEY", "SUM", "AB", "X"]
    for k in range(5):
        cols = [r.choice(vocab + [""]) for _ in range(3 + k)]
        rows = page(cols, max(len(c) for c in cols) + r.randint(0, 2) or 1)
        r.shuffle(rows)
        t.append(df(S, rows))
    return [{"lines_df": x} for x in t]
