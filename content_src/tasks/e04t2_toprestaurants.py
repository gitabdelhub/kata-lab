from kit import df, rng

ID = "e04t2"
NAME = "Top Rated Restaurants per City"
LANG = "pyspark"
PARAMS = ["spark", "reviews_df", "restaurants_df"]
MINUTES = 18
TAGS = ["dédoublonnage", "seuil HAVING", "dense_rank", "égalités"]
DESC = """
<p>The app shows the best restaurants of each city. You are given two DataFrames.</p>
<p><code>restaurants_df</code>: <code>restaurant_id</code> (string), <code>name</code> (string), <code>city</code> (string) and <code>active</code> (boolean).</p>
<p><code>reviews_df</code>: <code>review_id</code> (string), <code>restaurant_id</code> (string), <code>user_id</code> (string), <code>rating</code> (integer) and <code>reviewed_at</code> (timestamp).</p>
<p>Rules:</p>
<ol><li>Only ratings from <code>1</code> to <code>5</code> are valid; other ratings and <code>null</code> ratings are ignored.</li><li>A user can review the same restaurant several times: only their <b>latest</b> valid review of this restaurant counts.</li><li>Only active restaurants with at least <code>3</code> counted reviews are ranked.</li><li>The score of a restaurant is the average of its counted ratings, rounded to 2 decimals.</li><li>Restaurants are ranked inside their city by score, highest first, with <b>dense ranking</b>: restaurants with the same rounded score have the same rank, and the next rank is the next integer.</li></ol>
<p>Your task is to return the restaurants with a rank of <code>1</code> or <code>2</code>, with the columns <code>city</code>, <code>rank</code> (integer), <code>name</code>, <code>score</code> (double) and <code>reviews</code> (long), sorted by <code>city</code>, <code>rank</code>, then <code>name</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, reviews_df: DataFrame, restaurants_df: DataFrame) -> DataFrame:
    # write your code here
    return restaurants_df
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, reviews_df, restaurants_df):
    r = reviews_df.filter(F.col("rating").between(1, 5))
    w = Window.partitionBy("restaurant_id", "user_id").orderBy(F.col("reviewed_at").desc(), F.col("review_id").desc())
    r = r.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    s = r.groupBy("restaurant_id").agg(F.round(F.avg("rating"), 2).alias("score"), F.count("*").alias("reviews")).filter("reviews >= 3")
    j = s.join(restaurants_df.filter(F.col("active")), "restaurant_id")
    j = j.withColumn("rank", F.dense_rank().over(Window.partitionBy("city").orderBy(F.col("score").desc())))
    return (j.filter("rank <= 2").select("city", F.col("rank").cast("int"), "name", "score", "reviews")
            .orderBy("city", "rank", "name"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, reviews_df, restaurants_df):
    r = reviews_df.filter(F.col("rating").between(1, 5))
    s = r.groupBy("restaurant_id").agg(F.round(F.avg("rating"), 2).alias("score"), F.count("*").alias("reviews")).filter("reviews >= 3")
    j = s.join(restaurants_df.filter(F.col("active")), "restaurant_id")
    j = j.withColumn("rank", F.dense_rank().over(Window.partitionBy("city").orderBy(F.col("score").desc())))
    return j.filter("rank <= 2").select("city", F.col("rank").cast("int"), "name", "score", "reviews").orderBy("city", "rank", "name")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, reviews_df, restaurants_df):
    r = reviews_df.filter(F.col("rating").between(1, 5))
    w = Window.partitionBy("restaurant_id", "user_id").orderBy(F.col("reviewed_at").desc())
    r = r.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    s = r.groupBy("restaurant_id").agg(F.round(F.avg("rating"), 2).alias("score"), F.count("*").alias("reviews")).filter("reviews >= 3")
    j = s.join(restaurants_df.filter(F.col("active")), "restaurant_id")
    j = j.withColumn("rank", F.rank().over(Window.partitionBy("city").orderBy(F.col("score").desc())))
    return j.filter("rank <= 2").select("city", F.col("rank").cast("int"), "name", "score", "reviews").orderBy("city", "rank", "name")
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, reviews_df, restaurants_df):
    w = Window.partitionBy("restaurant_id", "user_id").orderBy(F.col("reviewed_at").desc())
    r = reviews_df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").filter(F.col("rating").between(1, 5))
    s = r.groupBy("restaurant_id").agg(F.round(F.avg("rating"), 2).alias("score"), F.count("*").alias("reviews")).filter("reviews >= 3")
    j = s.join(restaurants_df.filter(F.col("active")), "restaurant_id")
    j = j.withColumn("rank", F.dense_rank().over(Window.partitionBy("city").orderBy(F.col("score").desc())))
    return j.filter("rank <= 2").select("city", F.col("rank").cast("int"), "name", "score", "reviews").orderBy("city", "rank", "name")
""",
]
RS = "restaurant_id string, name string, city string, active boolean"
RV = "review_id string, restaurant_id string, user_id string, rating int, reviewed_at timestamp"


def tests():
    rest = [["r1", "Tajine House", "Rabat", True], ["r2", "Pizza Uno", "Rabat", True], ["r3", "Sushi Bar", "Rabat", True], ["r4", "Old Grill", "Rabat", False],
            ["r5", "Cafe Lome", "Lome", True], ["r6", "Maquis 228", "Lome", True]]
    rev = [["v1", "r1", "u1", 5, "2026-03-01 10:00:00"], ["v2", "r1", "u2", 4, "2026-03-01 11:00:00"], ["v3", "r1", "u3", 5, "2026-03-02 10:00:00"],
           ["v4", "r2", "u1", 5, "2026-03-01 10:00:00"], ["v5", "r2", "u2", 5, "2026-03-01 10:00:00"], ["v6", "r2", "u3", 4, "2026-03-01 10:00:00"],
           ["v7", "r3", "u1", 1, "2026-03-01 10:00:00"], ["v8", "r3", "u1", 4, "2026-03-05 10:00:00"], ["v9", "r3", "u2", 4, "2026-03-01 10:00:00"],
           ["v10", "r3", "u3", 4, "2026-03-01 10:00:00"], ["v11", "r4", "u1", 5, "2026-03-01 10:00:00"], ["v12", "r4", "u2", 5, "2026-03-01 10:00:00"],
           ["v13", "r4", "u3", 5, "2026-03-01 10:00:00"], ["v14", "r5", "u1", 3, "2026-03-01 10:00:00"], ["v15", "r5", "u2", 6, "2026-03-01 10:00:00"],
           ["v16", "r5", "u3", 3, "2026-03-01 10:00:00"], ["v17", "r5", "u4", 2, "2026-03-01 10:00:00"], ["v18", "r6", "u1", 5, "2026-03-01 10:00:00"]]
    t = [{"reviews_df": df(RV, rev), "restaurants_df": df(RS, rest)},
         {"reviews_df": df(RV, [["a", "x", "u1", 2, "2026-01-01 00:00:00"], ["b", "x", "u2", 3, "2026-01-01 00:00:00"], ["c", "x", "u3", None, "2026-01-01 00:00:00"],
                                ["d", "x", "u3", 4, "2025-12-01 00:00:00"], ["e", "y", "u1", 3, "2026-01-01 00:00:00"], ["f", "y", "u2", 3, "2026-01-01 00:00:00"], ["g", "y", "u4", 3, "2026-01-01 00:00:00"]]),
          "restaurants_df": df(RS, [["x", "Xango", "Dakar", True], ["y", "Yassa", "Dakar", True]])}]
    r = rng(402)
    for _ in range(6):
        rest = [[f"r{i}", f"Resto {chr(65 + i)}", r.choice(["Rabat", "Lome", "Dakar"]), r.random() < 0.85] for i in range(r.randint(3, 8))]
        rev, n = [], 0
        for x in rest:
            for u in r.sample(range(1, 7), r.randint(1, 6)):
                for _ in range(r.choice([1, 1, 2])):
                    n += 1
                    rev.append([f"v{n:03d}", x[0], f"u{u}", r.choice([None, 0, 1, 2, 3, 4, 5, 5, 4]), f"2026-03-{r.randint(1, 9):02d} 10:00:00"])
        t.append({"reviews_df": df(RV, rev), "restaurants_df": df(RS, rest)})
    return t
