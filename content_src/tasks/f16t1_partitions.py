from kit import folder, rng

ID = "f16t1"
NAME = "Partitioned Sales Lake"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["consigne longue", "partitions Hive", "marqueur _SUCCESS", "fichiers temporaires"]
DESC = """
<p>The nightly jobs of our stores write their sales into a data lake, in <code>input_dir</code>, partitioned the way Spark does it: <code>&lt;country folder&gt;/&lt;day folder&gt;/&lt;files&gt;</code>, where a country folder is named <code>country=&lt;code&gt;</code> and a day folder <code>dt=&lt;yyyy-MM-dd&gt;</code>. Data files end with <code>.csv</code> and have a header with the columns <code>sku</code>, <code>qty</code> and <code>unit_price</code>; the country and the day are not in the files, only in the folder names.</p>
<p>A job writes the files of a day folder first and creates an empty file named <code>_SUCCESS</code> in it when everything is written. A day folder without <code>_SUCCESS</code> is a job that crashed or is still running: its data is incomplete and the whole folder must be ignored. While it runs, a job also leaves work files behind: any file or folder whose name starts with <code>_</code> or <code>.</code> is not data, at any level below a day folder. An older version of the jobs wrote the country code in lower case, so the same country can have two folders (<code>country=ma</code> and <code>country=MA</code>), possibly with the same day in both; they are the same country, written in upper case in the report, and each day folder is judged on its own.</p>
<p>Your task is to return, for each country and day with complete data, the columns <code>country</code>, <code>day</code> (date), <code>units</code> (long, total quantity), <code>revenue</code> (double, total of quantity times unit price, rounded to 2 decimals) and <code>skus</code> (long, number of different products sold), sorted by <code>country</code>, then <code>day</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.csv(input_dir, header=True)
"""
SOLUTION = """
import csv
import os
from pyspark.sql import functions as F


def solve(spark, input_dir):
    rows = []
    for cdir in sorted(os.listdir(input_dir)):
        if not cdir.lower().startswith("country="):
            continue
        country = cdir.split("=", 1)[1].strip().upper()
        for ddir in sorted(os.listdir(os.path.join(input_dir, cdir))):
            base = os.path.join(input_dir, cdir, ddir)
            if not ddir.startswith("dt=") or not os.path.isfile(os.path.join(base, "_SUCCESS")):
                continue
            day = ddir[3:]
            for root, dirs, files in os.walk(base):
                dirs[:] = [d for d in dirs if not d.startswith(("_", "."))]
                for name in files:
                    if name.startswith(("_", ".")) or not name.endswith(".csv"):
                        continue
                    with open(os.path.join(root, name), newline="") as fh:
                        for r in csv.DictReader(fh):
                            rows.append((country, day, r["sku"].strip(), int(r["qty"]), float(r["unit_price"])))
    df = spark.createDataFrame(rows, "country string, day string, sku string, qty long, unit_price double")
    return (df.groupBy("country", F.to_date("day").alias("day")).agg(
                F.sum("qty").alias("units"),
                F.round(F.sum(F.col("qty") * F.col("unit_price")), 2).alias("revenue"),
                F.countDistinct("sku").alias("skus"))
            .orderBy("country", "day"))
"""
MUTANTS = [
    SOLUTION.replace(' or not os.path.isfile(os.path.join(base, "_SUCCESS"))', ''),
    SOLUTION.replace('                dirs[:] = [d for d in dirs if not d.startswith(("_", "."))]\n', ''),
    SOLUTION.replace('country = cdir.split("=", 1)[1].strip().upper()', 'country = cdir.split("=", 1)[1].strip()'),
    SOLUTION.replace('F.countDistinct("sku")', 'F.count("sku")'),
]


def part(rows):
    return "sku,qty,unit_price\n" + "".join(f"{s},{q},{p}\n" for s, q, p in rows)


def tests():
    t = [folder({"country=MA/dt=2026-03-04/part-0000.csv": part([("A1", 2, 10.0), ("B2", 1, 4.5)]),
                 "country=MA/dt=2026-03-04/part-0001.csv": part([("A1", 1, 10.0)]),
                 "country=MA/dt=2026-03-04/_SUCCESS": "",
                 "country=MA/dt=2026-03-04/_temporary/0/part-0002.csv": part([("Z9", 100, 1.0)]),
                 "country=MA/dt=2026-03-05/part-0000.csv": part([("A1", 5, 10.0)]),
                 "country=ma/dt=2026-03-04/part-0000.csv": part([("C3", 3, 2.0)]),
                 "country=ma/dt=2026-03-04/_SUCCESS": "",
                 "country=ma/dt=2026-03-04/.part-0000.csv.crc": "crc",
                 "country=SN/dt=2026-03-05/part-0000.csv": part([("A1", 1, 9.99), ("A1", 2, 9.99)]),
                 "country=SN/dt=2026-03-05/_SUCCESS": "",
                 "country=SN/dt=2026-03-05/notes.txt": "ok\n"}),
         folder({"country=FR/dt=2026-01-01/p.csv": part([("X", 1, 1.0)]), "country=FR/dt=2026-01-01/_SUCCESS": "",
                 "country=FR/dt=2026-01-02/p.csv": part([("X", 1, 1.0)])})]
    r = rng(3161)
    for _ in range(6):
        files = {}
        for c in r.sample(["MA", "ma", "SN", "CI"], r.randint(1, 3)):
            for d in r.sample(["2026-03-04", "2026-03-05", "2026-03-06"], r.randint(1, 2)):
                base = f"country={c}/dt={d}"
                for k in range(r.randint(1, 2)):
                    files[f"{base}/part-{k:04d}.csv"] = part([(r.choice(["A1", "B2", "C3"]), r.randint(1, 4), r.choice([1.5, 10.0, 2.25])) for _ in range(r.randint(1, 3))])
                if r.random() < 0.75:
                    files[f"{base}/_SUCCESS"] = ""
                if r.random() < 0.4:
                    files[f"{base}/_temporary/attempt/part-9999.csv"] = part([("T0", 50, 1.0)])
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
