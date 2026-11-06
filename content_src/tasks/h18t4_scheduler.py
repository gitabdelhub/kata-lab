from kit import rng

ID = "h18t4"
NAME = "Pipeline Scheduler"
LANG = "python"
PARAMS = ["tasks", "workers"]
MINUTES = 35
TAGS = ["graphe de dépendances", "simulation avec workers", "priorités", "détection de cycle", "cas d'erreur"]
IO = [("input", "array.string tasks"), ("input", "integer workers"), ("output", "array.string")]
DESC = """
<p>An orchestrator runs the tasks of a data pipeline on <code>workers</code> identical workers. <code>tasks</code> is a list of strings <code>"name duration deps"</code>, where <code>deps</code> is a comma-separated list of task names or <code>-</code> when the task has no dependency. Durations are positive integers.</p>
<p>A task is <b>ready</b> when all its dependencies are finished. Time starts at 0. Whenever at least one worker is free and at least one task is ready, a free worker starts a ready task immediately. Ready tasks are started in this order: the longest duration first, then the name in alphabetical order. A task that starts at <code>s</code> ends at <code>s + duration</code>, and its worker and the tasks depending on it are free/ready at that exact time.</p>
<p>Your task is to return <code>"name:start-end"</code> for every task, sorted by start time, then name, followed by <code>"TOTAL end"</code> where <code>end</code> is the time the last task ends (0 if there is no task).</p>
<p>If a task depends on a name that is not in the list, or if the dependencies contain a cycle (so some tasks can never run), return <code>["ERROR"]</code> instead.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(tasks, workers):
    # write your code here
    return []
"""
SOLUTION = """
def solution(tasks, workers):
    duration, deps = {}, {}
    for line in tasks:
        name, d, dl = line.split()
        duration[name] = int(d)
        deps[name] = [] if dl == "-" else dl.split(",")
    for name in deps:
        for d in deps[name]:
            if d not in duration:
                return ["ERROR"]

    waiting_for = {}        # tâche -> nombre de dépendances pas encore finies
    children = {}
    for name in deps:
        waiting_for[name] = len(deps[name])
        children[name] = []
    for name in deps:
        for d in deps[name]:
            children[d].append(name)

    ready = []
    for name in deps:
        if waiting_for[name] == 0:
            ready.append(name)
    running = []            # [fin, nom]
    start = {}
    t = 0
    done = 0
    while done < len(duration):
        # Lancer les tâches prêtes sur les workers libres
        while len(ready) > 0 and len(running) < workers:
            best = None
            for name in ready:
                if best is None or duration[name] > duration[best] or (duration[name] == duration[best] and name < best):
                    best = name
            ready.remove(best)
            start[best] = t
            running.append([t + duration[best], best])
        if len(running) == 0:
            return ["ERROR"]            # plus rien ne tourne mais des tâches restent : cycle
        # Avancer jusqu'à la prochaine fin, et terminer toutes les tâches qui finissent à cet instant
        t = running[0][0]
        for r in running:
            if r[0] < t:
                t = r[0]
        still = []
        for end, name in running:
            if end == t:
                done += 1
                for c in children[name]:
                    waiting_for[c] -= 1
                    if waiting_for[c] == 0:
                        ready.append(c)
            else:
                still.append([end, name])
        running = still

    rows = []
    for name in start:
        rows.append((start[name], name))
    rows.sort()
    out = []
    for s, name in rows:
        out.append(name + ":" + str(s) + "-" + str(s + duration[name]))
    out.append("TOTAL " + str(t))
    return out
"""
MUTANTS = [
    SOLUTION.replace("if best is None or duration[name] > duration[best] or (duration[name] == duration[best] and name < best):", "if best is None or name < best:"),
    SOLUTION.replace("        if len(running) == 0:\n            return [\"ERROR\"]            # plus rien ne tourne mais des tâches restent : cycle\n", "        if len(running) == 0:\n            break\n"),
    SOLUTION.replace("    for name in deps:\n        for d in deps[name]:\n            if d not in duration:\n                return [\"ERROR\"]\n", "    for name in deps:\n        deps[name] = [d for d in deps[name] if d in duration]\n"),
    SOLUTION.replace("        while len(ready) > 0 and len(running) < workers:", "        while len(ready) > 0 and len(running) <= workers:"),
]


def tests():
    t = [{"tasks": ["extract 3 -", "clean 2 extract", "dims 4 -", "facts 5 clean,dims", "report 1 facts", "audit 2 extract"], "workers": 2},
         {"tasks": ["a 2 -", "b 2 -", "c 1 a,b", "d 1 c", "e 3 d,f", "f 1 e"], "workers": 3},
         {"tasks": ["load 1 missing"], "workers": 1}, {"tasks": [], "workers": 2}]
    r = rng(4184)
    for k in range(8):
        n = r.randint(3, 25) if k < 7 else 400
        names = [f"t{i:03d}" for i in range(n)]
        lines = []
        for i, nm in enumerate(names):
            ds = sorted(set(r.sample(names[:i], min(i, r.randint(0, 3))))) if i else []
            if k == 3 and i == n - 1:
                ds = ds + [names[-1]]
            lines.append(f"{nm} {r.choice([1, 2, 3, 5, 8])} {','.join(ds) if ds else '-'}")
        r.shuffle(lines)
        t.append({"tasks": lines, "workers": r.randint(1, 4)})
    return t
