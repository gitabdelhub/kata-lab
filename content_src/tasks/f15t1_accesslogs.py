from kit import folder, rng
import datetime as dt

ID = "f15t1"
NAME = "Access Logs Project"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["projet multi-fichiers", "consigne longue", "regex", "fuseaux horaires", "normalisation des chemins"]
PROJECT = {"files": ["pipeline/parse.py", "pipeline/report.py"], "main": "pipeline/report.py"}
DESC = """
<p>This task is a small project. The editor contains a package <code>pipeline</code> with two files: <code>parse.py</code>, where you parse one log line, and <code>report.py</code>, where <code>solve</code> builds the report. Only <code>solve</code> is tested, but keep the parsing in <code>parse.py</code> and import it. Use the file list on the left of the editor to switch between files.</p>
<p>Our web servers write one line per HTTP request, in files ending with <code>.log</code> placed at any depth of <code>input_dir</code>. A line looks like this:</p>
<pre>203.0.113.5 - - [04/Mar/2026:10:12:01 +0100] "GET /api/orders/42?full=1 HTTP/1.1" 200 512 "-" "Mozilla/5.0"</pre>
<p>that is the client address, two dashes (or a user name instead of the second dash), the time with the offset of the server's time zone between square brackets, the request (method, path, protocol) between quotes, the status code, the size of the response in bytes (<code>-</code> when nothing was sent, which means 0), the referer and the user agent between quotes. The servers are in different time zones. Lines that do not follow this format (truncated lines, start-up messages) must be ignored, and so must requests from robots, whose user agent contains <code>bot</code> in any case.</p>
<p>The SRE team wants traffic per <b>endpoint</b>, not per URL: the endpoint of a request is its path without the query string (everything from <code>?</code>), without a trailing <code>/</code> (except for the path <code>/</code> itself), and with every path segment made only of digits replaced by <code>{id}</code>. For example <code>/api/orders/42/?full=1</code> and <code>/api/orders/7</code> are both <code>/api/orders/{id}</code>.</p>
<p>Your task is to return, for each hour in <b>UTC</b> and endpoint, the columns <code>hour</code> (string <code>yyyy-MM-dd HH:00</code>), <code>endpoint</code>, <code>requests</code> (long), <code>errors</code> (long, requests with a status of 500 or more) and <code>bytes</code> (long, total size), sorted by <code>hour</code>, then <code>endpoint</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
# ==== pipeline/parse.py ====
def parse_line(line):
    \"\"\"Parse ONE log line.
    Return None for a line to ignore, else a dict with the keys
    hour (yyyy-MM-dd HH:00, UTC), endpoint, status (int) and bytes (int).\"\"\"
    # write your code here
    return None

# ==== pipeline/report.py ====
from pyspark.sql import SparkSession, DataFrame, functions as F
from pipeline.parse import parse_line


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.text(input_dir)
"""
SOLUTION = """
# ==== pipeline/parse.py ====
import datetime as dt
import re

LINE = re.compile(r'^(\\S+) \\S+ \\S+ \\[([^\\]]+)\\] "(\\S+) (\\S+)[^"]*" (\\d{3}) (\\d+|-) "[^"]*" "([^"]*)"$')


def endpoint(path):
    path = path.split("?", 1)[0]
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/") or "/"
    return "/".join("{id}" if s.isdigit() else s for s in path.split("/"))


def parse_line(line):
    m = LINE.match(line.strip())
    if not m:
        return None
    _, when, _, path, status, size, agent = m.groups()
    if "bot" in agent.lower():
        return None
    t = dt.datetime.strptime(when, "%d/%b/%Y:%H:%M:%S %z").astimezone(dt.timezone.utc)
    return {"hour": t.strftime("%Y-%m-%d %H:00"), "endpoint": endpoint(path),
            "status": int(status), "bytes": 0 if size == "-" else int(size)}

# ==== pipeline/report.py ====
import os
from pyspark.sql import functions as F
from pipeline.parse import parse_line


def solve(spark, input_dir):
    rows = []
    for root, _, files in os.walk(input_dir):
        for name in files:
            if name.endswith(".log"):
                with open(os.path.join(root, name)) as fh:
                    for line in fh:
                        r = parse_line(line)
                        if r:
                            rows.append((r["hour"], r["endpoint"], r["status"], r["bytes"]))
    df = spark.createDataFrame(rows, "hour string, endpoint string, status int, bytes long")
    return (df.groupBy("hour", "endpoint").agg(
                F.count("*").alias("requests"),
                F.sum(F.when(F.col("status") >= 500, 1).otherwise(0)).cast("long").alias("errors"),
                F.sum("bytes").cast("long").alias("bytes"))
            .orderBy("hour", "endpoint"))
"""
MUTANTS = [
    SOLUTION.replace('.astimezone(dt.timezone.utc)', ''),
    SOLUTION.replace('return "/".join("{id}" if s.isdigit() else s for s in path.split("/"))', 'return path'),
    SOLUTION.replace('    if "bot" in agent.lower():\n        return None\n', ''),
    SOLUTION.replace('    if len(path) > 1 and path.endswith("/"):\n        path = path.rstrip("/") or "/"\n', ''),
]

MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def line(ip, t, off, path, status, size, agent="Mozilla/5.0", method="GET", user="-"):
    sign = "+" if off >= 0 else "-"
    stamp = f"{t.day:02d}/{MON[t.month - 1]}/{t.year}:{t:%H:%M:%S} {sign}{abs(off):02d}00"
    return f'{ip} - {user} [{stamp}] "{method} {path} HTTP/1.1" {status} {size} "-" "{agent}"'


T = dt.datetime


def tests():
    a = [line("10.0.0.1", T(2026, 3, 4, 10, 12, 1), 1, "/api/orders/42/?full=1", 200, 512),
         line("10.0.0.2", T(2026, 3, 4, 9, 59, 0), 0, "/api/orders/7", 503, "-"),
         line("10.0.0.3", T(2026, 3, 4, 10, 5, 0), 1, "/", 200, 100, user="ana"),
         line("10.0.0.4", T(2026, 3, 4, 10, 6, 0), 1, "/api/orders/42", 200, 300, agent="Googlebot/2.1"),
         "server started on :8080",
         '10.0.0.9 - - [04/Mar/2026:10:0']
    b = [line("10.1.0.1", T(2026, 3, 4, 4, 30, 0), -5, "/api/users/12/orders/3", 500, 80, method="POST"),
         line("10.1.0.2", T(2026, 3, 4, 9, 10, 0), -5, "/api/users/v2", 200, 40, agent="curl/8.0")]
    t = [folder({"eu/access.log": "\n".join(a) + "\n", "us/2026/03/access.log": "\n".join(b) + "\n", "us/notes.txt": "rotate weekly\n"}),
         folder({"x.log": line("1.1.1.1", T(2026, 1, 1, 0, 30, 0), 2, "/health/", 200, 2) + "\n"})]
    r = rng(3151)
    paths = ["/", "/api/orders/42", "/api/orders/7/?x=1", "/api/users/3/", "/shop?page=2", "/api/v2/items/99"]
    agents = ["Mozilla/5.0", "curl/8.0", "Bingbot/2.0", "Mozilla/5.0 (compatible; AhrefsBOT)"]
    for _ in range(6):
        files = {}
        for k in range(r.randint(1, 3)):
            off = r.choice([-5, 0, 1, 2])
            ls = [line(f"10.0.0.{r.randint(1, 9)}", T(2026, 3, 4, r.randint(0, 3), r.randint(0, 59), 0), off, r.choice(paths),
                       r.choice([200, 200, 404, 500, 502]), r.choice([0, 10, 512, "-"]), agent=r.choice(agents)) for _ in range(r.randint(2, 7))]
            if r.random() < 0.4:
                ls.insert(1, "kill -HUP received")
            files[f"srv{k}/access.log"] = "\n".join(ls) + "\n"
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
