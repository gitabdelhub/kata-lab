from kit import df, rng

ID = "f10t2"
NAME = "Billable Seat-Days"
LANG = "pyspark"
PARAMS = ["spark", "seat_events_df", "month"]
MINUTES = 22
TAGS = ["consigne longue", "intervalles actifs", "jours couverts", "règles implicites"]
DESC = """
<p>The SaaS platform now bills customers per <b>seat-day</b>: a seat costs one unit for every calendar day of the month on which it was active, even for a few minutes. Finance asks you to compute the bill of a given <code>month</code> (a string <code>YYYY-MM</code>) from the seat audit log.</p>
<p><code>seat_events_df</code> has the columns <code>tenant</code>, <code>user</code> (strings), <code>action</code> (string) and <code>at</code> (timestamp). When an admin gives a seat to a user, the log records <code>add</code>; when the seat is taken back, it records <code>remove</code>. The log comes from several application servers, so the same event can appear twice, and the case of <code>action</code> is not reliable. Other actions (for example <code>rename</code>) say nothing about the seat and must be ignored.</p>
<p>A seat becomes active at an <code>add</code> and stays active until the next <code>remove</code> of the same user in the same tenant. Admins sometimes click <code>add</code> again on a user who already has a seat: this changes nothing. Likewise, a <code>remove</code> for a user who has no active seat changes nothing. If a seat is still active when the log ends, it is active until the end of the month; a seat that became active before the month and was not removed counts from the first day of the month. Only days inside <code>month</code> are billed.</p>
<p>Your task is to return one row per tenant with at least one billable seat-day in <code>month</code>, with the columns <code>tenant</code>, <code>seat_days</code> (long, the number of (user, day) pairs that are billed) and <code>users</code> (long, the number of distinct users with at least one billed day), sorted by <code>tenant</code>. If an <code>add</code> and a <code>remove</code> of a user have exactly the same timestamp, the <code>add</code> happened first.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F
from pyspark.sql.window import Window


def solve(spark: SparkSession, seat_events_df: DataFrame, month: str) -> DataFrame:
    # write your code here
    return seat_events_df
"""
SOLUTION = """
import calendar
import datetime as dt
from pyspark.sql import functions as F


def solve(spark, seat_events_df, month):
    y, m = map(int, month.split("-"))
    first = dt.date(y, m, 1)
    last = dt.date(y, m, calendar.monthrange(y, m)[1])
    ev = (seat_events_df.select("tenant", "user", F.lower(F.trim("action")).alias("action"), "at")
          .filter(F.col("action").isin("add", "remove")).dropDuplicates()
          .collect())
    ev.sort(key=lambda r: (r.tenant, r.user, r.at, 0 if r.action == "add" else 1))
    billed = set()
    state = {}

    def bill(key, start, end):
        a = max(start.date(), first)
        b = min(end.date() if end else last, last)
        d = a
        while d <= b:
            billed.add((key[0], key[1], d))
            d += dt.timedelta(days=1)

    for r in ev:
        key = (r.tenant, r.user)
        if r.action == "add":
            if key not in state:
                state[key] = r.at
        elif key in state:
            bill(key, state.pop(key), r.at)
    for key, start in state.items():
        bill(key, start, None)
    rows = [(t, u, d) for t, u, d in billed]
    out = spark.createDataFrame(rows, "tenant string, user string, day date")
    return (out.groupBy("tenant").agg(F.count("*").alias("seat_days"), F.countDistinct("user").alias("users"))
            .orderBy("tenant"))
"""
MUTANTS = [
    """
import calendar, datetime as dt
from pyspark.sql import functions as F
def solve(spark, seat_events_df, month):
    y, m = map(int, month.split("-")); first = dt.date(y, m, 1); last = dt.date(y, m, calendar.monthrange(y, m)[1])
    ev = seat_events_df.select("tenant", "user", F.lower(F.trim("action")).alias("action"), "at").filter(F.col("action").isin("add", "remove")).dropDuplicates().collect()
    ev.sort(key=lambda r: (r.tenant, r.user, r.at, 0 if r.action == "add" else 1))
    billed, state = set(), {}
    def bill(key, s, e):
        a = max(s.date(), first); b = min(e.date() if e else last, last); d = a
        while d <= b: billed.add((key[0], key[1], d)); d += dt.timedelta(days=1)
    for r in ev:
        key = (r.tenant, r.user)
        if r.action == "add": state[key] = r.at
        elif key in state: bill(key, state.pop(key), r.at)
    for key, s in state.items(): bill(key, s, None)
    out = spark.createDataFrame(list(billed), "tenant string, user string, day date")
    return out.groupBy("tenant").agg(F.count("*").alias("seat_days"), F.countDistinct("user").alias("users")).orderBy("tenant")
""",
    """
import calendar, datetime as dt
from pyspark.sql import functions as F
def solve(spark, seat_events_df, month):
    y, m = map(int, month.split("-")); first = dt.date(y, m, 1); last = dt.date(y, m, calendar.monthrange(y, m)[1])
    ev = seat_events_df.select("tenant", "user", F.lower(F.trim("action")).alias("action"), "at").filter(F.col("action").isin("add", "remove")).dropDuplicates().collect()
    ev.sort(key=lambda r: (r.tenant, r.user, r.at, 0 if r.action == "add" else 1))
    billed, state = set(), {}
    def bill(key, s, e):
        a = max(s.date(), first); b = min(e.date() - dt.timedelta(days=1) if e else last, last); d = a
        while d <= b: billed.add((key[0], key[1], d)); d += dt.timedelta(days=1)
    for r in ev:
        key = (r.tenant, r.user)
        if r.action == "add":
            if key not in state: state[key] = r.at
        elif key in state: bill(key, state.pop(key), r.at)
    for key, s in state.items(): bill(key, s, None)
    out = spark.createDataFrame(list(billed), "tenant string, user string, day date")
    return out.groupBy("tenant").agg(F.count("*").alias("seat_days"), F.countDistinct("user").alias("users")).orderBy("tenant")
""",
    """
import calendar, datetime as dt
from pyspark.sql import functions as F
def solve(spark, seat_events_df, month):
    y, m = map(int, month.split("-")); first = dt.date(y, m, 1); last = dt.date(y, m, calendar.monthrange(y, m)[1])
    ev = seat_events_df.select("tenant", "user", F.lower(F.trim("action")).alias("action"), "at").filter(F.col("action").isin("add", "remove")).dropDuplicates().collect()
    ev = [r for r in ev if r.at.date() >= first and r.at.date() <= last]
    ev.sort(key=lambda r: (r.tenant, r.user, r.at, 0 if r.action == "add" else 1))
    billed, state = set(), {}
    def bill(key, s, e):
        a = max(s.date(), first); b = min(e.date() if e else last, last); d = a
        while d <= b: billed.add((key[0], key[1], d)); d += dt.timedelta(days=1)
    for r in ev:
        key = (r.tenant, r.user)
        if r.action == "add":
            if key not in state: state[key] = r.at
        elif key in state: bill(key, state.pop(key), r.at)
    for key, s in state.items(): bill(key, s, None)
    out = spark.createDataFrame(list(billed), "tenant string, user string, day date")
    return out.groupBy("tenant").agg(F.count("*").alias("seat_days"), F.countDistinct("user").alias("users")).orderBy("tenant")
""",
]
S = "tenant string, user string, action string, at timestamp"


def tests():
    t = [{"seat_events_df": df(S, [["acme", "ana", "add", "2026-02-20 10:00:00"], ["acme", "bob", "ADD", "2026-03-03 23:50:00"],
                                   ["acme", "bob", "remove", "2026-03-05 00:10:00"], ["acme", "bob", "remove", "2026-03-05 00:10:00"],
                                   ["acme", "cy", "add", "2026-03-10 09:00:00"], ["acme", "cy", "add", "2026-03-12 09:00:00"],
                                   ["acme", "cy", "rename", "2026-03-13 09:00:00"], ["acme", "cy", "remove", "2026-03-14 08:00:00"],
                                   ["globex", "dan", "remove", "2026-03-01 08:00:00"], ["globex", "eve", "add", "2026-04-01 00:00:00"]]), "month": "2026-03"},
         {"seat_events_df": df(S, [["t", "u", "add", "2026-02-27 12:00:00"], ["t", "u", "remove", "2026-02-27 12:00:00"],
                                   ["t", "v", "add", "2026-02-28 12:00:00"], ["t", "v", "remove", "2026-03-02 00:00:00"],
                                   ["t", "w", " Add ", "2026-01-31 12:00:00"]]), "month": "2026-02"}]
    r = rng(3102)
    for _ in range(6):
        rows = []
        for _ in range(r.randint(3, 16)):
            d = r.choice(["2026-02-2", "2026-03-0", "2026-03-1", "2026-03-2", "2026-04-0"]) + str(r.randint(1, 8))
            rows.append([r.choice(["acme", "globex"]), r.choice(["ana", "bob", "cy", "dan"]), r.choice(["add", "add", "remove", "REMOVE", "rename", "Add"]), f"{d} {r.randint(0, 23):02d}:{r.choice(['00', '30'])}:00"])
        if rows and r.random() < 0.5:
            rows.append(list(rows[0]))
        t.append({"seat_events_df": df(S, rows), "month": "2026-03"})
    return t
