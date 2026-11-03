from kit import folder, rng

ID = "p2x3"
NAME = "Latest Customer Record"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 22
TAGS = ["dossiers par date", "row_number", "départage", "suppression logique"]
SUMMARY_FR = "Des mises à jour de clients arrivent dans des dossiers par jour (dt=YYYY-MM-DD). Garder pour chaque client la version la plus récente (date du dossier, puis updated_at, puis nom de fichier), et enlever les clients dont la dernière version est supprimée (deleted = true)."
HINTS = ["La date vient du nom du dossier dt=YYYY-MM-DD : regexp_extract sur input_file_name() ou sur le chemin quand tu lis chaque fichier.",
         "Window.partitionBy('customer_id').orderBy(dt desc, updated_at desc, file desc) puis row_number() == 1, et SEULEMENT après, filtre deleted.",
         "Si tu filtres deleted avant de prendre la dernière version, un client supprimé réapparaît avec une ancienne version."]
DESC = """
<p>A CRM sends changes of customer records every day. The files are stored in <code>input_dir</code> with this layout:</p>
<pre class="exv">input_dir/
  dt=&lt;YYYY-MM-DD&gt;/
    &lt;name&gt;.csv</pre>
<p>Each file has a header and the columns <code>customer_id</code>, <code>email</code>, <code>city</code>, <code>updated_at</code> (timestamp written as <code>yyyy-MM-dd HH:mm:ss</code>) and <code>deleted</code> (<code>true</code> or <code>false</code>). A customer can appear in many files and many days.</p>
<p>The <b>latest version</b> of a customer is chosen with these rules, in this order:</p>
<ol><li>the version from the most recent <code>dt</code> folder wins;</li><li>inside the same folder, the version with the most recent <code>updated_at</code> wins;</li><li>if there is still a tie, the version from the file whose name is the greatest in alphabetical order wins.</li></ol>
<p>If the latest version of a customer has <code>deleted = true</code>, the customer is removed from the result, even if older versions were not deleted. E-mails must be trimmed and lower-cased.</p>
<p>Your task is to return the latest version of every customer that is not deleted, with the columns <code>customer_id</code> (string), <code>email</code> (string), <code>city</code> (string) and <code>as_of</code> (date, the <code>dt</code> of the chosen version), sorted by <code>customer_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.option("header", True).csv(input_dir)
"""
SOLUTION = """
import os
from functools import reduce
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, input_dir):
    parts = []
    for folder_name in sorted(os.listdir(input_dir)):
        if not folder_name.startswith("dt="):
            continue
        for name in sorted(os.listdir(os.path.join(input_dir, folder_name))):
            if not name.endswith(".csv"):
                continue
            d = spark.read.option("header", True).csv(os.path.join(input_dir, folder_name, name))
            parts.append(d.select(
                "customer_id", "email", "city",
                F.to_timestamp("updated_at", "yyyy-MM-dd HH:mm:ss").alias("updated_at"),
                (F.lower(F.trim("deleted")) == "true").alias("deleted"),
                F.to_date(F.lit(folder_name[3:])).alias("as_of"),
                F.lit(name).alias("file")))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    w = Window.partitionBy("customer_id").orderBy(F.col("as_of").desc(), F.col("updated_at").desc(), F.col("file").desc())
    latest = df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").filter(~F.col("deleted"))
    return (latest.select("customer_id", F.lower(F.trim("email")).alias("email"), "city", "as_of")
            .orderBy("customer_id"))
"""
MUTANTS = [
    """
import os
from functools import reduce
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, input_dir):
    parts = []
    for fo in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, fo))):
            if not name.endswith(".csv"): continue
            d = spark.read.option("header", True).csv(os.path.join(input_dir, fo, name))
            parts.append(d.select("customer_id", "email", "city", F.to_timestamp("updated_at").alias("updated_at"), (F.lower(F.trim("deleted")) == "true").alias("deleted"), F.to_date(F.lit(fo[3:])).alias("as_of"), F.lit(name).alias("file")))
    df = reduce(lambda a, b: a.unionByName(b), parts).filter(~F.col("deleted"))
    w = Window.partitionBy("customer_id").orderBy(F.col("as_of").desc(), F.col("updated_at").desc(), F.col("file").desc())
    return df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").select("customer_id", F.lower(F.trim("email")).alias("email"), "city", "as_of").orderBy("customer_id")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, input_dir):
    parts = []
    for fo in sorted(os.listdir(input_dir)):
        for name in sorted(os.listdir(os.path.join(input_dir, fo))):
            if not name.endswith(".csv"): continue
            d = spark.read.option("header", True).csv(os.path.join(input_dir, fo, name))
            parts.append(d.select("customer_id", "email", "city", F.to_timestamp("updated_at").alias("updated_at"), (F.lower(F.trim("deleted")) == "true").alias("deleted"), F.to_date(F.lit(fo[3:])).alias("as_of"), F.lit(name).alias("file")))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    w = Window.partitionBy("customer_id").orderBy(F.col("updated_at").desc(), F.col("file").desc())
    return df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").filter(~F.col("deleted")).select("customer_id", F.lower(F.trim("email")).alias("email"), "city", "as_of").orderBy("customer_id")
""",
]
H = "customer_id,email,city,updated_at,deleted"


def csv(rows):
    return H + "\n" + "\n".join(",".join(r) for r in rows) + "\n"


def tests():
    t = [folder({"dt=2026-03-01/a.csv": csv([["c1", "A@Mail.com ", "Rabat", "2026-03-01 09:00:00", "false"], ["c2", "b@mail.com", "Fes", "2026-03-01 10:00:00", "false"]]),
                 "dt=2026-03-02/a.csv": csv([["c1", "a@mail.com", "Casablanca", "2026-03-01 23:00:00", "false"], ["c2", "b@mail.com", "Fes", "2026-03-02 08:00:00", "true"]]),
                 "dt=2026-03-02/b.csv": csv([["c3", "c@mail.com", "Lome", "2026-03-02 12:00:00", "false"]])}),
         folder({"dt=2026-04-10/x.csv": csv([["k9", "OLD@x.io", "Tanger", "2026-04-10 10:00:00", "false"]]),
                 "dt=2026-04-10/y.csv": csv([["k9", "new@x.io", "Agadir", "2026-04-10 10:00:00", "FALSE"]]),
                 "dt=2026-04-09/z.csv": csv([["k9", "zz@x.io", "Oujda", "2026-04-11 10:00:00", "false"]])})]
    r = rng(303)
    for _ in range(6):
        files = {}
        for day in r.sample(["2026-05-01", "2026-05-02", "2026-05-03"], r.randint(1, 3)):
            for f in r.sample(["a.csv", "b.csv", "c.csv"], r.randint(1, 2)):
                rows = [[f"c{cid}", r.choice(["x@m.io", " Y@M.io", "z@m.io"]), r.choice(["Rabat", "Fes", "Lome"]),
                         f"2026-05-0{r.randint(1, 3)} {r.choice(['08', '09', '10'])}:00:00", r.choice(["false", "false", "true", "False"])] for cid in r.sample(range(1, 7), r.randint(1, 5))]
                files[f"dt={day}/{f}"] = csv(rows)
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
