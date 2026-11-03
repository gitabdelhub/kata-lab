from kit import df

ID = "p1m2"
NAME = "Clean column names"
LANG = "pyspark"
PARAMS = ["spark", "raw_df"]
MINUTES = 5
ORDERED = False
TAGS = ["nettoyage", "toDF", "trim"]
SUMMARY_FR = "Renomme toutes les colonnes : enlève les espaces autour, mets en minuscules, remplace les espaces internes par _. Puis enlève les espaces autour de chaque valeur texte."
DESC = """
<p>A CSV export produced <code>raw_df</code> with messy column names such as <code>" Customer ID"</code> or <code>"CITY "</code>. All columns are strings.</p>
<p>Return the same rows with:</p>
<ol><li>every column name trimmed, lower-cased, and with inner spaces replaced by <code>_</code> (for example <code>" Customer ID"</code> becomes <code>customer_id</code>);</li><li>every value trimmed of surrounding spaces (null stays null).</li></ol>
<p>Keep the columns in the same order. Row order does not matter.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, raw_df: DataFrame) -> DataFrame:
    # write your code here
    return raw_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, raw_df):
    names = [c.strip().lower().replace(" ", "_") for c in raw_df.columns]
    df = raw_df.toDF(*names)
    return df.select([F.trim(F.col(c)).alias(c) for c in names])
"""
MUTANTS = ["""
from pyspark.sql import functions as F
def solve(spark, raw_df):
    names = [c.strip().lower() for c in raw_df.columns]
    df = raw_df.toDF(*names)
    return df.select([F.trim(F.col(c)).alias(c) for c in names])
"""]
HINTS = [
    "df.columns donne la liste des noms. Construis la liste propre en Python, puis df.toDF(*noms).",
    "Pour les valeurs : df.select([F.trim(F.col(c)).alias(c) for c in noms]).",
]


def tests():
    t = [
        df("` Customer ID` STRING, `CITY ` STRING, `Total Amount` STRING",
           [[" C1", "Rabat ", "10"], ["C2 ", " Fes", None]]),
        df("`ID` STRING", [["  7  "]]),
        df("`  Order  Date ` STRING, `SKU` STRING", [["2026-01-01 ", " A-1"]]),
        df("`A B C` STRING, ` x` STRING, `Y ` STRING", [[" 1", "2 ", " 3 "], [None, None, " "]]),
        df("` Customer ID` STRING", []),
    ]
    return [{"raw_df": x} for x in t]
