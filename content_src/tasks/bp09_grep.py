import json
import os

from kit import exercism, rng, EXERCISM, BANKS

ID = "bp09"
NAME = "Mini grep over Log Files"
LANG = "python"
PARAMS = ["pattern", "flags", "files", "contents"]
MINUTES = 20
TAGS = ["fichiers", "options", "ordre de sortie", "lecture de consigne longue"]
SOURCE = EXERCISM + " · grep"
IO = [("input", "string pattern"), ("input", "array.string flags"), ("input", "array.string files"),
      ("input", "dictionary contents"), ("output", "array.string")]
SUMMARY_FR = "Coder un petit grep : chercher un texte fixe dans des fichiers (dans l'ordre donné), avec les options -n (numéro de ligne), -l (noms de fichiers seulement), -i (sans casse), -v (inverser), -x (ligne entière). Avec plusieurs fichiers, chaque ligne commence par 'nom:'."
HINTS = ["Écris d'abord une fonction match(ligne) qui gère -i, -x puis -v ; le reste n'est que du formatage.",
         "Ordre du préfixe : 'fichier:' (si plusieurs fichiers), puis 'numéro:' (si -n), puis la ligne. Avec -l, chaque fichier apparaît une seule fois."]
DESC = """
<p>The support team wants a tiny search tool for log files, similar to the Unix <code>grep</code> command. You are given:</p>
<ul><li><code>pattern</code>: a fixed string to search for (not a regular expression);</li><li><code>flags</code>: a list of options, among <code>"-n"</code>, <code>"-l"</code>, <code>"-i"</code>, <code>"-v"</code> and <code>"-x"</code>;</li><li><code>files</code>: the names of the files to search, <b>in this order</b>;</li><li><code>contents</code>: a dictionary that maps every file name to the list of its lines.</li></ul>
<p>A line <b>matches</b> if it contains <code>pattern</code>. The options change this rule and the output:</p>
<ul><li><code>-i</code>: the comparison ignores the case;</li><li><code>-x</code>: the line must be <b>equal</b> to the pattern, not just contain it;</li><li><code>-v</code>: select the lines that do <b>not</b> match;</li><li><code>-n</code>: write the line number (starting at 1) and a colon before each line;</li><li><code>-l</code>: return only the names of the files that have at least one selected line, once each.</li></ul>
<p>When several files are searched, every output line starts with the file name and a colon, before the line number if any (for example <code>"app.log:3:timeout"</code>).</p>
<p>Your task is to return the list of output lines, in the order of the files, then of the lines.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(pattern, flags, files, contents):
    # write your code here
    return []
"""
SOLUTION = """
def solution(pattern, flags, files, contents):
    def match(line):
        a, b = (line.lower(), pattern.lower()) if "-i" in flags else (line, pattern)
        ok = a == b if "-x" in flags else b in a
        return ok != ("-v" in flags)
    out = []
    for name in files:
        for i, line in enumerate(contents[name], 1):
            if not match(line):
                continue
            if "-l" in flags:
                out.append(name)
                break
            prefix = (name + ":" if len(files) > 1 else "") + (str(i) + ":" if "-n" in flags else "")
            out.append(prefix + line)
    return out
"""
ALT = ["""
def solution(pattern, flags, files, contents):
    f = set(flags)
    res = []
    for name in files:
        hits = []
        for no, line in enumerate(contents[name], start=1):
            l, p = (line.casefold(), pattern.casefold()) if "-i" in f else (line, pattern)
            m = (l == p) if "-x" in f else (p in l)
            if "-v" in f:
                m = not m
            if m:
                hits.append((no, line))
        if "-l" in f:
            if hits:
                res.append(name)
            continue
        for no, line in hits:
            parts = ([name] if len(files) > 1 else []) + ([str(no)] if "-n" in f else []) + [line]
            res.append(":".join(parts))
    return res
"""]
MUTANTS = [
    """
def solution(pattern, flags, files, contents):
    out = []
    for name in files:
        for i, line in enumerate(contents[name], 1):
            a, b = (line.lower(), pattern.lower()) if "-i" in flags else (line, pattern)
            ok = a == b if "-x" in flags else b in a
            if ok == ("-v" in flags):
                continue
            if "-l" in flags:
                out.append(name)
                continue
            prefix = (name + ":" if len(files) > 1 else "") + (str(i) + ":" if "-n" in flags else "")
            out.append(prefix + line)
    return out
""",
    """
def solution(pattern, flags, files, contents):
    out = []
    for name in files:
        for i, line in enumerate(contents[name], 1):
            a, b = (line.lower(), pattern.lower()) if "-i" in flags else (line, pattern)
            ok = a == b if "-x" in flags else b in a
            if ok == ("-v" in flags):
                continue
            if "-l" in flags:
                out.append(name)
                break
            prefix = (str(i) + ":" if "-n" in flags else "") + (name + ":" if len(files) > 1 else "")
            out.append(prefix + line)
    return out
""",
]


def _texts():
    data = json.load(open(os.path.join(BANKS, "exercism", "grep.json"), encoding="utf-8"))
    out, cur = {}, None
    for c in data["comments"]:
        s = c.strip()
        if s.endswith(".txt"):
            cur = s
            out[cur] = []
        elif cur and s.startswith("|"):
            out[cur].append(s[1:s.rindex("|")].rstrip())
    return out


TEXTS = _texts()
CASES = exercism("grep")
LOGS = {"app.log": ["boot ok", "db timeout", "retry 1", "DB TIMEOUT", "done"],
        "worker.log": ["start", "job 7 timeout", "end"]}


def tests():
    t = [{"pattern": "timeout", "flags": ["-n", "-i"], "files": ["app.log", "worker.log"], "contents": LOGS},
         {"pattern": "timeout", "flags": ["-l"], "files": ["app.log", "worker.log"], "contents": LOGS}]
    for i, _ in CASES:
        t.append({"pattern": i["pattern"], "flags": i["flags"], "files": i["files"], "contents": {f: TEXTS[f] for f in i["files"]}})
    r = rng(109)
    for _ in range(3):
        files = r.sample(list(LOGS), r.randint(1, 2))
        t.append({"pattern": r.choice(["timeout", "o", "DB", "done"]), "flags": r.sample(["-n", "-i", "-v", "-x", "-l"], r.randint(0, 3)),
                  "files": files, "contents": {f: LOGS[f] for f in files}})
    return t


def expected():
    return [None, None] + [e for _, e in CASES] + [None] * 3
