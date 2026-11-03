from kit import df, rng

ID = "p1m7"
NAME = "Words with their position"
LANG = "pyspark"
PARAMS = ["spark", "lines_df"]
MINUTES = 5
TAGS = ["split", "posexplode"]
SUMMARY_FR = "Coupe chaque texte en mots (séparés par un espace) et renvoie une ligne par mot avec sa position (1 pour le premier). Trie par line_id puis pos."
DESC = """
<p><code>lines_df</code> has the columns <code>line_id</code> (integer) and <code>text</code> (string). Words in <code>text</code> are separated by exactly one space.</p>
<p>Return one row per word with <code>line_id</code>, <code>pos</code> (the position of the word in its line, starting at <code>1</code>) and <code>word</code>, sorted by <code>line_id</code>, then <code>pos</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, lines_df: DataFrame) -> DataFrame:
    # write your code here
    return lines_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, lines_df):
    return (lines_df.select("line_id", F.posexplode(F.split("text", " ")).alias("p", "word"))
            .select("line_id", (F.col("p") + 1).alias("pos"), "word")
            .orderBy("line_id", "pos"))
"""
MUTANTS = ["""
from pyspark.sql import functions as F
def solve(spark, lines_df):
    return lines_df.select("line_id", F.posexplode(F.split("text", " ")).alias("pos", "word")).orderBy("line_id", "pos")
"""]
HINTS = ["F.split(\"text\", \" \") donne un tableau. F.posexplode(tableau).alias(\"p\", \"word\") donne une ligne par élément avec sa position.",
         "posexplode commence à 0 : ajoute 1."]
S = "line_id INT, text STRING"


def tests():
    t = [df(S, [[1, "big data is fun"], [2, "spark"]]), df(S, [[7, "a b a"], [3, "x y"]])]
    r = rng(12)
    words = ["data", "spark", "row", "file", "join", "sum", "key"]
    for k in range(3):
        t.append(df(S, [[i, " ".join(r.choice(words) for _ in range(r.randint(1, 6)))] for i in range(1, 5 + k)]))
    return [{"lines_df": x} for x in t]
