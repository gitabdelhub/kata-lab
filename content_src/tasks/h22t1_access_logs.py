from kit import folder, rng

ID = "h22t1"
NAME = "Access Logs per UTC Hour"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["consigne longue", "regex", "fuseau horaire vers UTC", "normalisation des chemins", "lignes mal formées"]
DESC = """
<p>Our web servers write access logs in <code>input_dir</code> (files ending with <code>.log</code>; other files are ignored). A valid line looks like:</p>
<pre>10.0.0.7 - - [06/Mar/2026:10:15:32 +0100] "GET /api/users/42?full=1 HTTP/1.1" 200 512 37ms</pre>
<p>That is: the client IP, two dashes, the local time with its UTC offset between brackets, the request between double quotes (method, path, protocol), the status code, the response size in bytes and the latency in milliseconds followed by <code>ms</code>. Lines that do not follow this format (truncated lines, empty lines, debug messages) are skipped.</p>
<p>Group the requests by <b>UTC hour</b> and by <b>endpoint</b>. The UTC hour is written <code>yyyy-MM-dd HH:00</code> after converting the time to UTC (<code>10:15:32 +0100</code> is <code>09:15:32</code> UTC). The endpoint is the method, a space, and the path without its query string (everything from <code>?</code>), where every path segment made only of digits is replaced by <code>{id}</code>: <code>GET /api/users/42?full=1</code> becomes <code>GET /api/users/{id}</code>.</p>
<p>Your task is to return the columns <code>hour_utc</code>, <code>endpoint</code>, <code>requests</code> (long), <code>errors</code> (long, status 500 or more) and <code>avg_ms</code> (double, average latency rounded to 1 decimal), sorted by <code>hour_utc</code>, then <code>endpoint</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.text(input_dir)
"""
SOLUTION = """
import os
import re
from datetime import datetime, timezone
from pyspark.sql import functions as F

LINE = re.compile(r'(\\S+) - - \\[([^\\]]+)\\] "(\\S+) (\\S+) [^"]*" (\\d{3}) (\\d+) (\\d+)ms')


def endpoint(method, path):
    path = path.split("?")[0]
    parts = ["{id}" if p.isdigit() else p for p in path.split("/")]
    return method + " " + "/".join(parts)


def solve(spark, input_dir):
    rows = []
    for name in sorted(os.listdir(input_dir)):
        if not name.endswith(".log"):
            continue
        with open(os.path.join(input_dir, name)) as fh:
            for line in fh:
                m = LINE.fullmatch(line.strip())
                if not m:
                    continue
                ip, when, method, path, status, size, ms = m.groups()
                try:
                    t = datetime.strptime(when, "%d/%b/%Y:%H:%M:%S %z").astimezone(timezone.utc)
                except ValueError:
                    continue
                rows.append((t.strftime("%Y-%m-%d %H:00"), endpoint(method, path), int(status), int(ms)))
    df = spark.createDataFrame(rows, "hour_utc string, endpoint string, status int, ms long")
    return (df.groupBy("hour_utc", "endpoint")
              .agg(F.count("*").alias("requests"), F.sum(F.when(F.col("status") >= 500, 1).otherwise(0)).cast("long").alias("errors"),
                   F.round(F.avg("ms"), 1).alias("avg_ms"))
              .orderBy("hour_utc", "endpoint"))
"""
MUTANTS = [
    SOLUTION.replace(".astimezone(timezone.utc)", ""),
    SOLUTION.replace('    path = path.split("?")[0]\n', ''),
    SOLUTION.replace('"{id}" if p.isdigit() else p', 'p'),
    SOLUTION.replace('F.col("status") >= 500', 'F.col("status") >= 400'),
]


def L(ip, when, req, status, size, ms):
    return f'{ip} - - [{when}] "{req}" {status} {size} {ms}ms'


def tests():
    t = [folder({"web1.log": "\n".join([L("10.0.0.7", "06/Mar/2026:10:15:32 +0100", "GET /api/users/42?full=1 HTTP/1.1", 200, 512, 37),
                                         L("10.0.0.8", "06/Mar/2026:09:59:59 +0000", "GET /api/users/7 HTTP/1.1", 503, 0, 120),
                                         "DEBUG cache warmed", "",
                                         L("10.0.0.9", "06/Mar/2026:10:00:01 +0100", "POST /api/users HTTP/1.1", 201, 80, 15),
                                         '10.0.0.9 - - [06/Mar/2026:10:00:01 +0100] "GET /api/users/1 HTTP/1.1" 200']) + "\n",
                 "web2.log": L("10.0.0.1", "05/Mar/2026:23:30:00 -0200", "GET /api/orders/12/items/3 HTTP/2", 404, 10, 8) + "\n" +
                 L("10.0.0.1", "06/Mar/2026:01:10:00 +0000", "GET /api/orders/99/items/1?x=2 HTTP/2", 500, 10, 11) + "\n",
                 "web2.log.1": L("1.1.1.1", "06/Mar/2026:01:10:00 +0000", "GET / HTTP/2", 200, 1, 1) + "\n"}),
         folder({"a.log": L("1.2.3.4", "31/Dec/2026:23:45:00 -0130", "GET /v2/items/007 HTTP/1.1", 200, 5, 3) + "\n" +
                 L("1.2.3.4", "01/Jan/2027:01:05:00 +0000", "GET /v2/items/abc1 HTTP/1.1", 200, 5, 4) + "\n"})]
    r = rng(4221)
    for _ in range(6):
        files = {}
        for f in range(r.randint(1, 3)):
            lines = []
            for _ in range(r.randint(3, 20)):
                when = f"06/Mar/2026:{r.randint(8, 11):02d}:{r.randint(0, 59):02d}:00 {r.choice(['+0000', '+0100', '-0300'])}"
                path = r.choice(["/api/users/42", "/api/users/7?debug=1", "/api/users", "/health", "/api/orders/3/items/9"])
                lines.append(L("10.0.0.1", when, f"{r.choice(['GET', 'GET', 'POST'])} {path} HTTP/1.1", r.choice([200, 200, 404, 500, 503]), 10, r.randint(1, 200)))
                if r.random() < 0.15:
                    lines.append(r.choice(["oops", "10.0.0.1 - - [bad] \"GET / HTTP/1.1\" 200 1 1ms"]))
            files[f"srv{f}.log"] = "\n".join(lines) + "\n"
        files["srv.log.gz.txt"] = "ignored\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
