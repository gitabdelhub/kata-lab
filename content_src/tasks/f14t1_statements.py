from kit import folder, rng
import datetime as dt

ID = "f14t1"
NAME = "Bank Statements from Two Banks"
LANG = "pyspark"
PARAMS = ["spark", "input_dir"]
MINUTES = 25
TAGS = ["consigne longue", "formats régionaux", "relevés qui se chevauchent", "doublons légitimes"]
DESC = """
<p>Finance downloads the bank statements of all our accounts every few days and drops them in <code>input_dir</code> (at any depth, files ending with <code>.csv</code>). We work with two banks, and they do not write numbers and dates the same way.</p>
<p>A statement starts with a few lines beginning with <code>#</code>; one of them is <code>#&nbsp;account:&nbsp;&lt;id&gt;</code> and gives the account (spaces around the id do not matter). The first line not starting with <code>#</code> is a header naming the columns <code>date</code>, <code>label</code> and <code>amount</code>, in an order that depends on the bank. If the header uses <code>;</code> as a separator, the file comes from our European bank: amounts use a decimal comma and a dot between thousands (<code>-1.234,50</code>) and dates are <code>dd/MM/yyyy</code>. Otherwise the separator is <code>,</code>, the file comes from our American bank, amounts use a decimal point and may be quoted with commas between thousands (<code>"1,234.50"</code>), and dates are <code>MM/dd/yyyy</code>. A positive amount is a credit, a negative one a debit.</p>
<p>Because statements are downloaded every few days, two statements of the same account usually overlap and the same transaction appears in both. Inside one statement, however, two identical lines are two real transactions (two coffees bought the same day). So a transaction line (same account, date, label and amount) must be counted as many times as it appears in the statement where it appears the most.</p>
<p>Your task is to return, for each account and month, the columns <code>account</code>, <code>month</code> (string <code>yyyy-MM</code>), <code>credits</code> (double, total of positive amounts), <code>debits</code> (double, total of negative amounts written as a positive number), both rounded to 2 decimals, and <code>transactions</code> (long), sorted by <code>account</code>, then <code>month</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
import os
from pyspark.sql import SparkSession, DataFrame, functions as F


def solve(spark: SparkSession, input_dir: str) -> DataFrame:
    # write your code here
    return spark.read.csv(input_dir, header=True)
"""
SOLUTION = """
import csv
import datetime as dt
import os
from collections import Counter
from pyspark.sql import functions as F


def amount(s, eu):
    s = s.strip().replace(" ", "")
    if eu:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")
    return float(s)


def read_statement(path):
    with open(path, newline="") as fh:
        lines = fh.read().splitlines()
    account, i = None, 0
    while i < len(lines) and lines[i].startswith("#"):
        key, _, value = lines[i][1:].partition(":")
        if key.strip().lower() == "account":
            account = value.strip()
        i += 1
    eu = ";" in lines[i]
    reader = csv.reader(lines[i:], delimiter=";" if eu else ",")
    header = [h.strip().lower() for h in next(reader)]
    fmt = "%d/%m/%Y" if eu else "%m/%d/%Y"
    out = []
    for row in reader:
        if not any(c.strip() for c in row):
            continue
        r = dict(zip(header, row))
        day = dt.datetime.strptime(r["date"].strip(), fmt).date()
        out.append((account, day, r["label"].strip(), amount(r["amount"], eu)))
    return out


def solve(spark, input_dir):
    best = Counter()
    for root, _, files in os.walk(input_dir):
        for name in files:
            if name.endswith(".csv"):
                c = Counter(read_statement(os.path.join(root, name)))
                for k, n in c.items():
                    best[k] = max(best[k], n)
    rows = [(acc, day.strftime("%Y-%m"), amt) for (acc, day, _, amt), n in best.items() for _ in range(n)]
    df = spark.createDataFrame(rows, "account string, month string, amount double")
    return (df.groupBy("account", "month").agg(
                F.round(F.sum(F.when(F.col("amount") > 0, F.col("amount")).otherwise(0.0)), 2).alias("credits"),
                F.round(-F.sum(F.when(F.col("amount") < 0, F.col("amount")).otherwise(0.0)), 2).alias("debits"),
                F.count("*").alias("transactions"))
            .orderBy("account", "month"))
"""
MUTANTS = [
    SOLUTION.replace("c = Counter(read_statement(os.path.join(root, name)))", "c = Counter(set(read_statement(os.path.join(root, name))))"),
    SOLUTION.replace("best[k] = max(best[k], n)", "best[k] = best[k] + n"),
    SOLUTION.replace('fmt = "%d/%m/%Y" if eu else "%m/%d/%Y"', 'fmt = "%d/%m/%Y"'),
]


def eu_num(x):
    s = f"{abs(x):,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    return ("-" if x < 0 else "") + s


def us_num(x):
    s = f"{x:,.2f}"
    return f'"{s}"' if "," in s else s


def statement(account, eu, lines, order=("date", "label", "amount"), extra=True):
    head = ["# Statement export", f"#  account:  {account} "] if extra else [f"# account: {account}"]
    if eu:
        head.append(";".join(order))
        for d, lab, amt in lines:
            v = {"date": d.strftime("%d/%m/%Y"), "label": lab, "amount": eu_num(amt)}
            head.append(";".join(v[k] for k in order))
    else:
        head.append(",".join(order))
        for d, lab, amt in lines:
            v = {"date": d.strftime("%m/%d/%Y"), "label": lab, "amount": us_num(amt)}
            head.append(",".join(v[k] for k in order))
    return "\n".join(head) + "\n"


D = dt.date


def tests():
    a = [(D(2026, 3, 4), "Coffee", -2.5), (D(2026, 3, 4), "Coffee", -2.5), (D(2026, 3, 5), "Salary", 1234.5)]
    b = [(D(2026, 3, 5), "Salary", 1234.5), (D(2026, 3, 4), "Coffee", -2.5), (D(2026, 4, 1), "Rent", -900.0)]
    t = [folder({"eu/fr-0305.csv": statement("FR01", True, a), "eu/fr-0402.csv": statement("FR01", True, b, ("amount", "date", "label")),
                 "us/one.csv": statement("US77", False, [(D(2026, 3, 4), "Wire in", 2500.0), (D(2026, 4, 3), "Card", -12.99)], ("label", "amount", "date")),
                 "us/readme.txt": "not a statement\n"}),
         folder({"x.csv": statement("A", False, [(D(2026, 1, 2), "Fee", -1.0)], extra=False),
                 "y.csv": statement("A", False, [(D(2026, 1, 2), "Fee", -1.0), (D(2026, 1, 2), "Fee", -1.0)], extra=False)})]
    r = rng(3141)
    labels = ["Coffee", "Rent", "Salary", "Card", "Transfer"]
    for _ in range(6):
        files = {}
        for acc, eu in (("FR01", True), ("US77", False)):
            pool = [(D(2026, r.randint(1, 4), r.randint(1, 12)), r.choice(labels), r.choice([-2.5, -1250.75, 3000.0, -9.99, 45.1])) for _ in range(r.randint(2, 6))]
            for k in range(r.randint(1, 3)):
                part = r.sample(pool, r.randint(1, len(pool)))
                if r.random() < 0.4:
                    part.append(part[0])
                order = r.choice([("date", "label", "amount"), ("amount", "label", "date"), ("label", "date", "amount")])
                files[f"{'eu' if eu else 'us'}/s{k}.csv"] = statement(acc, eu, part, order, extra=r.random() < 0.5)
        t.append(folder(files))
    return [{"input_dir": x} for x in t]
