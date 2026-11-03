from kit import folder, rng
import json

ID = "e08t1"
NAME = "Catalog JSON Exports"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 22
TAGS = ["JSON multi-lignes", "multiLine", "explode", "valeur par défaut du parent"]
DESC = """
<p>A marketplace receives the catalog of its sellers as JSON files in <code>input_dir/&lt;seller&gt;/</code>. Unlike JSON lines, each file contains <b>one JSON array</b>, written over many lines, of products like this:</p>
<pre class="exv">[
  {"product_id": "P1", "title": "Linen shirt", "base_price": 25.0,
   "variants": [{"sku": "P1-S-W", "size": "S", "color": "white", "price": null, "stock": 3},
                {"sku": "P1-M-W", "size": "M", "color": "white", "price": 27.5, "stock": 0}]}
]</pre>
<p>Rules:</p>
<ol><li>Only files ending with <code>.json</code> are read. The seller is the name of the folder.</li><li>Each variant becomes one row. A product without variants (missing or empty list) is ignored.</li><li>The price of a variant is its own <code>price</code>, or the <code>base_price</code> of its product when the variant price is <code>null</code> or missing.</li><li>A variant is <code>in_stock</code> when its <code>stock</code> is greater than <code>0</code>; a missing stock means <code>0</code>.</li><li>Sizes are upper-cased and colors are lower-cased and trimmed.</li></ol>
<p>Your task is to return the columns <code>seller</code>, <code>product_id</code>, <code>sku</code>, <code>size</code>, <code>color</code>, <code>price</code> (double) and <code>in_stock</code> (boolean), sorted by <code>seller</code>, then <code>sku</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.json(input_dir)
"""
SOLUTION = """
import os
from functools import reduce
from pyspark.sql import functions as F

SCHEMA = ("product_id string, title string, base_price double, "
          "variants array<struct<sku:string,size:string,color:string,price:double,stock:int>>")


def solve(spark, input_dir):
    parts = []
    for seller in sorted(os.listdir(input_dir)):
        sdir = os.path.join(input_dir, seller)
        if not os.path.isdir(sdir):
            continue
        files = [os.path.join(sdir, n) for n in sorted(os.listdir(sdir)) if n.endswith(".json")]
        if not files:
            continue
        d = spark.read.schema(SCHEMA).option("multiLine", True).json(files)
        parts.append(d.withColumn("seller", F.lit(seller)))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    v = df.select("seller", "product_id", "base_price", F.explode("variants").alias("v"))
    return (v.select("seller", "product_id", F.col("v.sku").alias("sku"),
                     F.upper(F.trim("v.size")).alias("size"), F.lower(F.trim("v.color")).alias("color"),
                     F.coalesce(F.col("v.price"), F.col("base_price")).alias("price"),
                     (F.coalesce(F.col("v.stock"), F.lit(0)) > 0).alias("in_stock"))
            .orderBy("seller", "sku"))
"""
MUTANTS = [
    """
import os
from functools import reduce
from pyspark.sql import functions as F
def solve(spark, input_dir):
    parts = []
    for seller in sorted(os.listdir(input_dir)):
        files = [os.path.join(input_dir, seller, n) for n in sorted(os.listdir(os.path.join(input_dir, seller))) if n.endswith(".json")]
        d = spark.read.option("multiLine", True).json(files)
        parts.append(d.withColumn("seller", F.lit(seller)))
    df = reduce(lambda a, b: a.unionByName(b, allowMissingColumns=True), parts)
    v = df.select("seller", "product_id", "base_price", F.explode("variants").alias("v"))
    return v.select("seller", "product_id", F.col("v.sku").alias("sku"), F.upper(F.trim("v.size")).alias("size"), F.lower(F.trim("v.color")).alias("color"), F.col("v.price").cast("double").alias("price"), (F.coalesce(F.col("v.stock"), F.lit(0)) > 0).alias("in_stock")).orderBy("seller", "sku")
""",
    """
import os
from functools import reduce
from pyspark.sql import functions as F
SCHEMA = "product_id string, title string, base_price double, variants array<struct<sku:string,size:string,color:string,price:double,stock:int>>"
def solve(spark, input_dir):
    parts = []
    for seller in sorted(os.listdir(input_dir)):
        files = [os.path.join(input_dir, seller, n) for n in sorted(os.listdir(os.path.join(input_dir, seller))) if n.endswith(".json")]
        d = spark.read.schema(SCHEMA).option("multiLine", True).json(files)
        parts.append(d.withColumn("seller", F.lit(seller)))
    df = reduce(lambda a, b: a.unionByName(b), parts)
    v = df.select("seller", "product_id", "base_price", F.explode_outer("variants").alias("v"))
    return v.select("seller", "product_id", F.col("v.sku").alias("sku"), F.upper(F.trim("v.size")).alias("size"), F.lower(F.trim("v.color")).alias("color"), F.coalesce(F.col("v.price"), F.col("base_price")).alias("price"), (F.col("v.stock") > 0).alias("in_stock")).orderBy("seller", "sku")
""",
]


def var(sku, size, color, price="missing", stock="missing"):
    d = {"sku": sku, "size": size, "color": color}
    if price != "missing":
        d["price"] = price
    if stock != "missing":
        d["stock"] = stock
    return d


def prod(pid, base, variants="missing"):
    d = {"product_id": pid, "title": "Item " + pid, "base_price": base}
    if variants != "missing":
        d["variants"] = variants
    return d


def tests():
    a = [prod("P1", 25.0, [var("P1-S-W", "s", " White", None, 3), var("P1-M-W", "M", "white", 27.5, 0)]), prod("P2", 9.9, []), prod("P3", 5.0)]
    b = [prod("Q1", 100.0, [var("Q1-XL", "xl ", "BLACK", stock=2)])]
    t = [folder({"atlas_shop/catalog.json": json.dumps(a, indent=2), "atlas_shop/notes.txt": "draft", "dune/part1.json": json.dumps(b, indent=2)}),
         folder({"z/a.json": json.dumps([prod("A", 1.0, [var("A1", "m", "Red", 0.0, None)])], indent=1), "z/b.json": json.dumps([prod("B", 2.0, [var("B1", "L", "red ", None, 1)])], indent=4)})]
    r = rng(801)
    for _ in range(6):
        files = {}
        for seller in r.sample(["atlas", "dune", "oasis"], r.randint(1, 3)):
            for f in range(r.randint(1, 2)):
                prods = []
                for p in range(r.randint(1, 3)):
                    pid = f"{seller[0].upper()}{f}{p}"
                    vs = [var(f"{pid}-{k}", r.choice(["s", "M", "l ", "XL"]), r.choice([" Red", "blue", "GREEN "]), r.choice([None, "missing", round(r.uniform(5, 90), 2)]),
                              r.choice(["missing", None, 0, 1, 7])) for k in range(r.randint(0, 3))]
                    prods.append(prod(pid, round(r.uniform(5, 90), 2), vs if r.random() < 0.9 else "missing"))
                files[f"{seller}/f{f}.json"] = json.dumps(prods, indent=2)
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
