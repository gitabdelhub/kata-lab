from kit import rng

ID = "h15t4"
NAME = "Data Lake Catalog"
LANG = "python"
PARAMS = ["queries"]
MINUTES = 40
TAGS = ["système à plusieurs commandes", "quotas", "instantanés et restauration", "copie profonde", "tri de sortie"]
IO = [("input", "array.array.string queries"), ("output", "array.string")]
DESC = """
<p>Implement the catalog of a data lake. Process <code>queries</code> in order (each query is a list of strings, sizes and quotas are written with digits) and return one string per query. Unless written otherwise, a query on an unknown database returns <code>"false"</code>.</p>
<ul>
<li><code>["CREATE_DB", db, quota]</code>: creates an empty database with a storage quota. <code>"true"</code>, or <code>"false"</code> if it already exists.</li>
<li><code>["SET_QUOTA", db, quota]</code>: changes the quota (it can become lower than the used storage). <code>"true"</code>.</li>
<li><code>["ADD_PARTITION", db, table, partition, size]</code>: adds a partition to a table (a table exists as long as it has at least one partition). Fails with <code>"false"</code> if the partition already exists in that table or if the used storage of the database plus <code>size</code> would be greater than the quota. Otherwise returns the remaining storage (<code>quota - used</code>) after the addition.</li>
<li><code>["DROP_PARTITION", db, table, partition]</code>: removes it and returns its size, or <code>"false"</code> if it does not exist.</li>
<li><code>["DROP_TABLE", db, table]</code>: removes all the partitions of the table and returns how many there were, or <code>"false"</code> if the table does not exist.</li>
<li><code>["TABLE_SIZE", db, table]</code>: the total size of the table, <code>"0"</code> if it does not exist.</li>
<li><code>["LARGEST", db, n]</code>: the <code>n</code> largest tables as <code>"name(size)"</code> items joined with <code>","</code>, by size (largest first), then name; <code>""</code> if there is no table.</li>
<li><code>["SNAPSHOT", db]</code>: saves the current tables and partitions of the database and returns a snapshot id <code>"db#k"</code>, where <code>k</code> is 1 for the first snapshot of this database, then 2, and so on.</li>
<li><code>["RESTORE", db, snapshot_id]</code>: replaces the tables and partitions of the database with the content of that snapshot (the quota is not changed, and a restore can exceed it). Returns the number of partitions after the restore, or <code>"false"</code> if the snapshot id was not created for this database. A snapshot stays valid after being restored, and later changes must not modify it.</li>
</ul>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(queries):
    # write your code here
    return []
"""
SOLUTION = """
def copy_tables(tables):
    # Copie profonde : un dict de tables, chaque table est un dict partition -> taille
    new = {}
    for name in tables:
        new[name] = dict(tables[name])
    return new


def solution(queries):
    dbs = {}          # db -> {"quota": int, "tables": {table: {partition: size}}, "snaps": [copies]}
    out = []

    def used(db):
        total = 0
        for name in dbs[db]["tables"]:
            for part in dbs[db]["tables"][name]:
                total += dbs[db]["tables"][name][part]
        return total

    for q in queries:
        op, db = q[0], q[1]
        if op == "CREATE_DB":
            if db in dbs:
                out.append("false")
            else:
                dbs[db] = {"quota": int(q[2]), "tables": {}, "snaps": []}
                out.append("true")
            continue
        if db not in dbs:
            out.append("false")
            continue
        d = dbs[db]
        tables = d["tables"]
        if op == "SET_QUOTA":
            d["quota"] = int(q[2])
            out.append("true")
        elif op == "ADD_PARTITION":
            table, part, size = q[2], q[3], int(q[4])
            if table in tables and part in tables[table]:
                out.append("false")
            elif used(db) + size > d["quota"]:
                out.append("false")
            else:
                if table not in tables:
                    tables[table] = {}
                tables[table][part] = size
                out.append(str(d["quota"] - used(db)))
        elif op == "DROP_PARTITION":
            table, part = q[2], q[3]
            if table not in tables or part not in tables[table]:
                out.append("false")
            else:
                size = tables[table][part]
                del tables[table][part]
                if len(tables[table]) == 0:
                    del tables[table]
                out.append(str(size))
        elif op == "DROP_TABLE":
            table = q[2]
            if table not in tables:
                out.append("false")
            else:
                out.append(str(len(tables[table])))
                del tables[table]
        elif op == "TABLE_SIZE":
            total = 0
            for part in tables.get(q[2], {}):
                total += tables[q[2]][part]
            out.append(str(total))
        elif op == "LARGEST":
            sizes = []
            for name in tables:
                total = 0
                for part in tables[name]:
                    total += tables[name][part]
                sizes.append((-total, name))
            sizes.sort()
            items = []
            for neg, name in sizes[: int(q[2])]:
                items.append(name + "(" + str(-neg) + ")")
            out.append(",".join(items))
        elif op == "SNAPSHOT":
            d["snaps"].append(copy_tables(tables))
            out.append(db + "#" + str(len(d["snaps"])))
        elif op == "RESTORE":
            sid = q[2]
            ok = False
            if sid.startswith(db + "#") and sid[len(db) + 1:].isdigit():
                k = int(sid[len(db) + 1:])
                if 1 <= k <= len(d["snaps"]):
                    ok = True
            if not ok:
                out.append("false")
            else:
                d["tables"] = copy_tables(d["snaps"][k - 1])
                count = 0
                for name in d["tables"]:
                    count += len(d["tables"][name])
                out.append(str(count))
    return out
"""
MUTANTS = [
    SOLUTION.replace("d[\"tables\"] = copy_tables(d[\"snaps\"][k - 1])", "d[\"tables\"] = d[\"snaps\"][k - 1]"),
    SOLUTION.replace("            elif used(db) + size > d[\"quota\"]:", "            elif used(db) + size >= d[\"quota\"]:"),
    SOLUTION.replace("                if len(tables[table]) == 0:\n                    del tables[table]\n", ""),
    SOLUTION.replace("            sizes.append((-total, name))", "            sizes.append((total, name))").replace("            sizes.sort()\n", "            sizes.sort(reverse=True)\n").replace("str(-neg)", "str(neg)"),
    SOLUTION.replace("if sid.startswith(db + \"#\") and sid[len(db) + 1:].isdigit():", "if \"#\" in sid and sid.split(\"#\")[-1].isdigit():").replace("k = int(sid[len(db) + 1:])", "k = int(sid.split(\"#\")[-1])"),
]


def tests():
    t = [{"queries": [["CREATE_DB", "sales", "100"], ["ADD_PARTITION", "sales", "orders", "dt=01", "40"], ["ADD_PARTITION", "sales", "orders", "dt=02", "30"],
                      ["ADD_PARTITION", "sales", "refunds", "dt=01", "30"], ["ADD_PARTITION", "sales", "refunds", "dt=02", "1"], ["SNAPSHOT", "sales"],
                      ["DROP_TABLE", "sales", "orders"], ["LARGEST", "sales", "5"], ["RESTORE", "sales", "sales#1"], ["TABLE_SIZE", "sales", "orders"],
                      ["DROP_PARTITION", "sales", "orders", "dt=01"], ["RESTORE", "sales", "sales#1"], ["RESTORE", "sales", "sales#2"], ["CREATE_DB", "sales", "5"]]},
         {"queries": [["ADD_PARTITION", "x", "t", "p", "1"], ["CREATE_DB", "x", "10"], ["CREATE_DB", "y", "10"], ["ADD_PARTITION", "x", "b", "p1", "5"],
                      ["ADD_PARTITION", "x", "a", "p1", "5"], ["LARGEST", "x", "1"], ["SNAPSHOT", "y"], ["RESTORE", "x", "y#1"], ["SET_QUOTA", "x", "4"],
                      ["ADD_PARTITION", "x", "a", "p2", "0"], ["DROP_PARTITION", "x", "a", "p1"], ["DROP_PARTITION", "x", "a", "p1"], ["TABLE_SIZE", "x", "a"],
                      ["LARGEST", "x", "5"], ["DROP_TABLE", "x", "a"]]}]
    r = rng(4154)
    for _ in range(9):
        qs = [["CREATE_DB", "lake", str(r.choice([50, 100, 200]))], ["CREATE_DB", "dev", "60"]]
        snaps = {"lake": 0, "dev": 0}
        for _ in range(r.randint(10, 70)):
            db = r.choice(["lake", "lake", "dev", "nope"])
            tb = r.choice(["orders", "users", "events"])
            op = r.choice(["ADD_PARTITION"] * 5 + ["DROP_PARTITION", "DROP_TABLE", "TABLE_SIZE", "LARGEST", "SNAPSHOT", "RESTORE", "SET_QUOTA"])
            if op == "ADD_PARTITION":
                qs.append([op, db, tb, f"dt={r.randint(1, 6)}", str(r.choice([0, 5, 10, 20, 35]))])
            elif op == "DROP_PARTITION":
                qs.append([op, db, tb, f"dt={r.randint(1, 6)}"])
            elif op in ("DROP_TABLE", "TABLE_SIZE"):
                qs.append([op, db, tb])
            elif op == "LARGEST":
                qs.append([op, db, str(r.randint(1, 3))])
            elif op == "SNAPSHOT":
                qs.append([op, db])
                if db in snaps:
                    snaps[db] += 1
            elif op == "RESTORE":
                other = r.choice(["lake", "dev"])
                qs.append([op, db, f"{other}#{r.randint(1, snaps[other] + 1)}"])
            else:
                qs.append([op, db, str(r.choice([20, 80, 150]))])
        t.append({"queries": qs})
    return t
