from kit import df, rng

ID = "e01t2"
NAME = "Promo Code Settlement"
LANG = "pyspark"
PARAMS = ["spark", "rides_df", "promos_df"]
MINUTES = 15
TAGS = ["join", "left join", "when / otherwise", "least", "groupBy / agg"]
DESC = """
<p>Marketing ran several promo campaigns last month. Each promo code gives a percentage discount on the fare, with a maximum discount per ride, and is valid only between two dates. The finance team needs to know how much each campaign cost.</p>
<p>You are given two DataFrames.</p>
<p><code>rides_df</code>:</p>
<ul><li><code>ride_id</code> - the ID of the ride (string);</li><li><code>ride_date</code> - the date of the ride (date);</li><li><code>fare</code> - the fare before discount (double);</li><li><code>promo_code</code> - the code typed by the rider (string, can be null). Riders type codes in any case and sometimes with spaces.</li></ul>
<p><code>promos_df</code>:</p>
<ul><li><code>code</code> - the promo code, always upper-case (string);</li><li><code>pct</code> - the discount in percent (integer);</li><li><code>max_discount</code> - the maximum discount for one ride (double);</li><li><code>valid_from</code>, <code>valid_to</code> - the first and last day the code can be used (dates, both included).</li></ul>
<p>A ride <b>uses</b> a promo if its trimmed, upper-cased <code>promo_code</code> equals a <code>code</code> and its <code>ride_date</code> is between <code>valid_from</code> and <code>valid_to</code>. The discount of such a ride is <code>fare * pct / 100</code>, but never more than <code>max_discount</code>. Rides with an unknown code or outside the dates get no discount.</p>
<p>Your task is to return one row <b>per promo code</b>, including codes that were never used, with:</p>
<ol><li><code>code</code>;</li><li><code>uses</code> - the number of rides that used the code;</li><li><code>total_discount</code> - the sum of discounts, rounded to 2 decimals (<code>0.0</code> if never used);</li><li><code>capped_rides</code> - the number of rides where the discount was limited by <code>max_discount</code> (the uncapped discount was strictly greater than <code>max_discount</code>).</li></ol>
<p>Sort by <code>total_discount</code> descending, then <code>code</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, rides_df: DataFrame, promos_df: DataFrame) -> DataFrame:
    # write your code here
    return promos_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, rides_df, promos_df):
    rides = rides_df.withColumn("code", F.upper(F.trim("promo_code")))
    used = (rides.join(promos_df, "code")
            .filter(F.col("ride_date").between(F.col("valid_from"), F.col("valid_to")))
            .withColumn("raw", F.col("fare") * F.col("pct") / 100)
            .withColumn("discount", F.least("raw", "max_discount"))
            .groupBy("code")
            .agg(F.count("*").alias("uses"),
                 F.sum("discount").alias("total"),
                 F.sum(F.when(F.col("raw") > F.col("max_discount"), 1).otherwise(0)).alias("capped_rides")))
    return (promos_df.select("code").join(used, "code", "left")
            .select("code",
                    F.coalesce("uses", F.lit(0)).alias("uses"),
                    F.round(F.coalesce("total", F.lit(0.0)), 2).alias("total_discount"),
                    F.coalesce("capped_rides", F.lit(0)).alias("capped_rides"))
            .orderBy(F.col("total_discount").desc(), "code"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
def solve(spark, rides_df, promos_df):
    rides = rides_df.withColumn("code", F.upper(F.trim("promo_code")))
    used = (rides.join(promos_df, "code").filter(F.col("ride_date").between(F.col("valid_from"), F.col("valid_to")))
            .withColumn("raw", F.col("fare") * F.col("pct") / 100).withColumn("discount", F.least("raw", "max_discount"))
            .groupBy("code").agg(F.count("*").alias("uses"), F.round(F.sum("discount"), 2).alias("total_discount"), F.sum(F.when(F.col("raw") > F.col("max_discount"), 1).otherwise(0)).alias("capped_rides")))
    return used.orderBy(F.col("total_discount").desc(), "code")
""",
    """
from pyspark.sql import functions as F
def solve(spark, rides_df, promos_df):
    rides = rides_df.withColumn("code", F.col("promo_code"))
    used = (rides.join(promos_df, "code").filter(F.col("ride_date").between(F.col("valid_from"), F.col("valid_to")))
            .withColumn("raw", F.col("fare") * F.col("pct") / 100).withColumn("discount", F.least("raw", "max_discount"))
            .groupBy("code").agg(F.count("*").alias("uses"), F.sum("discount").alias("total"), F.sum(F.when(F.col("raw") > F.col("max_discount"), 1).otherwise(0)).alias("capped_rides")))
    return (promos_df.select("code").join(used, "code", "left").select("code", F.coalesce("uses", F.lit(0)).alias("uses"), F.round(F.coalesce("total", F.lit(0.0)), 2).alias("total_discount"), F.coalesce("capped_rides", F.lit(0)).alias("capped_rides")).orderBy(F.col("total_discount").desc(), "code"))
""",
    """
from pyspark.sql import functions as F
def solve(spark, rides_df, promos_df):
    rides = rides_df.withColumn("code", F.upper(F.trim("promo_code")))
    used = (rides.join(promos_df, "code").filter((F.col("ride_date") > F.col("valid_from")) & (F.col("ride_date") < F.col("valid_to")))
            .withColumn("raw", F.col("fare") * F.col("pct") / 100).withColumn("discount", F.least("raw", "max_discount"))
            .groupBy("code").agg(F.count("*").alias("uses"), F.sum("discount").alias("total"), F.sum(F.when(F.col("raw") > F.col("max_discount"), 1).otherwise(0)).alias("capped_rides")))
    return (promos_df.select("code").join(used, "code", "left").select("code", F.coalesce("uses", F.lit(0)).alias("uses"), F.round(F.coalesce("total", F.lit(0.0)), 2).alias("total_discount"), F.coalesce("capped_rides", F.lit(0)).alias("capped_rides")).orderBy(F.col("total_discount").desc(), "code"))
""",
]
R = "ride_id STRING, ride_date DATE, fare DOUBLE, promo_code STRING"
P = "code STRING, pct INT, max_discount DOUBLE, valid_from DATE, valid_to DATE"


def tests():
    promos = [["RAMADAN", 20, 10.0, "2026-03-01", "2026-03-10"], ["WELCOME", 50, 15.0, "2026-03-01", "2026-03-31"], ["SPRING", 10, 5.0, "2026-03-20", "2026-03-31"]]
    t = [{"rides_df": df(R, [["R1", "2026-03-02", 40.0, "ramadan"], ["R2", "2026-03-10", 80.0, " RAMADAN "], ["R3", "2026-03-11", 50.0, "RAMADAN"],
                             ["R4", "2026-03-05", 20.0, "Welcome"], ["R5", "2026-03-06", 30.0, None], ["R6", "2026-03-07", 60.0, "WELCOME10"]]),
          "promos_df": df(P, promos)},
         {"rides_df": df(R, [["X", "2026-03-31", 100.0, "spring"], ["Y", "2026-03-20", 50.0, "SPRING"]]), "promos_df": df(P, promos)}]
    r = rng(31)
    for k in range(6):
        rides = []
        for i in range(15 + 5 * k):
            code = r.choice([None, "ramadan", " WELCOME", "Spring ", "SPRING", "promo", "WELCOME"])
            rides.append([f"R{k}{i}", f"2026-03-{r.randint(1, 31):02d}", round(r.uniform(10, 150), 2), code])
        t.append({"rides_df": df(R, rides), "promos_df": df(P, promos + ([["EID", 30, 20.0, "2026-03-29", "2026-03-31"]] if k % 2 else []))})
    return t
