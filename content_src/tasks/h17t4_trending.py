from kit import rng

ID = "h17t4"
NAME = "Trending Videos"
LANG = "python"
PARAMS = ["stream", "window"]
MINUTES = 30
TAGS = ["fenêtre glissante", "file (deque) + compteurs", "classement avec égalités", "beaucoup d'événements"]
IO = [("input", "array.string stream"), ("input", "integer window"), ("output", "array.string")]
DESC = """
<p>A streaming platform shows the trending videos. <code>stream</code> is a list of strings sorted by time (an integer number of seconds; several lines can share the same time):</p>
<ul><li><code>"t VIEW user video"</code>: a user watched a video at time <code>t</code>.</li>
<li><code>"t TOP k"</code>: asks for the top <code>k</code> videos at time <code>t</code>.</li></ul>
<p>The score of a video at time <code>t</code> is the number of <b>different users</b> who watched it with a view time in <code>(t - window, t]</code> (a user who watches the same video several times in the window counts once). Views that appear <b>after</b> the query in the list are not counted, even with the same time.</p>
<p>For each <code>TOP</code> query, return the videos with a score of at least 1, by score (highest first), then video name, keeping at most <code>k</code> of them, as <code>"video:score"</code> items joined with <code>","</code>; return <code>""</code> if there is none.</p>
<p>The stream can contain up to 30 000 lines: recounting all the views of the window at every query is too slow when the window is long.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(stream, window):
    # write your code here
    return []
"""
SOLUTION = """
from collections import deque


def solution(stream, window):
    views = deque()          # vues dans la fenêtre : (temps, user, vidéo), de la plus ancienne à la plus récente
    pair_count = {}          # (user, vidéo) -> nombre de vues de ce user sur cette vidéo dans la fenêtre
    score = {}               # vidéo -> nombre de users différents dans la fenêtre
    out = []
    for line in stream:
        p = line.split()
        t = int(p[0])
        # Retirer les vues sorties de la fenêtre (temps <= t - window)
        while len(views) > 0 and views[0][0] <= t - window:
            old_t, user, video = views.popleft()
            pair_count[(user, video)] -= 1
            if pair_count[(user, video)] == 0:
                del pair_count[(user, video)]
                score[video] -= 1
                if score[video] == 0:
                    del score[video]
        if p[1] == "VIEW":
            user, video = p[2], p[3]
            views.append((t, user, video))
            if (user, video) not in pair_count:
                pair_count[(user, video)] = 0
                score[video] = score.get(video, 0) + 1
            pair_count[(user, video)] += 1
        else:
            k = int(p[2])
            ranking = []
            for video in score:
                ranking.append((-score[video], video))
            ranking.sort()
            items = []
            for neg, video in ranking[:k]:
                items.append(video + ":" + str(-neg))
            out.append(",".join(items))
    return out
"""
MUTANTS = [
    SOLUTION.replace("        while len(views) > 0 and views[0][0] <= t - window:", "        while len(views) > 0 and views[0][0] < t - window:"),
    SOLUTION.replace("            if (user, video) not in pair_count:\n                pair_count[(user, video)] = 0\n                score[video] = score.get(video, 0) + 1\n            pair_count[(user, video)] += 1",
                     "            pair_count[(user, video)] = pair_count.get((user, video), 0) + 1\n            score[video] = score.get(video, 0) + 1"),
    SOLUTION.replace("            ranking.sort()", "            ranking.sort(key=lambda x: x[0])"),
]


def tests():
    t = [{"stream": ["0 VIEW u1 cats", "5 VIEW u2 cats", "5 VIEW u1 cats", "6 VIEW u3 dogs", "6 TOP 2", "6 VIEW u4 dogs", "10 TOP 5", "15 TOP 1",
                     "16 VIEW u9 ants", "16 TOP 3", "40 TOP 3"], "window": 10},
         {"stream": ["1 VIEW a x", "1 VIEW b y", "1 TOP 1", "2 VIEW a x", "11 TOP 2", "12 TOP 2"], "window": 10}]
    r = rng(4174)
    for k in range(9):
        st, tt = [], 0
        for _ in range(r.randint(5, 60) if k < 8 else 30000):
            tt += r.choice([0, 0, 1, 2, 5])
            if r.random() < 0.2:
                st.append(f"{tt} TOP {r.randint(1, 4)}")
            else:
                st.append(f"{tt} VIEW u{r.randint(1, 6)} {r.choice(['cats', 'dogs', 'ants', 'bees', 'cars'])}")
        t.append({"stream": st, "window": r.choice([5, 10, 30]) if k < 8 else 20000})
    return t
