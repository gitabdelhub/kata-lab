from kit import folder, rng
import json

ID = "f13t1"
NAME = "Three Systems, One Customer"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["consigne longue", "CSV et JSON mélangés", "normalisation", "dernière valeur non vide par champ"]
DESC = """
<p>Three systems know our customers, and the data team must build one golden record per customer. Each system drops its exports in its own folder of <code>input_dir</code>:</p>
<p><code>crm/</code> holds CSV files with a header and the columns <code>customer_ref</code>, <code>email</code>, <code>phone</code>, <code>city</code> and <code>updated</code> (<code>yyyy-MM-dd HH:mm:ss</code>). <code>shop/</code> holds JSON lines files where each object looks like <code>{"email": ..., "tel": ..., "town": ..., "ts": ...}</code>, <code>ts</code> being a Unix time in seconds. <code>support/</code> holds JSON lines files where each object looks like <code>{"contact": {"mail": ..., "phone": ...}, "updated_at": ...}</code>, with an ISO time such as <code>2026-03-01T10:00:00Z</code>; the support tool does not know the city. Files have the extension of their format (<code>.csv</code> or <code>.jsonl</code>); anything else is ignored. All times are UTC.</p>
<p>Customers are matched by email only, after trimming it and putting it in lower case; a record whose email does not contain <code>@</code> cannot be matched and is dropped. Phone numbers are typed in every possible way (<code>+212 6 12-34-56-78</code>, <code>0612345678</code>, <code>(212) 612 345 678</code>): keep only the digits, then remove a leading <code>212</code> country code if there is one, then a leading <code>0</code>; what remains is the phone. City names are trimmed and written in title case (<code>casablanca</code> becomes <code>Casablanca</code>). An empty or missing value is not a value.</p>
<p>For each field, the golden record takes the value of the <b>most recent</b> record (by update time, whatever the system) that has a value for this field. If two records with a value have exactly the same time, any of them is fine because they always agree in the tests.</p>
<p>Your task is to return one row per customer with the columns <code>email</code>, <code>phone</code>, <code>city</code> (strings, <code>null</code> if no record has a value) and <code>systems</code> (long, number of the three systems in which the customer appears), sorted by <code>email</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.json(os.path.join(input_dir, "shop"))
"""
SOLUTION = """
import csv
import datetime as dt
import json
import os
import re
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def norm_phone(p):
    d = re.sub(r"\\D", "", p or "")
    if d.startswith("212"):
        d = d[3:]
    if d.startswith("0"):
        d = d[1:]
    return d or None


def clean(v):
    v = (v or "").strip()
    return v or None


def solve(spark, input_dir):
    rows = []
    for system in ("crm", "shop", "support"):
        base = os.path.join(input_dir, system)
        if not os.path.isdir(base):
            continue
        for root, _, files in os.walk(base):
            for name in files:
                path = os.path.join(root, name)
                if system == "crm" and name.endswith(".csv"):
                    with open(path, newline="") as fh:
                        for r in csv.DictReader(fh):
                            ts = dt.datetime.strptime(r["updated"].strip(), "%Y-%m-%d %H:%M:%S")
                            rows.append((system, r.get("email"), r.get("phone"), r.get("city"), ts))
                elif system != "crm" and name.endswith(".jsonl"):
                    with open(path) as fh:
                        for line in fh:
                            if not line.strip():
                                continue
                            o = json.loads(line)
                            if system == "shop":
                                ts = dt.datetime.fromtimestamp(int(o["ts"]), dt.timezone.utc).replace(tzinfo=None)
                                rows.append((system, o.get("email"), o.get("tel"), o.get("town"), ts))
                            else:
                                c = o.get("contact") or {}
                                ts = dt.datetime.strptime(o["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
                                rows.append((system, c.get("mail"), c.get("phone"), None, ts))
    out = []
    for system, email, phone, city, ts in rows:
        e = clean(email)
        if not e or "@" not in e:
            continue
        c = clean(city)
        out.append((system, e.lower(), norm_phone(phone), c.title() if c else None, ts))
    df = spark.createDataFrame(out, "system string, email string, phone string, city string, ts timestamp")
    w = Window.partitionBy("email").orderBy(F.col("ts").desc())
    return (df.groupBy("email").agg(
                F.max_by("phone", F.when(F.col("phone").isNotNull(), F.col("ts"))).alias("phone"),
                F.max_by("city", F.when(F.col("city").isNotNull(), F.col("ts"))).alias("city"),
                F.countDistinct("system").alias("systems"))
            .orderBy("email"))
"""
MUTANTS = [
    SOLUTION.replace('F.max_by("phone", F.when(F.col("phone").isNotNull(), F.col("ts")))', 'F.max_by("phone", F.col("ts"))'),
    SOLUTION.replace('''    if d.startswith("212"):
        d = d[3:]
''', ''),
    SOLUTION.replace('ts = dt.datetime.fromtimestamp(int(o["ts"]), dt.timezone.utc).replace(tzinfo=None)', 'ts = dt.datetime(2000, 1, 1)'),
]


def crm(rows):
    return "customer_ref,email,phone,city,updated\n" + "".join(f"C{i},{e},{p},{c},{u}\n" for i, (e, p, c, u) in enumerate(rows))


def epoch(s):
    import datetime as dt
    return int(dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp())


def shop(rows):
    return "".join(json.dumps({"email": e, "tel": p, "town": c, "ts": epoch(u)}) + "\n" for e, p, c, u in rows)


def support(rows):
    return "".join(json.dumps({"contact": {"mail": e, "phone": p}, "updated_at": u.replace(" ", "T") + "Z"}) + "\n" for e, p, u in rows)


def tests():
    t = [folder({"crm/2026/a.csv": crm([(" Ana@Mail.com", "0612345678", "casablanca", "2026-03-01 09:00:00"), ("bob@x.io", "", " rabat ", "2026-03-01 09:00:00"), ("no-email", "0611", "fes", "2026-03-01 09:00:00")]),
                 "shop/s.jsonl": shop([("ana@mail.com", "+212 6 99-88-77-66", "", "2026-03-02 10:00:00"), ("bob@x.io", "0655555555", "Tanger", "2026-02-01 10:00:00")]),
                 "support/t.jsonl": support([("ANA@mail.com ", "(212) 611 111 111", "2026-02-15 08:00:00"), ("cy@z.ma", "0700000000", "2026-03-03 12:00:00")]),
                 "support/old.json": "{}\n"}),
         folder({"shop/a.jsonl": shop([("d@d.d", "0600000001", "agadir", "2026-01-01 00:00:00"), ("d@d.d", "0600000002", None, "2026-01-02 00:00:00")])})]
    r = rng(3131)
    emails = ["ana@mail.com", "bob@x.io", "cy@z.ma", "dina@y.org"]
    phones = ["0612345678", "+212 6 12 34 56 78", "(212) 699 887 766", "", "0700000000"]
    cities = ["casablanca", " Rabat", "", "FES", "tanger "]
    for _ in range(6):
        used = set()

        def when():
            while True:
                s = f"2026-03-0{r.randint(1, 9)} {r.randint(0, 23):02d}:{r.randint(0, 5)}0:00"
                if s not in used:
                    used.add(s)
                    return s
        files = {}
        if r.random() < 0.9:
            files["crm/x.csv"] = crm([(r.choice(emails).upper() if r.random() < 0.3 else r.choice(emails), r.choice(phones), r.choice(cities), when()) for _ in range(r.randint(1, 4))])
        files["shop/y.jsonl"] = shop([(r.choice(emails), r.choice(phones) or None, r.choice(cities) or None, when()) for _ in range(r.randint(1, 4))])
        if r.random() < 0.8:
            files["support/z.jsonl"] = support([(r.choice(emails), r.choice(phones), when()) for _ in range(r.randint(1, 3))])
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
