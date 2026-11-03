from kit import folder, rng

ID = "p1m5"
NAME = "Rows per file"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 5
TAGS = ["lire un dossier", "_metadata.file_name"]
SUMMARY_FR = "Lis tous les CSV du dossier (avec en-tête) et renvoie le nom de chaque fichier avec son nombre de lignes de données, trié par nom de fichier."
DESC = """
<p><code>input_dir</code> is the path of a folder that contains CSV files with a header line. Every file has the same columns.</p>
<p>Return one row per file with <code>file_name</code> (the file name only, without the folder, for example <code>"day_01.csv"</code>) and <code>n_rows</code> (the number of data rows, header excluded). Files with no data row are not returned. Sort by <code>file_name</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    df = spark.read.option("header", True).csv(input_dir)
    # write your code here
    return df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, input_dir):
    df = spark.read.option("header", True).csv(input_dir)
    return (df.withColumn("file_name", F.col("_metadata.file_name"))
            .groupBy("file_name").agg(F.count("*").alias("n_rows"))
            .orderBy("file_name"))
"""
MUTANTS = ["""
from pyspark.sql import functions as F
def solve(spark, input_dir):
    df = spark.read.csv(input_dir)
    return df.withColumn("file_name", F.col("_metadata.file_name")).groupBy("file_name").agg(F.count("*").alias("n_rows")).orderBy("file_name")
"""]
HINTS = ["Chaque ligne lue connaît son fichier : F.col(\"_metadata.file_name\") (ou F.input_file_name() qui donne le chemin complet).",
         "Ensuite c'est un groupBy(\"file_name\").agg(F.count(\"*\")...)."]


def tests():
    t = [folder({"day_01.csv": "id,v\n1,a\n2,b\n", "day_02.csv": "id,v\n3,c\n"}),
         folder({"b.csv": "x\n1\n2\n3\n", "a.csv": "x\n9\n", "c.csv": "x\n"})]
    r = rng(8)
    for k in range(3):
        files = {}
        for f in range(2 + k):
            n = r.randint(1, 6)
            files[f"part_{f:02d}.csv"] = "k,amount\n" + "".join(f"{i},{r.randint(1, 99)}\n" for i in range(n))
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
