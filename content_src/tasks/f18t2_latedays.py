from kit import df, rng

ID = "f18t2"
NAME = "Late Deliveries in Working Days"
LANG = "pyspark"
PARAMS = ["spark", "shipments_df", "holidays_df", "as_of"]
MINUTES = 22
TAGS = ["consigne longue", "jours ouvrés", "jours fériés", "livraisons pas encore arrivées"]
DESC = """
<p>Our carriers are paid with a penalty for every working day of delay, and the logistics team wants the numbers per carrier. <code>shipments_df</code> has the columns <code>shipment_id</code>, <code>carrier</code>, <code>promised_on</code> (date) and <code>delivered_at</code> (timestamp, <code>null</code> if not delivered yet). <code>holidays_df</code> has one column <code>day</code> (date) with the public holidays.</p>
<p>A <b>working day</b> is a Monday to Friday that is not a public holiday. A shipment delivered on or before its promised day is on time, even if it was delivered at night. Otherwise, its delay is the number of working days after the promised day, up to and including the day of delivery; a shipment promised on Friday and delivered on the next Monday is late by one working day, and one delivered on the Saturday is late, but by 0 working days.</p>
<p>The report is made on the date <code>as_of</code> (string <code>yyyy-MM-dd</code>). A shipment that is not delivered at that date (no delivery, or a delivery after the end of <code>as_of</code>) and whose promised day is before <code>as_of</code> is late, and its delay is counted as if it were delivered on <code>as_of</code>. A shipment promised on or after <code>as_of</code> and not delivered yet is not judged and does not count at all.</p>
<p>Your task is to return, for each carrier with at least one judged shipment, the columns <code>carrier</code>, <code>shipments</code> (long, judged shipments), <code>late</code> (long, late shipments) and <code>delay_days</code> (long, total working days of delay), sorted by <code>delay_days</code> descending, then <code>carrier</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, shipments_df: DataFrame, holidays_df: DataFrame, as_of: str) -> DataFrame:
    # write your code here
    return shipments_df
"""
SOLUTION = """
from pyspark.sql import functions as F


def solve(spark, shipments_df, holidays_df, as_of):
    today = F.to_date(F.lit(as_of))
    d = F.to_date("delivered_at")
    s = shipments_df.withColumn("done", F.when(d <= today, d))
    s = s.filter(F.col("done").isNotNull() | (F.col("promised_on") < today))
    s = s.withColumn("end", F.coalesce("done", today)).withColumn("is_late", F.col("end") > F.col("promised_on"))
    late = (s.filter("is_late")
            .withColumn("day", F.explode(F.sequence(F.date_add("promised_on", 1), F.col("end"))))
            .filter(~F.dayofweek("day").isin(1, 7))
            .join(holidays_df, "day", "left_anti")
            .groupBy("shipment_id").agg(F.count("*").alias("wd")))
    s = s.join(late, "shipment_id", "left")
    return (s.groupBy("carrier").agg(F.count("*").alias("shipments"),
                                     F.sum(F.col("is_late").cast("int")).cast("long").alias("late"),
                                     F.coalesce(F.sum("wd"), F.lit(0)).cast("long").alias("delay_days"))
            .orderBy(F.col("delay_days").desc(), "carrier"))
"""
MUTANTS = [
    SOLUTION.replace('            .join(holidays_df, "day", "left_anti")\n', ''),
    SOLUTION.replace('s = shipments_df.withColumn("done", F.when(d <= today, d))', 's = shipments_df.withColumn("done", d)'),
    SOLUTION.replace('F.sequence(F.date_add("promised_on", 1), F.col("end"))', 'F.sequence(F.col("promised_on"), F.col("end"))'),
    SOLUTION.replace('s = s.filter(F.col("done").isNotNull() | (F.col("promised_on") < today))', 's = s'),
]
S = "shipment_id string, carrier string, promised_on date, delivered_at timestamp"
H = "day date"


def tests():
    t = [{"shipments_df": df(S, [["s1", "FastCo", "2026-03-06", "2026-03-09 08:00:00"], ["s2", "FastCo", "2026-03-06", "2026-03-07 10:00:00"],
                                 ["s3", "FastCo", "2026-03-10", "2026-03-10 23:59:00"], ["s4", "SlowLine", "2026-03-02", "2026-03-05 12:00:00"],
                                 ["s5", "SlowLine", "2026-03-11", None], ["s6", "SlowLine", "2026-03-13", None], ["s7", "SlowLine", "2026-03-10", "2026-03-14 09:00:00"],
                                 ["s8", "Rare", "2026-03-20", None]]),
          "holidays_df": df(H, [["2026-03-04"]]), "as_of": "2026-03-13"},
         {"shipments_df": df(S, [["a", "X", "2026-01-01", "2026-01-01 05:00:00"]]), "holidays_df": df(H, []), "as_of": "2026-01-02"}]
    r = rng(3182)
    for _ in range(6):
        rows = []
        for i in range(r.randint(3, 9)):
            p = r.randint(2, 16)
            dlv = None if r.random() < 0.25 else f"2026-03-{min(28, p + r.choice([-1, 0, 1, 2, 3, 6])):02d} {r.randint(0, 23):02d}:00:00"
            rows.append([f"s{i}", r.choice(["FastCo", "SlowLine"]), f"2026-03-{p:02d}", dlv])
        t.append({"shipments_df": df(S, rows), "holidays_df": df(H, [[f"2026-03-{d:02d}"] for d in r.sample(range(2, 20), 2)]), "as_of": "2026-03-16"})
    return t
