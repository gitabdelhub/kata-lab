from kit import rng

ID = "h16t4"
NAME = "Late Events and Watermark"
LANG = "python"
PARAMS = ["events", "lateness"]
MINUTES = 30
TAGS = ["watermark", "événements en retard", "dernière version gagne", "fenêtres de 10 minutes", "ordre d'arrivée vs temps de l'événement"]
IO = [("input", "array.string events"), ("input", "integer lateness"), ("output", "array.string")]
DESC = """
<p>A streaming job receives <code>events</code> in <b>arrival order</b>, each as <code>"event_time,key,version,amount"</code> (integers except <code>key</code>). Events can arrive out of order.</p>
<p>The job keeps a <b>watermark</b>: before an event is read, the watermark is the highest <code>event_time</code> of all the events read so far (accepted or not) minus <code>lateness</code>; before the first event there is no watermark. An event whose <code>event_time</code> is <b>strictly lower</b> than the watermark is <b>late</b>: it is dropped and only counted.</p>
<p>A non-late event is applied to the state of its key only if its <code>version</code> is <b>strictly higher</b> than the version already stored for that key (or if the key is new); otherwise it is a <b>stale</b> event, counted and ignored. An applied event replaces the amount of the key and stores its event time.</p>
<p>At the end, the job reports totals per 10-minute window: an applied value belongs to the window that contains the event time of the version kept for its key (<code>window_start = event_time - event_time % 600</code>, times are in seconds).</p>
<p>Your task is to return <code>"window_start:total"</code> for each window that holds at least one key, sorted by <code>window_start</code>, followed by <code>"LATE n"</code> and <code>"STALE n"</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(events, lateness):
    # write your code here
    return []
"""
SOLUTION = """
def solution(events, lateness):
    state = {}          # key -> [version, event_time, amount]
    max_time = None
    late = 0
    stale = 0
    for line in events:
        t, key, version, amount = line.split(",")
        t, version, amount = int(t), int(version), int(amount)
        if max_time is not None and t < max_time - lateness:
            late += 1
        elif key in state and version <= state[key][0]:
            stale += 1
        else:
            state[key] = [version, t, amount]
        # Le watermark avance avec tous les événements lus, même en retard
        if max_time is None or t > max_time:
            max_time = t

    windows = {}
    for key in state:
        version, t, amount = state[key]
        w = t - t % 600
        windows[w] = windows.get(w, 0) + amount

    out = []
    for w in sorted(windows):
        out.append(str(w) + ":" + str(windows[w]))
    out.append("LATE " + str(late))
    out.append("STALE " + str(stale))
    return out
"""
MUTANTS = [
    SOLUTION.replace("        if max_time is not None and t < max_time - lateness:", "        if max_time is not None and t <= max_time - lateness:"),
    SOLUTION.replace("        elif key in state and version <= state[key][0]:", "        elif key in state and version < state[key][0]:"),
    SOLUTION.replace("            state[key] = [version, t, amount]\n        # Le watermark avance avec tous les événements lus, même en retard\n        if max_time is None or t > max_time:\n            max_time = t", "            state[key] = [version, t, amount]\n            if max_time is None or t > max_time:\n                max_time = t"),
    SOLUTION.replace("        w = t - t % 600", "        w = t // 600"),
]


def tests():
    t = [{"events": ["100,a,1,10", "650,b,1,5", "120,a,2,12", "40,c,1,7", "700,a,1,99", "1300,b,3,1", "601,c,2,8", "1250,d,1,4"], "lateness": 600},
         {"events": ["0,k,1,1", "50,k,1,2", "1000,x,1,3", "400,k,2,4", "399,y,5,5"], "lateness": 600},
         {"events": [], "lateness": 10}, {"events": ["0,k,2,1", "700,k,1,5", "50,z,1,3", "100,y,1,2"], "lateness": 600}]
    r = rng(4164)
    for k in range(8):
        ev, base = [], 0
        for i in range(r.randint(5, 60) if k < 7 else 5000):
            base += r.choice([0, 30, 60, 200])
            et = max(0, base - r.choice([0, 0, 0, 100, 300, 599, 600, 601, 1200]))
            ev.append(f"{et},{r.choice('abcdefg')},{r.randint(1, 5)},{r.randint(1, 50)}")
        t.append({"events": ev, "lateness": r.choice([300, 600])})
    return t
