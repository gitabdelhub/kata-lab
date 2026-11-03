from kit import df, rng

ID = "e02t2"
NAME = "Pallet Label Grid"
LANG = "pyspark"
PARAMS = ["spark", "rows_df"]
MINUTES = 20
TAGS = ["grille", "posexplode", "collect_list ordonné", "split regex"]
DESC = """
<p>Pallets in a warehouse carry a printed label grid. Product words are printed <b>vertically</b>: each word is written from top to bottom inside one column of the grid. A column can hold several words, separated by one or more <code>#</code> characters, and <code>#</code> is also used to fill empty cells. A camera scans the grid row by row.</p>
<p>You are given <code>rows_df</code> with the columns <code>row_no</code> (integer, <code>1</code> is the top row) and <code>text</code> (string). Rows can have <b>different lengths</b>: a row that is shorter than the others has no character in the last columns, which is the same as <code>#</code>.</p>
<p>Your task is to extract every word of the grid:</p>
<ol><li>columns are numbered from left to right, starting at <code>1</code>;</li><li>read the characters of a column from the top row to the bottom row; the words of the column are the non-empty pieces between <code>#</code> characters;</li><li>words of a column are numbered from top to bottom, starting at <code>1</code>.</li></ol>
<p>Return <code>col_no</code>, <code>word_no</code> and <code>word</code>, sorted by <code>col_no</code>, then <code>word_no</code>. The rows of <code>rows_df</code> are not given in any particular order.</p>
<h4>Example</h4>{{EXAMPLE}}
<p>Column <code>1</code> reads <code>"TEA#OIL"</code> from top to bottom, so it holds two words. Row <code>1</code> is <code>"TS"</code>: it is too short to reach columns <code>3</code> and <code>4</code>, so these cells count as <code>#</code>.</p>
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, rows_df: DataFrame) -> DataFrame:
    # write your code here
    return rows_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, rows_df):
    cells = (rows_df.select("row_no", F.posexplode(F.split("text", "")).alias("pos", "ch"))
             .filter(F.col("ch") != "")
             .withColumn("col_no", F.col("pos") + 1))
    columns = (cells.groupBy("col_no")
               .agg(F.sort_array(F.collect_list(F.struct("row_no", "ch"))).alias("cells"))
               .select("col_no", F.array_join(F.transform("cells", lambda c: c["ch"]), "").alias("col_text")))
    words = (columns.select("col_no", F.posexplode(F.filter(F.split("col_text", "#+"), lambda w: w != "")).alias("p", "word"))
             .select("col_no", (F.col("p") + 1).alias("word_no"), "word"))
    return words.orderBy("col_no", "word_no")
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, rows_df):
    cells = rows_df.select("row_no", F.posexplode(F.split("text", "")).alias("pos", "ch")).filter(F.col("ch") != "").withColumn("col_no", F.col("pos") + 1)
    cols = cells.groupBy("col_no").agg(F.sort_array(F.collect_list(F.struct("row_no", "ch"))).alias("cells")).select("col_no", F.array_join(F.transform("cells", lambda c: c["ch"]), "").alias("col_text"))
    w = cols.select("col_no", F.posexplode(F.split("col_text", "#")).alias("p", "word")).filter(F.col("word") != "").select("col_no", (F.col("p") + 1).alias("word_no"), "word")
    return w.orderBy("col_no", "word_no")
""",
    """
from pyspark.sql import functions as F
def solve(spark, rows_df):
    cells = rows_df.select("row_no", F.posexplode(F.split("text", "")).alias("pos", "ch")).filter(F.col("ch") != "").withColumn("col_no", F.col("pos") + 1)
    cols = cells.groupBy("col_no").agg(F.array_join(F.collect_list("ch"), "").alias("col_text"))
    w = cols.select("col_no", F.posexplode(F.filter(F.split("col_text", "#+"), lambda x: x != "")).alias("p", "word")).select("col_no", (F.col("p") + 1).alias("word_no"), "word")
    return w.orderBy("col_no", "word_no")
""",
]
S = "row_no INT, text STRING"


def grid(columns, height, ragged, r=None):
    width = len(columns)
    g = [["#"] * width for _ in range(height)]
    for x, col in enumerate(columns):
        for y, ch in enumerate(col[:height]):
            g[y][x] = ch
    rows = []
    for y, row in enumerate(g):
        s = "".join(row)
        if ragged:
            s = s.rstrip("#") or "#"
        rows.append([y + 1, s])
    if r:
        r.shuffle(rows)
    return rows


def tests():
    t = [df(S, grid(["TEA#OIL", "S#KIWI", "#ROW#", "##FIG"], 7, True, rng(5))),
         df(S, grid(["##", "AB", "#C"], 2, True))]
    r = rng(41)
    voc = ["TEA", "OIL", "RICE", "SOAP", "MILK", "SALT", "JAM", "OAT", "FIG"]
    for k in range(6):
        cols = []
        for _ in range(3 + k):
            parts = [r.choice(voc) for _ in range(r.randint(0, 2))]
            col = "#" * r.randint(0, 2) + ("#" * r.randint(1, 2)).join(parts)
            cols.append(col)
        h = max(len(c) for c in cols) + r.randint(0, 1)
        t.append(df(S, grid(cols, max(h, 1), k % 2 == 0, r)))
    return [{"rows_df": x} for x in t]
