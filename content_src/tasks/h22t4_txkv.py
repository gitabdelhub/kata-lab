from kit import rng

ID = "h22t4"
NAME = "Transactional Key-Value Store"
LANG = "python"
PARAMS = ["commands"]
MINUTES = 40
TAGS = ["transactions imbriquées", "journal d'annulation", "compteur de valeurs en O(1)", "COMMIT global", "beaucoup de commandes"]
IO = [("input", "array.string commands"), ("output", "array.string")]
DESC = """
<p>Implement an in-memory key-value store with nested transactions. <code>commands</code> is a list of strings processed in order. Keys and values are words without spaces.</p>
<ul><li><code>"SET key value"</code>: sets the key. No output.</li>
<li><code>"DELETE key"</code>: removes the key (nothing happens if it does not exist). No output.</li>
<li><code>"GET key"</code>: outputs the value, or <code>"NULL"</code>.</li>
<li><code>"COUNT value"</code>: outputs how many keys currently have exactly this value.</li>
<li><code>"BEGIN"</code>: opens a new transaction, inside the current one if there is one. No output.</li>
<li><code>"ROLLBACK"</code>: cancels every change made since the <b>innermost</b> open transaction began, and closes that transaction only. Outputs <code>"NO TRANSACTION"</code> if no transaction is open, else nothing.</li>
<li><code>"COMMIT"</code>: makes all the changes permanent and closes <b>all</b> open transactions. Outputs <code>"NO TRANSACTION"</code> if no transaction is open, else nothing.</li></ul>
<p>Your task is to return the list of outputs. There can be up to 30 000 commands with many keys: <code>COUNT</code> must not scan all the keys, and <code>ROLLBACK</code> must only undo what changed.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(commands):
    # write your code here
    return []
"""
SOLUTION = """
def solution(commands):
    data = {}
    count = {}            # valeur -> nombre de clés qui l'ont
    undo = []             # une liste par transaction ouverte : [clé, ancienne valeur ou None]

    def put(key, value):
        # Change une clé (value None = supprimer) en tenant les compteurs à jour
        old = data.get(key)
        if old is not None:
            count[old] -= 1
            del data[key]
        if value is not None:
            data[key] = value
            count[value] = count.get(value, 0) + 1
        return old

    out = []
    for line in commands:
        p = line.split()
        op = p[0]
        if op == "SET" or op == "DELETE":
            key = p[1]
            value = p[2] if op == "SET" else None
            old = put(key, value)
            if len(undo) > 0:
                undo[-1].append([key, old])
        elif op == "GET":
            out.append(data.get(p[1], "NULL"))
        elif op == "COUNT":
            out.append(str(count.get(p[1], 0)))
        elif op == "BEGIN":
            undo.append([])
        elif op == "ROLLBACK":
            if len(undo) == 0:
                out.append("NO TRANSACTION")
            else:
                changes = undo.pop()
                # Annuler dans l'ordre inverse
                for i in range(len(changes) - 1, -1, -1):
                    key, old = changes[i]
                    put(key, old)
        elif op == "COMMIT":
            if len(undo) == 0:
                out.append("NO TRANSACTION")
            else:
                undo = []
    return out
"""
MUTANTS = [
    SOLUTION.replace("                for i in range(len(changes) - 1, -1, -1):", "                for i in range(len(changes)):"),
    SOLUTION.replace("            if len(undo) > 0:\n                undo[-1].append([key, old])", "            if len(undo) > 0:\n                undo[0].append([key, old])"),
    SOLUTION.replace("                undo = []", "                undo.pop()"),
    SOLUTION.replace("        if old is not None:\n            count[old] -= 1\n            del data[key]", "        if old is not None:\n            del data[key]"),
]


def tests():
    t = [{"commands": ["SET a 10", "SET b 10", "COUNT 10", "BEGIN", "SET a 20", "DELETE b", "COUNT 10", "BEGIN", "SET a 30", "SET a 31", "GET a",
                       "ROLLBACK", "GET a", "ROLLBACK", "GET a", "GET b", "COUNT 10", "ROLLBACK", "BEGIN", "SET c 5", "BEGIN", "DELETE c", "COMMIT",
                       "GET c", "ROLLBACK", "COMMIT"]},
         {"commands": ["BEGIN", "SET x 1", "SET x 1", "DELETE x", "DELETE x", "COUNT 1", "ROLLBACK", "COUNT 1", "GET x", "DELETE nope", "GET nope"]}]
    r = rng(4224)
    for k in range(9):
        cmds, depth = [], 0
        for _ in range(r.randint(10, 80) if k < 8 else 30000):
            op = r.choice(["SET"] * 5 + ["DELETE", "GET", "COUNT", "COUNT", "BEGIN", "ROLLBACK", "COMMIT"])
            key = f"k{r.randint(1, 8 if k < 8 else 3000)}"
            if op == "SET":
                cmds.append(f"SET {key} {r.choice(['red', 'blue', 'green'])}")
            elif op in ("DELETE", "GET"):
                cmds.append(f"{op} {key}")
            elif op == "COUNT":
                cmds.append(f"COUNT {r.choice(['red', 'blue', 'green', 'pink'])}")
            else:
                cmds.append(op)
        t.append({"commands": cmds})
    return t
