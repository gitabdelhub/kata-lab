from kit import folder, rng
import json

ID = "e17t1"
NAME = "Player Event Files"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 20
TAGS = ["JSON lines", "noms de champs différents", "explode", "lignes corrompues"]
DESC = """
<p>A streaming app uploads player events to <code>input_dir</code> as JSON lines files (<code>*.jsonl</code>, one JSON object per line). Two versions of the app are in use:</p>
<ul><li>version 1 writes <code>{"user_id": ..., "events": [{"type": ..., "seconds": ...}, ...]}</code>;</li><li>version 2 writes <code>{"userId": ..., "payload": {"events": [{"kind": ..., "durationMs": ...}, ...]}}</code>.</li></ul>
<p>A file can contain lines of both versions. Lines that are not valid JSON, and lines without a user, must be ignored. In version 2, <code>durationMs</code> is in milliseconds.</p>
<p>Your task is to return, for each user who has at least one event of type <code>"play"</code>, the columns <code>user_id</code> (string), <code>plays</code> (long, number of <code>play</code> events) and <code>watch_minutes</code> (double, total duration of the <code>play</code> events in minutes, rounded to 1 decimal; a missing duration counts as <code>0</code>), sorted by <code>watch_minutes</code> descending, then <code>user_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.json(input_dir)
"""
SOLUTION = """
import json
import os


def solve(spark, input_dir):
    rows = []
    for root, _, files in os.walk(input_dir):
        for name in sorted(files):
            if not name.endswith(".jsonl"):
                continue
            with open(os.path.join(root, name)) as fh:
                for line in fh:
                    try:
                        obj = json.loads(line)
                    except ValueError:
                        continue
                    if not isinstance(obj, dict):
                        continue
                    if obj.get("user_id") is not None:
                        user = str(obj["user_id"])
                        for e in obj.get("events") or []:
                            rows.append((user, e.get("type"), float(e.get("seconds") or 0)))
                    elif obj.get("userId") is not None:
                        user = str(obj["userId"])
                        for e in (obj.get("payload") or {}).get("events") or []:
                            rows.append((user, e.get("kind"), float(e.get("durationMs") or 0) / 1000))
    from pyspark.sql import functions as F
    df = spark.createDataFrame(rows, "user_id string, type string, seconds double")
    return (df.filter(F.col("type") == "play").groupBy("user_id")
            .agg(F.count("*").alias("plays"), F.round(F.sum("seconds") / 60, 1).alias("watch_minutes"))
            .orderBy(F.col("watch_minutes").desc(), "user_id"))
"""
MUTANTS = [
    """
import json, os
from pyspark.sql import functions as F
def solve(spark, input_dir):
    rows = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if not name.endswith(".jsonl"): continue
            for line in open(os.path.join(root, name)):
                try: obj = json.loads(line)
                except ValueError: continue
                if obj.get("user_id") is not None:
                    for e in obj.get("events") or []: rows.append((str(obj["user_id"]), e.get("type"), float(e.get("seconds") or 0)))
                elif obj.get("userId") is not None:
                    for e in (obj.get("payload") or {}).get("events") or []: rows.append((str(obj["userId"]), e.get("kind"), float(e.get("durationMs") or 0)))
    df = spark.createDataFrame(rows, "user_id string, type string, seconds double")
    return df.filter(F.col("type") == "play").groupBy("user_id").agg(F.count("*").alias("plays"), F.round(F.sum("seconds") / 60, 1).alias("watch_minutes")).orderBy(F.col("watch_minutes").desc(), "user_id")
""",
    """
import json, os
from pyspark.sql import functions as F
def solve(spark, input_dir):
    rows = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if not name.endswith(".jsonl"): continue
            for line in open(os.path.join(root, name)):
                try: obj = json.loads(line)
                except ValueError: continue
                if obj.get("user_id") is not None:
                    for e in obj.get("events") or []: rows.append((str(obj["user_id"]), e.get("type"), float(e.get("seconds") or 0)))
    df = spark.createDataFrame(rows, "user_id string, type string, seconds double")
    return df.filter(F.col("type") == "play").groupBy("user_id").agg(F.count("*").alias("plays"), F.round(F.sum("seconds") / 60, 1).alias("watch_minutes")).orderBy(F.col("watch_minutes").desc(), "user_id")
""",
]


def v1(u, ev):
    return json.dumps({"user_id": u, "events": [{"type": t, "seconds": s} for t, s in ev]})


def v2(u, ev):
    return json.dumps({"userId": u, "payload": {"events": [{"kind": t, "durationMs": None if s is None else int(s * 1000)} for t, s in ev]}})


def tests():
    t = [folder({"a.jsonl": v1("u1", [("play", 600), ("pause", 5), ("play", 300)]) + "\n" + v2("u2", [("play", 90)]) + "\n{broken\n",
                 "b.jsonl": v2("u1", [("play", 60), ("seek", 2)]) + "\n" + json.dumps({"events": [{"type": "play", "seconds": 999}]}) + "\n",
                 "notes.txt": v1("u9", [("play", 9999)])}),
         folder({"x.jsonl": v1("7", [("play", None), ("play", 30)]) + "\n" + v1("8", [("pause", 30)]) + "\n" + v2("9", []) + "\n"})]
    r = rng(1701)
    for _ in range(6):
        files = {}
        for f in range(r.randint(1, 3)):
            lines = []
            for _ in range(r.randint(1, 6)):
                ev = [(r.choice(["play", "play", "pause", "seek"]), r.choice([None, 30, 45, 120, 600])) for _ in range(r.randint(0, 4))]
                u = f"u{r.randint(1, 5)}"
                lines.append(r.choice([v1, v2])(u, ev) if r.random() > 0.1 else "not json")
            files[f"day{f}/events-{f}.jsonl"] = "\n".join(lines) + "\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
