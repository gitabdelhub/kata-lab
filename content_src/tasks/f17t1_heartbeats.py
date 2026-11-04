from kit import folder, rng
import json

ID = "f17t1"
NAME = "Player Event Batches"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["consigne longue", "JSON imbriqué", "lots renvoyés", "intervalles lecture/pause"]
DESC = """
<p>Our video players do not send each event on its own: they collect events and upload them in batches, sometimes long after, when the device is back online. The upload service writes the batches it receives as JSON lines into files ending with <code>.jsonl</code>, at any depth of <code>input_dir</code>. A batch looks like this:</p>
<pre>{"batch_id": "b-17", "device": "tv-3", "sent_at": "2026-03-04T21:00:00Z",
 "events": [{"ago": 600, "type": "play", "content": "show-1"},
            {"ago": 120, "type": "pause", "content": "show-1"}]}</pre>
<p>(on one line in the files). <code>ago</code> is the number of seconds between the event and the upload, so an event happened at <code>sent_at</code> minus <code>ago</code> seconds. When an upload times out, the player sends the same batch again with the same <code>batch_id</code>; the service keeps both, but it is one batch.</p>
<p>The content team wants to know how long each content is watched. A device watches a content from a <code>play</code> event of that content until the next event of the same device, whatever its type (<code>pause</code>, <code>stop</code>, or a <code>play</code> of another content or of the same one), because a device plays one thing at a time. A <code>play</code> that is the last event known for its device is still running and is not counted yet. Event types may be written in any case.</p>
<p>Your task is to return, for each content watched at least once, the columns <code>content</code>, <code>viewers</code> (long, number of different devices that watched it) and <code>watch_minutes</code> (double, total watched time in minutes, rounded to 1 decimal), sorted by <code>watch_minutes</code> descending, then <code>content</code>.</p>
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
import datetime as dt
import json
import os
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def solve(spark, input_dir):
    batches = {}
    for root, _, files in os.walk(input_dir):
        for name in files:
            if name.endswith(".jsonl"):
                with open(os.path.join(root, name)) as fh:
                    for line in fh:
                        if line.strip():
                            b = json.loads(line)
                            batches[b["batch_id"]] = b
    rows = []
    for b in batches.values():
        sent = dt.datetime.strptime(b["sent_at"], "%Y-%m-%dT%H:%M:%SZ")
        for e in b.get("events") or []:
            rows.append((b["device"], sent - dt.timedelta(seconds=e["ago"]), e["type"].strip().lower(), e.get("content")))
    df = spark.createDataFrame(rows, "device string, ts timestamp, type string, content string")
    w = Window.partitionBy("device").orderBy("ts")
    p = (df.withColumn("next_ts", F.lead("ts").over(w))
         .filter((F.col("type") == "play") & F.col("next_ts").isNotNull())
         .withColumn("sec", F.col("next_ts").cast("long") - F.col("ts").cast("long")))
    return (p.groupBy("content").agg(F.countDistinct("device").alias("viewers"),
                                     F.round(F.sum("sec") / 60.0, 1).alias("watch_minutes"))
            .orderBy(F.col("watch_minutes").desc(), "content"))
"""
MUTANTS = [
    SOLUTION.replace('batches[b["batch_id"]] = b', 'batches[len(batches)] = b'),
    SOLUTION.replace('rows.append((b["device"], sent - dt.timedelta(seconds=e["ago"]),', 'rows.append((b["device"], sent,'),
    SOLUTION.replace('p = (df.withColumn("next_ts", F.lead("ts").over(w))', 'p = (df.withColumn("next_ts", F.lead("ts").over(w)).filter(F.col("type") != "play").union(df.filter(F.col("type") == "play").withColumn("next_ts", F.lit(None).cast("timestamp"))).withColumn("next_ts", F.min(F.when(F.col("type") != "play", F.col("ts"))).over(w.rowsBetween(1, Window.unboundedFollowing)))'),
    SOLUTION.replace('e["type"].strip().lower()', 'e["type"]'),
]


def batch(bid, device, sent, events):
    return json.dumps({"batch_id": bid, "device": device, "sent_at": sent, "events": [{"ago": a, "type": ty, "content": c} for a, ty, c in events]})


def tests():
    t = [folder({"2026/03/04/up-1.jsonl": "\n".join([
                    batch("b1", "tv-3", "2026-03-04T21:00:00Z", [(600, "play", "show-1"), (120, "pause", "show-1")]),
                    batch("b2", "tv-3", "2026-03-04T22:00:00Z", [(1800, "PLAY", "show-1"), (900, "play", "show-2"), (300, "stop", "show-2")]),
                    batch("b2", "tv-3", "2026-03-04T22:00:00Z", [(1800, "PLAY", "show-1"), (900, "play", "show-2"), (300, "stop", "show-2")])]) + "\n",
                 "2026/03/04/up-2.jsonl": batch("b9", "phone-1", "2026-03-04T23:00:00Z", [(3600, "play", "show-2"), (60, "Pause", "show-2"), (30, "play", "show-1")]) + "\n",
                 "2026/03/04/up-2.json.tmp": "{\n"}),
         folder({"a.jsonl": batch("z", "d", "2026-01-01T10:00:00Z", [(90, "play", "c"), (0, "play", "c")]) + "\n"})]
    r = rng(3171)
    for _ in range(6):
        lines = []
        for k in range(r.randint(2, 5)):
            ev, ago = [], r.randint(3000, 6000)
            for _ in range(r.randint(1, 4)):
                ev.append((ago, r.choice(["play", "play", "PLAY", "pause", "stop"]), r.choice(["show-1", "show-2", "film-9"])))
                ago -= r.choice([60, 300, 900])
                ago = max(ago, 0)
            lines.append(batch(f"b{k}", r.choice(["tv-1", "tv-2", "phone"]), f"2026-03-04T2{r.randint(0, 3)}:00:00Z", ev))
        if r.random() < 0.6:
            lines.append(lines[0])
        t.append(folder({"up/a.jsonl": "\n".join(lines[: len(lines) // 2 + 1]) + "\n", "up/b/c.jsonl": "\n".join(lines[len(lines) // 2 + 1:]) + "\n"}))
    return [{"input_dir": x} for x in t]
