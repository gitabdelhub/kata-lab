import json

from kit import folder, rng

ID = "e03t1"
NAME = "No-Show Rate from Appointment Logs"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 20
TAGS = ["JSON", "schéma qui change", "dernière version", "Window", "groupBy / agg"]
DESC = """
<p>A network of clinics logs every change of every appointment as JSON lines. The logs are stored in <code>input_dir</code>, one folder per day: <code>input_dir/day=YYYY-MM-DD/updates.json</code>. Each line of a file is one JSON object with these fields:</p>
<ul><li><code>appointment_id</code> - the ID of the appointment (string);</li><li><code>patient_id</code> - the patient (string);</li><li><code>doctor</code> or <code>doctor_id</code> - the doctor (string). Old logs use the field <code>doctor</code>; after a migration, new logs use <code>doctor_id</code> instead. A test can contain only old logs or only new logs;</li><li><code>slot</code> - the time of the appointment, <code>"YYYY-MM-DD HH:MM:SS"</code> (string);</li><li><code>status</code> - <code>"booked"</code>, <code>"completed"</code>, <code>"no_show"</code> or <code>"cancelled"</code>;</li><li><code>updated_at</code> - when the change was logged, <code>"YYYY-MM-DD HH:MM:SS"</code> (string).</li></ul>
<p>Some lines are broken (not valid JSON) and must be ignored. The current state of an appointment is its update with the latest <code>updated_at</code>; two updates of the same appointment never have the same <code>updated_at</code>. An appointment can change doctor or slot between two updates: always use the values of the current state.</p>
<p>Your task is to compute the no-show rate of each doctor per month of the <code>slot</code>, using the current state of every appointment:</p>
<ol><li><code>appointments</code> - the number of appointments whose current status is not <code>"cancelled"</code>;</li><li><code>no_shows</code> - the number of appointments whose current status is <code>"no_show"</code>;</li><li><code>no_show_rate</code> - <code>no_shows / appointments</code>, rounded to 2 decimals.</li></ol>
<p>Return <code>doctor_id</code>, <code>month</code> (string <code>"YYYY-MM"</code>), <code>appointments</code>, <code>no_shows</code> and <code>no_show_rate</code>, only for doctor-months with at least one appointment. Sort by <code>month</code>, then <code>no_show_rate</code> descending, then <code>doctor_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
<p><code>A2</code> was moved from <code>dr_lam</code> to <code>dr_ben</code>, and its current status is <code>no_show</code>. <code>A3</code> is cancelled, so <code>dr_lam</code> has one appointment left in March.</p>
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    logs = spark.read.json(input_dir)
    # write your code here
    return logs
"""
SOLUTION = """
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, input_dir):
    logs = spark.read.option("mode", "DROPMALFORMED").json(input_dir)
    doctor_cols = [F.col(c) for c in ("doctor_id", "doctor") if c in logs.columns]
    logs = (logs.filter(F.col("appointment_id").isNotNull())
            .withColumn("doc", F.coalesce(*doctor_cols)))
    w = Window.partitionBy("appointment_id").orderBy(F.col("updated_at").desc())
    current = logs.withColumn("rn", F.row_number().over(w)).filter("rn = 1")
    current = current.filter(F.col("status") != "cancelled").withColumn("month", F.substring("slot", 1, 7))
    return (current.groupBy(F.col("doc").alias("doctor_id"), "month")
            .agg(F.count("*").alias("appointments"),
                 F.sum(F.when(F.col("status") == "no_show", 1).otherwise(0)).alias("no_shows"))
            .withColumn("no_show_rate", F.round(F.col("no_shows") / F.col("appointments"), 2))
            .orderBy("month", F.col("no_show_rate").desc(), "doctor_id"))
"""
MUTANTS = [
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, input_dir):
    logs = spark.read.option("mode", "DROPMALFORMED").json(input_dir)
    cols = [F.col(c) for c in ("doctor_id", "doctor") if c in logs.columns]
    logs = logs.filter(F.col("appointment_id").isNotNull()).withColumn("doc", F.coalesce(*cols))
    cur = logs.filter(F.col("status") != "cancelled")
    w = Window.partitionBy("appointment_id").orderBy(F.col("updated_at").desc())
    cur = cur.withColumn("rn", F.row_number().over(w)).filter("rn = 1").withColumn("month", F.substring("slot", 1, 7))
    return (cur.groupBy(F.col("doc").alias("doctor_id"), "month").agg(F.count("*").alias("appointments"), F.sum(F.when(F.col("status") == "no_show", 1).otherwise(0)).alias("no_shows"))
            .withColumn("no_show_rate", F.round(F.col("no_shows") / F.col("appointments"), 2)).orderBy("month", F.col("no_show_rate").desc(), "doctor_id"))
""",
    """
from pyspark.sql import functions as F
from pyspark.sql.window import Window
def solve(spark, input_dir):
    logs = spark.read.option("mode", "DROPMALFORMED").json(input_dir)
    logs = logs.filter(F.col("appointment_id").isNotNull()).withColumn("doc", F.coalesce(F.col("doctor_id"), F.col("doctor")))
    w = Window.partitionBy("appointment_id").orderBy(F.col("updated_at").desc())
    cur = logs.withColumn("rn", F.row_number().over(w)).filter("rn = 1").filter(F.col("status") != "cancelled").withColumn("month", F.substring("slot", 1, 7))
    return (cur.groupBy(F.col("doc").alias("doctor_id"), "month").agg(F.count("*").alias("appointments"), F.sum(F.when(F.col("status") == "no_show", 1).otherwise(0)).alias("no_shows"))
            .withColumn("no_show_rate", F.round(F.col("no_shows") / F.col("appointments"), 2)).orderBy("month", F.col("no_show_rate").desc(), "doctor_id"))
""",
]


def line(a, p, doc, slot, st, up, new):
    d = {"appointment_id": a, "patient_id": p, ("doctor_id" if new else "doctor"): doc, "slot": slot, "status": st, "updated_at": up}
    return json.dumps(d)


def tests():
    ex = {
        "day=2026-02-27/updates.json": "\n".join([
            line("A1", "P1", "dr_lam", "2026-03-02 09:00:00", "booked", "2026-02-27 10:00:00", False),
            line("A2", "P2", "dr_lam", "2026-03-03 10:00:00", "booked", "2026-02-27 11:00:00", False),
            line("A3", "P3", "dr_lam", "2026-03-04 11:00:00", "booked", "2026-02-27 12:00:00", False)]) + "\n",
        "day=2026-03-05/updates.json": "\n".join([
            line("A1", "P1", "dr_lam", "2026-03-02 09:00:00", "completed", "2026-03-05 08:00:00", True),
            '{"appointment_id": "A9", "status": ',
            line("A2", "P2", "dr_ben", "2026-03-03 10:00:00", "no_show", "2026-03-05 09:00:00", True),
            line("A3", "P3", "dr_lam", "2026-03-04 11:00:00", "cancelled", "2026-03-05 10:00:00", True),
            line("A4", "P1", "dr_ben", "2026-04-01 09:00:00", "booked", "2026-03-05 11:00:00", True)]) + "\n",
    }
    old_only = {"day=2026-01-10/updates.json": "\n".join([
        line("B1", "P1", "dr_ait", "2026-01-12 09:00:00", "no_show", "2026-01-10 10:00:00", False),
        line("B2", "P2", "dr_ait", "2026-01-13 09:00:00", "completed", "2026-01-10 10:00:00", False),
        line("B3", "P3", "dr_ait", "2026-01-14 09:00:00", "completed", "2026-01-10 10:00:00", False)]) + "\n"}
    t = [folder(ex), folder(old_only)]
    r = rng(50)
    for k in range(6):
        files = {}
        state = {}
        for day in range(1, 4 + k % 3):
            new = day >= 2 if k % 3 else (k == 0)
            lines = []
            for j in range(r.randint(2, 7)):
                a = f"A{r.randint(1, 10)}"
                doc, slot = state.get(a, (r.choice(["dr_lam", "dr_ben", "dr_ait"]), f"2026-0{r.randint(3, 4)}-{r.randint(1, 28):02d} 10:00:00"))
                if r.random() < 0.2:
                    doc = r.choice(["dr_lam", "dr_ben", "dr_ait"])
                if r.random() < 0.15:
                    slot = f"2026-0{r.randint(3, 4)}-{r.randint(1, 28):02d} 15:00:00"
                state[a] = (doc, slot)
                st = r.choice(["booked", "completed", "no_show", "cancelled", "no_show"])
                lines.append(line(a, "P" + a[1:], doc, slot, st, f"2026-03-{day:02d} {8 + j:02d}:{r.randint(0, 59):02d}:00", new))
                if r.random() < 0.1:
                    lines.append('{"appointment_id": "BROKEN"')
            files[f"day=2026-03-{day:02d}/updates.json"] = "\n".join(lines) + "\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
