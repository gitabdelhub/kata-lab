from kit import rng

ID = "h13t4"
NAME = "Customer Deduplication"
LANG = "python"
PARAMS = ["records"]
MINUTES = 35
TAGS = ["normalisation", "groupes transitifs", "union-find", "vote du nom", "beaucoup de lignes"]
IO = [("input", "array.array.string records"), ("output", "array.string")]
DESC = """
<p>Our CRM contains duplicates. <code>records</code> is a list of <code>[id, name, email, phone]</code> (all strings, <code>id</code> is made of digits; <code>email</code> and <code>phone</code> can be empty).</p>
<p>Normalize the contact fields first:</p>
<ul><li><b>email</b>: trim spaces and convert to lower case. Then, in the part before <code>@</code>, remove everything from the first <code>+</code> (<code>ana+shop@x.ma</code> is <code>ana@x.ma</code>). For the domain <code>gmail.com</code> only, also remove the dots of that part (<code>a.na@gmail.com</code> is <code>ana@gmail.com</code>). An email without <code>@</code> is ignored.</li>
<li><b>phone</b>: keep only the digits. If they start with <code>00212</code>, replace that prefix with <code>0</code>; else if they start with <code>212</code>, replace it with <code>0</code>. The result is valid only if it has exactly 10 digits; an invalid phone is ignored.</li></ul>
<p>Two records belong to the same customer when they share a normalized email or a normalized phone, and this is transitive: if A shares an email with B and B shares a phone with C, then A, B and C are the same customer.</p>
<p>For each customer, the <b>name</b> is the most frequent name among its records (names are compared after trimming and in lower case); on a tie, the name of the record with the smallest id among the tied names wins. Write the name as it appears (trimmed) in the record with the smallest id that has it.</p>
<p>Your task is to return one string per customer, <code>"ids|name"</code> where <code>ids</code> are its record ids sorted as numbers and joined with <code>","</code>, sorted by the smallest id of each customer. There can be up to 6 000 records.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(records):
    # write your code here
    return []
"""
SOLUTION = """
def norm_email(e):
    e = e.strip().lower()
    if "@" not in e:
        return None
    local, domain = e.split("@", 1)
    if "+" in local:
        local = local[: local.index("+")]
    if domain == "gmail.com":
        local = local.replace(".", "")
    return local + "@" + domain


def norm_phone(p):
    digits = ""
    for ch in p:
        if ch.isdigit():
            digits += ch
    if digits.startswith("00212"):
        digits = "0" + digits[5:]
    elif digits.startswith("212"):
        digits = "0" + digits[3:]
    if len(digits) != 10:
        return None
    return digits


def solution(records):
    # Union-find : parent[i] mène au représentant du groupe de l'enregistrement i
    n = len(records)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    first_with = {}       # contact normalisé -> premier enregistrement qui l'a
    for i in range(n):
        rid, name, email, phone = records[i]
        keys = []
        e = norm_email(email)
        if e is not None:
            keys.append("e:" + e)
        ph = norm_phone(phone)
        if ph is not None:
            keys.append("p:" + ph)
        for key in keys:
            if key in first_with:
                union(i, first_with[key])
            else:
                first_with[key] = i

    groups = {}
    for i in range(n):
        r = find(i)
        if r not in groups:
            groups[r] = []
        groups[r].append(i)

    out = []
    for r in groups:
        members = groups[r]
        ids = []
        for i in members:
            ids.append(int(records[i][0]))
        ids.sort()
        # Vote : nom en minuscules -> [nombre, plus petit id, nom tel qu'écrit pour ce plus petit id]
        votes = {}
        for i in members:
            rid = int(records[i][0])
            shown = records[i][1].strip()
            key = shown.lower()
            if key not in votes:
                votes[key] = [0, rid, shown]
            votes[key][0] += 1
            if rid < votes[key][1]:
                votes[key][1] = rid
                votes[key][2] = shown
        best = None
        for key in votes:
            c, rid, shown = votes[key]
            if best is None or c > best[0] or (c == best[0] and rid < best[1]):
                best = [c, rid, shown]
        id_text = []
        for x in ids:
            id_text.append(str(x))
        out.append([ids[0], ",".join(id_text) + "|" + best[2]])
    out.sort()
    result = []
    for first, text in out:
        result.append(text)
    return result
"""
MUTANTS = [
    SOLUTION.replace('    if domain == "gmail.com":\n        local = local.replace(".", "")', '    local = local.replace(".", "")'),
    SOLUTION.replace('    elif digits.startswith("212"):\n        digits = "0" + digits[3:]\n', ''),
    SOLUTION.replace("            if best is None or c > best[0] or (c == best[0] and rid < best[1]):", "            if best is None or c > best[0]:"),
    SOLUTION.replace("        ids.sort()", "        ids.sort(key=str)"),
    SOLUTION.replace("            key = shown.lower()", "            key = shown"),
]


def tests():
    t = [{"records": [["1", "Amina Diallo", "Amina.D@gmail.com", ""], ["2", "amina diallo ", "aminad+promo@gmail.com", "06 12 34 56 78"],
                      ["3", "A. Diallo", "", "+212 612-345-678"], ["4", "Omar", "omar@x.ma", "0700000000"], ["5", "Omar", "o.mar@x.ma", ""],
                      ["10", "A. Diallo", "a.diallo@corp.ma", "00212612345678"], ["7", "Sara", "not-an-email", "123"]]},
         {"records": [["9", "Kofi", "k@y.tg", ""], ["8", "kofi", "", "0011223344"], ["12", "KOFI", "k@y.tg", "0011223344"],
                      ["11", "Ama", "", "0011223344"], ["30", "Ama", "", ""]]}]
    r = rng(4134)
    names = ["Amina", "amina ", "Omar", "Sara", "Kofi", "Ama"]
    for k in range(9):
        n = r.randint(5, 40) if k < 8 else 6000
        recs = []
        ids = r.sample(range(1, 3 * n + 1), n)
        for i in range(n):
            u = r.randint(0, max(3, n // 3))
            email = r.choice([f"user{u}@gmail.com", f"us.er{u}@gmail.com", f"user{u}+x@gmail.com", f"U{u}@corp.ma", f"u.{u}@corp.ma", "", "bad"])
            phone = r.choice([f"06{u:08d}", f"+212 6{u:08d}", f"002126{u:08d}", "", "12345"])
            recs.append([str(ids[i]), r.choice(names), email, phone])
        t.append({"records": recs})
    return t
