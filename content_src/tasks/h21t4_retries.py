from kit import rng

ID = "h21t4"
NAME = "Retry Policy and Dead Letters"
LANG = "python"
PARAMS = ["attempts", "base", "max_failures"]
MINUTES = 30
TAGS = ["machine à états", "backoff exponentiel", "tri stable", "tentatives ignorées", "format de sortie"]
IO = [("input", "array.string attempts"), ("input", "integer base"), ("input", "integer max_failures"), ("output", "array.string")]
DESC = """
<p>A job runner logs every attempt to run a job. <code>attempts</code> is a list of strings <code>"job,time,status"</code> (<code>time</code> is an integer, <code>status</code> is <code>ok</code>, <code>fail</code> or <code>timeout</code>), <b>not sorted</b>. Process the attempts in order of time; attempts with the same time keep their order in the list.</p>
<p>The retry policy of a job is:</p>
<ul><li>A job starts <b>PENDING</b> with 0 failures, and its first attempt is allowed at any time.</li>
<li>A <code>fail</code> or a <code>timeout</code> is a failure. After the <code>n</code>-th failure at time <code>t</code>, the next attempt is allowed only from <code>t + base * 2^(n-1)</code> on (so <code>base</code>, then <code>2 * base</code>, <code>4 * base</code>...).</li>
<li>An attempt made before it is allowed is <b>throttled</b>: it is ignored and does not change anything.</li>
<li>When a job reaches <code>max_failures</code> failures, it becomes <b>DEAD</b>. An <code>ok</code> makes it <b>DONE</b>. Attempts on a DEAD or DONE job are <b>ignored</b>.</li></ul>
<p>The <b>attempt count</b> of a job only counts the attempts that were not throttled or ignored.</p>
<p>Your task is to return one string per job, sorted by job name: <code>"job:DONE:count"</code>, <code>"job:DEAD:count"</code> or <code>"job:PENDING:count:next"</code> where <code>next</code> is the time from which the next attempt is allowed (<code>0</code> if the job has no failure yet). Then add <code>"THROTTLED n"</code> and <code>"IGNORED n"</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(attempts, base, max_failures):
    # write your code here
    return []
"""
SOLUTION = """
def solution(attempts, base, max_failures):
    rows = []
    for i in range(len(attempts)):
        job, time, status = attempts[i].split(",")
        rows.append([int(time), i, job, status])
    rows.sort()                       # par heure, puis position dans la liste

    jobs = {}                         # job -> [état, échecs, tentatives comptées, prochaine heure permise]
    throttled = 0
    ignored = 0
    for time, i, job, status in rows:
        if job not in jobs:
            jobs[job] = ["PENDING", 0, 0, 0]
        j = jobs[job]
        if j[0] != "PENDING":
            ignored += 1
            continue
        if time < j[3]:
            throttled += 1
            continue
        j[2] += 1
        if status == "ok":
            j[0] = "DONE"
        else:
            j[1] += 1
            if j[1] >= max_failures:
                j[0] = "DEAD"
            else:
                j[3] = time + base * 2 ** (j[1] - 1)

    out = []
    for job in sorted(jobs):
        state, failures, count, nxt = jobs[job]
        if state == "PENDING":
            out.append(job + ":PENDING:" + str(count) + ":" + str(nxt))
        else:
            out.append(job + ":" + state + ":" + str(count))
    out.append("THROTTLED " + str(throttled))
    out.append("IGNORED " + str(ignored))
    return out
"""
MUTANTS = [
    SOLUTION.replace("                j[3] = time + base * 2 ** (j[1] - 1)", "                j[3] = time + base * 2 ** j[1]"),
    SOLUTION.replace("        rows.append([int(time), i, job, status])", "        rows.append([time, i, job, status])"),
    SOLUTION.replace("        if time < j[3]:", "        if time <= j[3] and j[1] > 0:"),
    SOLUTION.replace("        j[2] += 1\n        if status == \"ok\":", "        if status == \"ok\":"),
    SOLUTION.replace("            if j[1] >= max_failures:", "            if j[1] > max_failures:"),
]


def tests():
    t = [{"attempts": ["etl,10,fail", "etl,12,ok", "etl,15,timeout", "etl,40,ok", "etl,45,ok", "sync,5,fail", "sync,6,fail", "sync,9,fail",
                       "sync,13,fail", "sync,30,ok", "mail,100,ok"], "base": 5, "max_failures": 3},
         {"attempts": ["b,3,fail", "a,3,ok", "b,3,ok", "b,4,fail", "c,9,timeout"], "base": 1, "max_failures": 5},
         {"attempts": [], "base": 1, "max_failures": 1}]
    r = rng(4214)
    for k in range(8):
        at = []
        for _ in range(r.randint(5, 60) if k < 7 else 6000):
            at.append(f"{r.choice(['etl', 'sync', 'mail', 'job10', 'job9'])},{r.randint(0, 120 if k < 7 else 20000)},{r.choice(['ok', 'fail', 'fail', 'timeout'])}")
        t.append({"attempts": at, "base": r.choice([1, 2, 5, 10]), "max_failures": r.randint(1, 5)})
    return t
