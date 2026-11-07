from kit import df, rng

ID = "g07"
NAME = "Prepare Driver Classification Data"
LANG = "pyspark"
PARAMS = ["spark", "train_df", "test_df"]
MINUTES = 30
TAGS = ["statistiques du train seulement", "encodage", "standardisation", "valeurs manquantes", "union", "BCG"]
SOURCE = "Question rapportée du test BCG (fastprep.io, à l'origine en Pandas), réécrite en PySpark et testée par Kata Lab"
SUMMARY_FR = "Préparer train et test pour un modèle avec des statistiques calculées sur le train SEULEMENT : remplir les âges manquants, encoder les textes en entiers, standardiser les pourboires, coder la classe en 0/1, puis renvoyer une seule table (train puis test)."
HINTS = ["Calcule d'abord sur train_df seul : moyenne des âges non nuls, moyenne et écart type de population (F.stddev_pop) de net_worth_of_tips, et la liste triée des valeurs distinctes de car_model et second_language. Récupère-les avec collect().",
         "Applique la même fonction aux deux tables, ajoute la colonne dataset, puis unionByName et trie par (train d'abord, puis driver_id). Pour l'encodage : F.create_map, ou une jointure avec une petite table valeur -> code, puis coalesce(code, -1)."]
DESC = """
<p>The taxi company prepares its driver data for a classifier. You get <code>train_df</code> and <code>test_df</code> with the same columns: <code>driver_id</code> int, <code>car_model</code> string, <code>car_manufacture_year</code> int, <code>days_since_inspection</code> int, <code>age</code> int (can be null), <code>experience</code> int, <code>second_language</code> string, <code>rating</code> double, <code>net_worth_of_tips</code> double, <code>number_of_rejected_rides</code>, <code>number_of_upvotes</code>, <code>number_of_complaints</code>, <code>number_of_incidents</code> (int), and <code>driver_class</code> string (can be null in the test data).</p>
<p>Every statistic below is computed on the <b>training data only</b>, then applied to both tables:</p>
<ol><li><code>age</code>: replace null ages with the mean of the non-null training ages, then truncate every age to an integer (drop the decimals).</li>
<li><code>car_model</code> and <code>second_language</code>: sort the distinct training values in ascending order and replace each value by its position <code>0, 1, 2, ...</code> in that list. A value never seen in the training data becomes <code>-1</code>.</li>
<li><code>net_worth_of_tips</code>: replace each value by <code>(value - mean) / std</code>, where mean and std are the training mean and <b>population</b> standard deviation (divide by N), rounded to 5 decimal places. If that std is <code>0</code>, the standardized value is <code>0</code>.</li>
<li><code>driver_class</code>: <code>"A class"</code> becomes <code>0</code>, <code>"B class"</code> becomes <code>1</code>, null stays null.</li></ol>
<p>All other columns are unchanged. Return one DataFrame whose first column is <code>dataset</code> (<code>"train"</code> or <code>"test"</code>), followed by the 14 columns above in the same order, with all training rows first, then all test rows, each group sorted by <code>driver_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
IO = [("input", "DataFrame train_df, test_df")]
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, train_df: DataFrame, test_df: DataFrame) -> DataFrame:
    # write your code here
    return train_df
"""
SOLUTION = """
from pyspark.sql import functions as F

COLS = ["driver_id", "car_model", "car_manufacture_year", "days_since_inspection", "age", "experience", "second_language",
        "rating", "net_worth_of_tips", "number_of_rejected_rides", "number_of_upvotes", "number_of_complaints",
        "number_of_incidents", "driver_class"]


def solve(spark, train_df, test_df):
    st = train_df.agg(F.avg("age").alias("age_mean"), F.avg("net_worth_of_tips").alias("m"),
                      F.stddev_pop("net_worth_of_tips").alias("s")).first()
    codes = {}
    for c in ["car_model", "second_language"]:
        values = sorted(r[0] for r in train_df.select(c).distinct().collect())
        codes[c] = F.create_map(*[x for i, v in enumerate(values) for x in (F.lit(v), F.lit(i))])

    def prep(d, name):
        d = d.withColumn("age", F.coalesce(F.col("age").cast("double"), F.lit(st.age_mean)).cast("int"))
        for c in codes:
            d = d.withColumn(c, F.coalesce(codes[c][F.col(c)], F.lit(-1)))
        z = F.lit(0.0) if st.s == 0 else F.round((F.col("net_worth_of_tips") - F.lit(st.m)) / F.lit(st.s), 5)
        d = d.withColumn("net_worth_of_tips", z)
        d = d.withColumn("driver_class", F.when(F.col("driver_class") == "A class", 0).when(F.col("driver_class") == "B class", 1))
        return d.select(F.lit(name).alias("dataset"), *COLS).withColumn("_g", F.lit(0 if name == "train" else 1))

    return prep(train_df, "train").unionByName(prep(test_df, "test")).orderBy("_g", "driver_id").drop("_g")
"""
MUTANTS = [
    SOLUTION.replace('st = train_df.agg(', 'st = train_df.unionByName(test_df).agg('),
    SOLUTION.replace("F.stddev_pop(", "F.stddev("),
    SOLUTION.replace('.cast("double"), F.lit(st.age_mean)).cast("int")', '.cast("double"), F.lit(st.age_mean)).cast("double")).withColumn("age", F.round("age").cast("int")'),
    SOLUTION.replace('train_df.select(c).distinct()', 'train_df.unionByName(test_df).select(c).distinct()'),
    SOLUTION.replace("F.coalesce(codes[c][F.col(c)], F.lit(-1))", "codes[c][F.col(c)]"),
    SOLUTION.replace('.orderBy("_g", "driver_id")', '.orderBy("driver_id")'),
]
S = ("driver_id int, car_model string, car_manufacture_year int, days_since_inspection int, age int, experience int, "
     "second_language string, rating double, net_worth_of_tips double, number_of_rejected_rides int, number_of_upvotes int, "
     "number_of_complaints int, number_of_incidents int, driver_class string")
MODELS = ["Toyota Prius", "Dacia Logan", "Skoda Octavia", "Hyundai Ioniq", "Kia Niro"]
LANGS = ["no", "English", "French", "Arabic"]


def _rows(r, ids, test, models, langs):
    out = []
    for i in ids:
        out.append([i, r.choice(models), r.randint(2008, 2022), r.randint(0, 400), r.choice([None, r.randint(21, 64), r.randint(21, 64)]),
                    r.randint(0, 25), r.choice(langs), round(r.uniform(3, 5), 2), round(r.uniform(0, 900), 2), r.randint(0, 9),
                    r.randint(0, 60), r.randint(0, 5), r.randint(0, 3),
                    r.choice([None, "A class", "B class"]) if test else r.choice(["A class", "B class"])])
    r.shuffle(out)
    return out


def tests():
    t = [{"train_df": df(S, [[3, "Toyota Prius", 2018, 31, 30, 8, "French", 4.6, 100.0, 1, 12, 0, 0, "A class"],
                             [1, "Dacia Logan", 2014, 105, None, 3, "no", 3.9, 300.0, 4, 5, 2, 1, "B class"],
                             [2, "Toyota Prius", 2020, 0, 41, 22, "English", 4.9, 200.0, 0, 20, 0, 0, "A class"],
                             [5, "Skoda Octavia", 2019, 12, 26, 2, "no", 4.1, 400.0, 2, 9, 1, 0, "B class"]]),
          "test_df": df(S, [[9, "Kia Niro", 2021, 3, None, 1, "Arabic", 4.4, 250.0, 0, 3, 0, 0, None],
                            [7, "Dacia Logan", 2012, 200, 58, 30, "French", 3.7, 50.0, 6, 2, 3, 2, "B class"]])},
         {"train_df": df(S, [[1, "Kia Niro", 2020, 10, 33, 5, "no", 4.0, 80.0, 0, 4, 0, 0, "A class"],
                             [2, "Kia Niro", 2021, 20, 34, 6, "no", 4.2, 80.0, 1, 5, 0, 0, "B class"]]),
          "test_df": df(S, [[3, "Kia Niro", 2019, 30, None, 7, "English", 4.5, 120.0, 0, 6, 1, 0, None]])}]
    r = rng(1907)
    for _ in range(5):
        n = r.randint(3, 9)
        ids = r.sample(range(1, 60), n + r.randint(1, 5))
        t.append({"train_df": df(S, _rows(r, ids[:n], False, MODELS[:4], LANGS[:3])),
                  "test_df": df(S, _rows(r, ids[n:], True, MODELS, LANGS))})
    return t
