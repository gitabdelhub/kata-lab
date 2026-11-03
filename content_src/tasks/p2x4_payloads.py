from kit import folder, rng
import json

ID = "p2x4"
NAME = "Nested Order Payloads"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 22
TAGS = ["JSON lines", "schéma explicite", "explode_outer", "champs imbriqués"]
SUMMARY_FR = "Des fichiers JSON lines de commandes, avec une liste d'articles imbriquée. Ignorer les lignes cassées, dédoublonner les commandes, éclater les articles et calculer le chiffre d'affaires par catégorie et par jour, en comptant aussi les commandes sans article."
HINTS = ["Donne un schéma explicite à spark.read.json avec mode DROPMALFORMED : sinon une ligne cassée crée une colonne _corrupt_record.",
         "explode_outer garde les commandes avec une liste vide ou absente (la catégorie sera NULL, à remplacer par 'none').",
         "Dédoublonne sur order_id AVANT d'éclater les articles, sinon tu comptes les articles deux fois."]
DESC = """
<p>An e-commerce backend writes its orders as <b>JSON lines</b> files (one JSON object per line) in <code>input_dir</code>. Files can be in sub-folders and all end with <code>.jsonl</code>. Each object looks like this:</p>
<pre class="exv">{"order_id": "o1", "created_at": "2026-03-01T10:15:00",
 "customer": {"id": "c7", "country": "MA"},
 "items": [{"sku": "A1", "category": "books", "qty": 2, "unit_price": 50.0}]}</pre>
<p>Rules:</p>
<ol><li>Some lines are broken (not valid JSON): they are ignored.</li><li>The same order can be written several times (retries). Rows with the same <code>order_id</code> are identical: count each order once.</li><li><code>items</code> can be an empty list or be missing. Such an order still counts as an order, with the category <code>"none"</code> and a revenue of <code>0</code>.</li><li>The revenue of an item is <code>qty * unit_price</code>. A missing <code>qty</code> counts as <code>1</code>.</li><li>The day is the date part of <code>created_at</code>.</li></ol>
<p>Your task is to return, for each day and category, the columns <code>day</code> (date), <code>category</code> (string), <code>orders</code> (long, the number of distinct orders with at least one item of this category, or with no item for <code>"none"</code>) and <code>revenue</code> (double, rounded to 2 decimals), sorted by <code>day</code>, then <code>category</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.json(input_dir)
"""
SOLUTION = """
from pyspark.sql import functions as F

SCHEMA = ("order_id string, created_at string, customer struct<id:string,country:string>, "
          "items array<struct<sku:string,category:string,qty:int,unit_price:double>>")


def solve(spark, input_dir):
    df = (spark.read.schema(SCHEMA).option("mode", "DROPMALFORMED")
          .option("recursiveFileLookup", "true").option("pathGlobFilter", "*.jsonl").json(input_dir))
    df = df.filter(F.col("order_id").isNotNull()).dropDuplicates(["order_id"])
    it = df.select("order_id", F.to_date(F.to_timestamp("created_at")).alias("day"), F.explode_outer("items").alias("it"))
    it = it.select("order_id", "day",
                   F.coalesce(F.col("it.category"), F.lit("none")).alias("category"),
                   (F.coalesce(F.col("it.qty"), F.lit(1)) * F.coalesce(F.col("it.unit_price"), F.lit(0.0))).alias("rev"))
    it = it.withColumn("rev", F.when(F.col("category") == "none", F.lit(0.0)).otherwise(F.col("rev")))
    return (it.groupBy("day", "category")
            .agg(F.countDistinct("order_id").alias("orders"), F.round(F.sum("rev"), 2).alias("revenue"))
            .orderBy("day", "category"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
SCHEMA = "order_id string, created_at string, customer struct<id:string,country:string>, items array<struct<sku:string,category:string,qty:int,unit_price:double>>"
def solve(spark, input_dir):
    df = spark.read.schema(SCHEMA).option("mode", "DROPMALFORMED").option("recursiveFileLookup", "true").json(input_dir)
    df = df.filter(F.col("order_id").isNotNull()).dropDuplicates(["order_id"])
    it = df.select("order_id", F.to_date(F.to_timestamp("created_at")).alias("day"), F.explode("items").alias("it"))
    it = it.select("order_id", "day", F.col("it.category").alias("category"), (F.coalesce(F.col("it.qty"), F.lit(1)) * F.col("it.unit_price")).alias("rev"))
    return it.groupBy("day", "category").agg(F.countDistinct("order_id").alias("orders"), F.round(F.sum("rev"), 2).alias("revenue")).orderBy("day", "category")
""",
    """
from pyspark.sql import functions as F
SCHEMA = "order_id string, created_at string, customer struct<id:string,country:string>, items array<struct<sku:string,category:string,qty:int,unit_price:double>>"
def solve(spark, input_dir):
    df = spark.read.schema(SCHEMA).option("mode", "DROPMALFORMED").option("recursiveFileLookup", "true").json(input_dir)
    df = df.filter(F.col("order_id").isNotNull())
    it = df.select("order_id", F.to_date(F.to_timestamp("created_at")).alias("day"), F.explode_outer("items").alias("it"))
    it = it.select("order_id", "day", F.coalesce(F.col("it.category"), F.lit("none")).alias("category"), (F.coalesce(F.col("it.qty"), F.lit(1)) * F.coalesce(F.col("it.unit_price"), F.lit(0.0))).alias("rev"))
    return it.groupBy("day", "category").agg(F.countDistinct("order_id").alias("orders"), F.round(F.sum("rev"), 2).alias("revenue")).orderBy("day", "category")
""",
    """
from pyspark.sql import functions as F
SCHEMA = "order_id string, created_at string, customer struct<id:string,country:string>, items array<struct<sku:string,category:string,qty:int,unit_price:double>>"
def solve(spark, input_dir):
    df = spark.read.schema(SCHEMA).option("mode", "DROPMALFORMED").option("recursiveFileLookup", "true").json(input_dir)
    df = df.filter(F.col("order_id").isNotNull()).dropDuplicates(["order_id"])
    it = df.select("order_id", F.to_date(F.to_timestamp("created_at")).alias("day"), F.explode_outer("items").alias("it"))
    it = it.select("order_id", "day", F.coalesce(F.col("it.category"), F.lit("none")).alias("category"), (F.col("it.qty") * F.coalesce(F.col("it.unit_price"), F.lit(0.0))).alias("rev"))
    return it.groupBy("day", "category").agg(F.countDistinct("order_id").alias("orders"), F.round(F.sum("rev"), 2).alias("revenue")).orderBy("day", "category")
""",
]


def order(oid, ts, items, drop_items=False):
    o = {"order_id": oid, "created_at": ts, "customer": {"id": "c" + oid[-1], "country": "MA"}}
    if not drop_items:
        o["items"] = items
    return json.dumps(o)


def it(sku, cat, qty, price):
    d = {"sku": sku, "category": cat, "unit_price": price}
    if qty is not None:
        d["qty"] = qty
    return d


def tests():
    a = [order("o1", "2026-03-01T10:15:00", [it("A1", "books", 2, 50.0), it("B2", "games", None, 19.99)]),
         order("o2", "2026-03-01T18:00:00", []),
         '{"order_id": "o3", "created_at": ',
         order("o1", "2026-03-01T10:15:00", [it("A1", "books", 2, 50.0), it("B2", "games", None, 19.99)])]
    b = [order("o4", "2026-03-02T00:05:00", [it("A9", "books", 1, 12.5), it("A1", "books", 3, 50.0)]), order("o5", "2026-03-02T09:00:00", [], True)]
    t = [folder({"2026/03/01/part-0.jsonl": "\n".join(a) + "\n", "2026/03/02/part-0.jsonl": "\n".join(b) + "\n", "2026/_SUCCESS": ""}),
         folder({"x.jsonl": order("k1", "2026-04-01T23:59:59", [it("Z", "food", 0, 3.0), it("Y", "food", 4, 2.25)]) + "\nnot json\n"})]
    r = rng(304)
    cats = ["books", "games", "food", "music"]
    for _ in range(6):
        files, n, made = {}, 0, {}
        for f in range(r.randint(1, 3)):
            lines = []
            for _ in range(r.randint(1, 5)):
                n += 1
                oid = f"o{r.randint(1, n)}"
                items = [it(f"S{r.randint(1, 9)}", r.choice(cats), r.choice([None, 1, 2, 5]), round(r.uniform(1, 80), 2)) for _ in range(r.randint(0, 3))]
                if oid not in made:
                    made[oid] = order(oid, f"2026-03-0{r.randint(1, 3)}T{r.randint(0, 23):02d}:00:00", items, r.random() < 0.15)
                lines.append(made[oid])
                if r.random() < 0.2:
                    lines.append("{broken")
            files[f"day{f}/part-{f}.jsonl"] = "\n".join(lines) + "\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
