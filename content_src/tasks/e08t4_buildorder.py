from kit import rng

ID = "e08t4"
NAME = "Pipeline Run Order"
LANG = "python"
PARAMS = ["jobs"]
MINUTES = 22
TAGS = ["graphe", "tri topologique (Kahn)", "heapq pour l'ordre", "détection de cycle"]
IO = [("input", "array.string jobs"), ("output", "array.string")]
DESC = """
<p>A data platform runs a set of jobs every night. Some jobs need other jobs to be finished first. You are given <code>jobs</code>, a list of strings of the form <code>"job: dep1, dep2"</code>, where the dependencies are the jobs that must run <b>before</b> <code>job</code>. A job without dependencies is written <code>"job:"</code>. A dependency that is not described by its own string is still a job (with no dependencies) and must be run too.</p>
<p>The scheduler runs one job at a time. At each step it runs, among the jobs whose dependencies are all finished, the one that comes first in <b>alphabetical order</b>.</p>
<p>Your task is to return the list of jobs in the order they are run. If the dependencies contain a cycle, so that the jobs cannot all be run, return <code>["CYCLE"]</code>. Spaces around names must be ignored, and a dependency can be listed twice.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(jobs):
    # write your code here
    return []
"""
SOLUTION = """
import heapq


def solution(jobs):
    deps, users = {}, {}
    for line in jobs:
        name, _, rest = line.partition(":")
        name = name.strip()
        deps.setdefault(name, set())
        for d in rest.split(","):
            d = d.strip()
            if d:
                deps[name].add(d)
                deps.setdefault(d, set())
    for job, ds in deps.items():
        for d in ds:
            users.setdefault(d, []).append(job)
    left = {j: len(ds) for j, ds in deps.items()}
    ready = [j for j, n in left.items() if n == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        j = heapq.heappop(ready)
        order.append(j)
        for u in users.get(j, []):
            left[u] -= 1
            if left[u] == 0:
                heapq.heappush(ready, u)
    return order if len(order) == len(deps) else ["CYCLE"]
"""
MUTANTS = [
    """
def solution(jobs):
    deps = {}
    for line in jobs:
        n, _, rest = line.partition(":")
        deps[n.strip()] = [d.strip() for d in rest.split(",") if d.strip()]
    order, done = [], set()
    while len(done) < len(deps):
        ready = sorted(j for j in deps if j not in done and all(d in done for d in deps[j]))
        if not ready: return ["CYCLE"]
        order.append(ready[0]); done.add(ready[0])
    return order
""",
    """
def solution(jobs):
    deps = {}
    for line in jobs:
        n, _, rest = line.partition(":")
        deps.setdefault(n.strip(), [])
        for d in rest.split(","):
            if d.strip():
                deps[n.strip()].append(d.strip()); deps.setdefault(d.strip(), [])
    order, done = [], set()
    while len(done) < len(deps):
        ready = sorted(j for j in deps if j not in done and all(d in done for d in deps[j]))
        if not ready: return ["CYCLE"]
        order.extend(ready); done.update(ready)
    return order
""",
]


def tests():
    t = [{"jobs": ["report: clean, load", "clean: extract", "load: extract", "extract:", "audit: report"]},
         {"jobs": ["b: a", "a: b", "c:"]},
         {"jobs": ["z: y , x", "y: x, x", "w:"]},
         {"jobs": ["dashboard: kpis", "kpis: orders, users"]}]
    r = rng(804)
    names = ["ingest", "clean", "dedup", "join", "kpis", "report", "export", "audit"]
    for k in range(7):
        order = r.sample(names, r.randint(3, 8))
        lines = []
        for i, j in enumerate(order):
            ds = r.sample(order[:i], r.randint(0, min(i, 3))) if i else []
            if k % 3 == 2 and i == len(order) - 1:
                lines[0] = lines[0] + (", " if lines[0].rstrip().endswith(":") is False else " ") + j
            lines.append(f"{j}: {', '.join(ds)}")
        r.shuffle(lines)
        t.append({"jobs": lines})
    return t
