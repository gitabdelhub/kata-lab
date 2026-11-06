from kit import rng

ID = "h06t4"
NAME = "Versioned Config Store"
LANG = "python"
PARAMS = ["queries"]
MINUTES = 35
TAGS = ["système à plusieurs commandes", "versions", "retour arrière", "tri de sortie", "cas limites"]
IO = [("input", "array.array.string queries"), ("output", "array.string")]
DESC = """
<p>Implement a small configuration store used by our services. Each query is a list of strings; process them in order and return one string per query.</p>
<p>The store holds keys per service. Each service has its own <b>version</b> counter, starting at 0. Every query that really changes a service increases its version by 1 and records the new state of the service as that version.</p>
<ul>
<li><code>["SET", service, key, value]</code>: sets the key. Returns the new version of the service. If the key already has exactly this value, nothing changes and the current version is returned.</li>
<li><code>["DELETE", service, key]</code>: removes the key. Returns the new version, or <code>"missing"</code> if the key does not exist (nothing changes).</li>
<li><code>["GET", service, key]</code>: returns the current value, or <code>""</code> if there is none.</li>
<li><code>["GET_AT", service, key, version]</code>: returns the value the key had at that version of the service (version 0 is the empty service), or <code>""</code>. If the version is greater than the current version, returns <code>"invalid"</code>.</li>
<li><code>["ROLLBACK", service, version]</code>: makes the state of the service equal to its state at that version. This is a change: it creates a new version, which is returned. Returns <code>"invalid"</code> if the version is greater than the current version. Rolling back to a state equal to the current one still creates a new version.</li>
<li><code>["SCAN", service, prefix]</code>: returns the current keys that start with <code>prefix</code>, as <code>"key=value"</code> items sorted by key and joined with <code>","</code>, or <code>""</code>.</li>
<li><code>["CHANGED", service, v1, v2]</code>: returns the keys whose value differs between versions <code>v1</code> and <code>v2</code> (a key present in only one of them differs), sorted and joined with <code>","</code>, or <code>""</code>. Returns <code>"invalid"</code> if one of the versions is greater than the current version.</li>
</ul>
<p>Versions in queries are written as strings of digits. An unknown service is an empty service at version 0.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(queries):
    # write your code here
    return []
"""
SOLUTION = """
def solution(queries):
    history = {}   # service -> liste des états ; history[s][v] = dict de l'état à la version v

    def states(service):
        if service not in history:
            history[service] = [{}]          # version 0 : service vide
        return history[service]

    def save(service, new_state):
        states(service).append(new_state)
        return str(len(history[service]) - 1)

    out = []
    for q in queries:
        op, service = q[0], q[1]
        st = states(service)
        cur = st[-1]
        last = len(st) - 1
        if op == "SET":
            key, value = q[2], q[3]
            if key in cur and cur[key] == value:
                out.append(str(last))
            else:
                new = dict(cur)
                new[key] = value
                out.append(save(service, new))
        elif op == "DELETE":
            key = q[2]
            if key not in cur:
                out.append("missing")
            else:
                new = dict(cur)
                del new[key]
                out.append(save(service, new))
        elif op == "GET":
            out.append(cur.get(q[2], ""))
        elif op == "GET_AT":
            v = int(q[3])
            if v > last:
                out.append("invalid")
            else:
                out.append(st[v].get(q[2], ""))
        elif op == "ROLLBACK":
            v = int(q[2])
            if v > last:
                out.append("invalid")
            else:
                out.append(save(service, dict(st[v])))
        elif op == "SCAN":
            items = []
            for key in sorted(cur):
                if key.startswith(q[2]):
                    items.append(key + "=" + cur[key])
            out.append(",".join(items))
        elif op == "CHANGED":
            v1, v2 = int(q[2]), int(q[3])
            if v1 > last or v2 > last:
                out.append("invalid")
            else:
                a, b = st[v1], st[v2]
                keys = []
                for key in a:
                    if key not in b or a[key] != b[key]:
                        keys.append(key)
                for key in b:
                    if key not in a:
                        keys.append(key)
                keys.sort()
                out.append(",".join(keys))
    return out
"""
MUTANTS = [
    SOLUTION.replace("            if key in cur and cur[key] == value:\n                out.append(str(last))\n            else:\n                new = dict(cur)", "            if False:\n                pass\n            else:\n                new = dict(cur)"),
    SOLUTION.replace("out.append(save(service, dict(st[v])))", "history[service] = st[: v + 1]\n                out.append(str(v))"),
    SOLUTION.replace("                for key in b:\n                    if key not in a:\n                        keys.append(key)\n", ""),
    SOLUTION.replace("            if v > last:\n                out.append(\"invalid\")\n            else:\n                out.append(st[v].get", "            if v > last + 1:\n                out.append(\"invalid\")\n            else:\n                out.append(st[min(v, last)].get"),
    SOLUTION.replace("new = dict(cur)\n                new[key] = value", "new = cur\n                new[key] = value"),
]


def tests():
    t = [{"queries": [["SET", "api", "timeout", "30"], ["SET", "api", "retries", "3"], ["SET", "api", "timeout", "30"], ["SET", "api", "timeout", "45"],
                      ["GET_AT", "api", "timeout", "1"], ["DELETE", "api", "retries"], ["DELETE", "api", "retries"], ["ROLLBACK", "api", "2"],
                      ["GET", "api", "retries"], ["SCAN", "api", "t"], ["CHANGED", "api", "3", "5"], ["GET_AT", "api", "timeout", "9"], ["GET", "web", "x"]]},
         {"queries": [["SET", "s", "a.b", "1"], ["SET", "s", "a.c", "2"], ["SET", "s", "b", "3"], ["SCAN", "s", "a."], ["ROLLBACK", "s", "0"],
                      ["SCAN", "s", ""], ["CHANGED", "s", "0", "4"], ["CHANGED", "s", "3", "2"], ["ROLLBACK", "s", "7"], ["GET_AT", "s", "b", "4"]]}]
    r = rng(4064)
    keys = ["a", "ab", "b", "db.host", "db.port"]
    for _ in range(9):
        qs, ver = [], {}
        for _ in range(r.randint(8, 60)):
            s = r.choice(["api", "web"])
            v = ver.get(s, 0)
            op = r.choice(["SET"] * 4 + ["DELETE", "GET", "GET_AT", "ROLLBACK", "SCAN", "CHANGED"])
            if op == "SET":
                qs.append(["SET", s, r.choice(keys), r.choice(["1", "2", "on"])])
                ver[s] = v + 1
            elif op == "DELETE":
                qs.append(["DELETE", s, r.choice(keys)])
            elif op == "GET":
                qs.append(["GET", s, r.choice(keys)])
            elif op == "GET_AT":
                qs.append(["GET_AT", s, r.choice(keys), str(r.randint(0, v + 1))])
            elif op == "ROLLBACK":
                qs.append(["ROLLBACK", s, str(r.randint(0, v + 1))])
                ver[s] = v + 1
            elif op == "SCAN":
                qs.append(["SCAN", s, r.choice(["", "a", "db.", "z"])])
            else:
                qs.append(["CHANGED", s, str(r.randint(0, v + 1)), str(r.randint(0, v))])
        t.append({"queries": qs})
    return t
