from kit import df, rng

ID = "g06"
NAME = "Taxi Driver Features"
LANG = "pyspark"
PARAMS = ["spark", "drivers_df", "cars_df", "rides_1_df", "rides_2_df", "rides_3_df", "rides_4_df"]
MINUTES = 25
ORDERED = False
TAGS = ["union de partitions", "jointure gauche", "agrégation conditionnelle", "dates", "zéro si aucune course", "BCG"]
SOURCE = "Question rapportée du test BCG (fastprep.io, à l'origine en Pandas), réécrite en PySpark et testée par Kata Lab"
SUMMARY_FR = "Construire une ligne de features par chauffeur : infos de sa voiture, jours depuis l'inspection, expérience, et 4 compteurs calculés sur ses courses (refus, votes positifs, plaintes, incidents). Un chauffeur sans course garde sa ligne avec des 0."
HINTS = ["Réunis les 4 rides, agrège-les par driver_id, puis fais une jointure GAUCHE depuis drivers : sinon les chauffeurs sans course disparaissent. Ensuite F.coalesce(col, F.lit(0)).",
         "number_of_upvotes additionne les 4 colonnes booléennes : F.sum(F.col(c).cast(\"int\")) pour chacune, puis additionne. days_since_inspection = F.datediff(F.lit(\"2023-04-15\").cast(\"date\"), F.col(\"last_inspection_date\"))."]
DESC = """
<p>The taxi company wants one feature row per driver to train a model. Today is <b>2023-04-15</b>.</p>
<p><code>drivers_df</code>: <code>driver_id</code> int, <code>car_id</code> int, <code>age</code> int (can be null), <code>started_driving_year</code> int, <code>second_language</code> string, <code>rating</code> double, <code>net_worth_of_tips</code> double, <code>driver_class</code> string. Every driver has exactly one car.</p>
<p><code>cars_df</code>: <code>car_id</code> int, <code>model</code> string, <code>manufacture_year</code> int, <code>last_inspection_date</code> date.</p>
<p>The rides arrive in four parts <code>rides_1_df</code> to <code>rides_4_df</code> with the same columns: <code>ride_id</code> int, <code>driver_id</code> int, <code>date</code> date, <code>status</code> string, and six booleans <code>car_clearness_upvote_given</code>, <code>politeness_upvote_given</code>, <code>communication_upvote_given</code>, <code>punctuality_upvote_given</code>, <code>complaint_given</code>, <code>incident_occurred</code>.</p>
<p>Return one row per driver with these columns, in this order:</p>
<ul><li><code>driver_id</code>;</li>
<li><code>car_model</code> and <code>car_manufacture_year</code>: the <code>model</code> and <code>manufacture_year</code> of the driver's car;</li>
<li><code>days_since_inspection</code>: number of calendar days from <code>last_inspection_date</code> to 2023-04-15;</li>
<li><code>age</code> (unchanged, may stay null);</li>
<li><code>experience</code>: <code>2023 - started_driving_year</code>;</li>
<li><code>second_language</code>, <code>rating</code>, <code>net_worth_of_tips</code> (unchanged);</li>
<li><code>number_of_rejected_rides</code>: rides whose <code>status</code> is exactly <code>"Rejected by the driver"</code>;</li>
<li><code>number_of_upvotes</code>: the total number of <code>true</code> values in the four <code>*_upvote_given</code> columns over all the driver's rides (one ride can give up to 4 upvotes);</li>
<li><code>number_of_complaints</code>: rides with <code>complaint_given</code> true;</li>
<li><code>number_of_incidents</code>: rides with <code>incident_occurred</code> true;</li>
<li><code>driver_class</code> (unchanged).</li></ul>
<p>The four parts must be combined before counting. A driver with no ride keeps a row, with the four counts equal to <code>0</code>. The row order does not matter.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
IO = [("input", "DataFrame drivers_df, cars_df, rides_1_df, rides_2_df, rides_3_df, rides_4_df")]
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, drivers_df: DataFrame, cars_df: DataFrame, rides_1_df: DataFrame,
          rides_2_df: DataFrame, rides_3_df: DataFrame, rides_4_df: DataFrame) -> DataFrame:
    # write your code here
    return drivers_df
"""
SOLUTION = """
from pyspark.sql import functions as F

UP = ["car_clearness_upvote_given", "politeness_upvote_given", "communication_upvote_given", "punctuality_upvote_given"]


def solve(spark, drivers_df, cars_df, rides_1_df, rides_2_df, rides_3_df, rides_4_df):
    rides = rides_1_df.unionByName(rides_2_df).unionByName(rides_3_df).unionByName(rides_4_df)
    agg = rides.groupBy("driver_id").agg(
        F.sum(F.when(F.col("status") == "Rejected by the driver", 1).otherwise(0)).alias("number_of_rejected_rides"),
        F.sum(sum(F.col(c).cast("int") for c in UP)).alias("number_of_upvotes"),
        F.sum(F.col("complaint_given").cast("int")).alias("number_of_complaints"),
        F.sum(F.col("incident_occurred").cast("int")).alias("number_of_incidents"))
    today = F.lit("2023-04-15").cast("date")
    counts = ["number_of_rejected_rides", "number_of_upvotes", "number_of_complaints", "number_of_incidents"]
    return (drivers_df.join(cars_df, "car_id").join(agg, "driver_id", "left")
            .select("driver_id", F.col("model").alias("car_model"), F.col("manufacture_year").alias("car_manufacture_year"),
                    F.datediff(today, F.col("last_inspection_date")).alias("days_since_inspection"), "age",
                    (F.lit(2023) - F.col("started_driving_year")).alias("experience"), "second_language", "rating",
                    "net_worth_of_tips", *[F.coalesce(F.col(c), F.lit(0)).alias(c) for c in counts], "driver_class"))
"""
_BASE = SOLUTION.split("def solve")[0]
MUTANTS = [
    SOLUTION.replace('join(agg, "driver_id", "left")', 'join(agg, "driver_id")'),
    SOLUTION.replace("rides = rides_1_df.unionByName(rides_2_df).unionByName(rides_3_df).unionByName(rides_4_df)", "rides = rides_1_df"),
    SOLUTION.replace('F.sum(sum(F.col(c).cast("int") for c in UP))', 'F.sum(F.greatest(*[F.col(c).cast("int") for c in UP]))'),
    SOLUTION.replace('F.datediff(today, F.col("last_inspection_date"))', 'F.datediff(F.current_date(), F.col("last_inspection_date"))'),
    SOLUTION.replace('F.col("status") == "Rejected by the driver"', 'F.lower(F.col("status")).contains("reject")'),
]
SD = "driver_id int, car_id int, age int, started_driving_year int, second_language string, rating double, net_worth_of_tips double, driver_class string"
SC = "car_id int, model string, manufacture_year int, last_inspection_date date"
SR = ("ride_id int, driver_id int, date date, status string, car_clearness_upvote_given boolean, politeness_upvote_given boolean, "
      "communication_upvote_given boolean, punctuality_upvote_given boolean, complaint_given boolean, incident_occurred boolean")
MODELS = ["Toyota Prius", "Dacia Logan", "Skoda Octavia", "Hyundai Ioniq"]
STATUSES = ["Success", "Success", "Rejected by the driver", "Rejected by the client", "Cancelled"]


def _case(r, nd, nr):
    cars = [[100 + i, r.choice(MODELS), r.randint(2008, 2022), f"2022-{r.randint(1, 12):02d}-{r.randint(1, 28):02d}"] for i in range(nd)]
    drivers = [[i + 1, 100 + i, r.choice([None, r.randint(21, 64)]), r.randint(1995, 2022), r.choice(["no", "English", "French"]),
                round(r.uniform(3, 5), 2), round(r.uniform(0, 900), 2), r.choice(["A class", "B class"])] for i in range(nd)]
    parts = [[], [], [], []]
    for k in range(nr):
        row = [k + 1, r.randint(1, nd + 1) if nd > 1 else 1, f"2023-0{r.randint(1, 4)}-{r.randint(1, 14):02d}", r.choice(STATUSES)]
        row += [r.random() < 0.5 for _ in range(4)] + [r.random() < 0.2, r.random() < 0.1]
        if row[1] <= nd:
            parts[r.randrange(4)].append(row)
    out = {"drivers_df": df(SD, drivers), "cars_df": df(SC, cars)}
    for i in range(4):
        out[f"rides_{i + 1}_df"] = df(SR, parts[i])
    return out


def tests():
    T, F_ = True, False
    t = [{"drivers_df": df(SD, [[1, 11, 35, 2015, "French", 4.6, 120.5, "A class"], [2, 12, None, 2020, "no", 3.9, 40.0, "B class"],
                                [3, 13, 52, 2001, "English", 4.9, 300.0, "A class"]]),
          "cars_df": df(SC, [[11, "Toyota Prius", 2018, "2023-03-15"], [12, "Dacia Logan", 2014, "2022-12-31"], [13, "Skoda Octavia", 2020, "2023-04-15"]]),
          "rides_1_df": df(SR, [[1, 1, "2023-04-01", "Success", T, T, F_, T, F_, F_], [2, 2, "2023-04-02", "Rejected by the driver", F_, F_, F_, F_, F_, F_]]),
          "rides_2_df": df(SR, [[3, 1, "2023-04-03", "Rejected by the driver", F_, F_, F_, F_, T, F_]]),
          "rides_3_df": df(SR, []),
          "rides_4_df": df(SR, [[4, 2, "2023-04-05", "Rejected by the client", F_, T, F_, F_, T, T], [5, 1, "2023-04-06", "Success", T, T, T, T, F_, F_]])},
         {"drivers_df": df(SD, [[9, 90, 44, 2023, "no", 4.0, 0.0, "B class"]]),
          "cars_df": df(SC, [[90, "Hyundai Ioniq", 2022, "2023-01-01"]]),
          "rides_1_df": df(SR, []), "rides_2_df": df(SR, []), "rides_3_df": df(SR, []), "rides_4_df": df(SR, [])}]
    r = rng(1906)
    for _ in range(5):
        t.append(_case(r, r.randint(2, 7), r.randint(3, 25)))
    return t
