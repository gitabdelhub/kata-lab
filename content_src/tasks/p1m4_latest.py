from kit import df, rng

ID = "p1m4"
NAME = "Latest status per order"
LANG = "pyspark"
PARAMS = ["spark", "events_df"]
MINUTES = 5
ORDERED = False
TAGS = ["Window", "row_number"]
SUMMARY_FR = "Pour chaque commande, garde seulement l'événement le plus récent (updated_at le plus grand). Ordre des lignes libre."
DESC = """
<p><code>events_df</code> stores every status change of every order: <code>order_id</code> (string), <code>status</code> (string) and <code>updated_at</code> (timestamp). Timestamps of one order are all different.</p>
<p>Return one row per order with its latest status: columns <code>order_id</code>, <code>status</code>, <code>updated_at</code>. Row order does not matter.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, events_df: DataFrame) -> DataFrame:
    # write your code here
    return events_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, events_df):
    w = Window.partitionBy("order_id").orderBy(F.col("updated_at").desc())
    return (events_df.withColumn("rn", F.row_number().over(w))
            .filter("rn = 1").drop("rn"))
"""
MUTANTS = ["""
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, events_df):
    w = Window.partitionBy("order_id").orderBy("updated_at")
    return events_df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")
"""]
HINTS = ["Window.partitionBy(\"order_id\").orderBy(F.col(\"updated_at\").desc()) puis F.row_number().over(w).",
         "Garde rn = 1 puis .drop(\"rn\")."]
S = "order_id STRING, status STRING, updated_at TIMESTAMP"


def tests():
    t = [df(S, [["O1", "created", "2026-03-01 10:00:00"], ["O1", "paid", "2026-03-01 10:05:00"], ["O2", "created", "2026-03-01 11:00:00"],
                ["O1", "shipped", "2026-03-02 09:00:00"]]),
         df(S, [["A", "paid", "2026-01-02 00:00:00"], ["A", "created", "2026-01-01 00:00:00"]])]
    r = rng(6)
    for k in range(4):
        rows = []
        for o in range(3 + k):
            for j, s in enumerate(r.sample(["created", "paid", "shipped", "delivered", "returned"], r.randint(1, 4))):
                rows.append([f"O{o}", s, f"2026-03-{r.randint(1, 28):02d} {r.randint(0, 23):02d}:{j:02d}:{o:02d}"])
        r.shuffle(rows)
        t.append(df(S, rows))
    return [{"events_df": x} for x in t]
