"""Versions simples des corrigés Python : boucles, dict et listes seulement.

Pas de Counter, defaultdict, OrderedDict, lambda, compréhension ni expression génératrice.
Le corrigé de l'exo montre d'abord cette version, puis la version courte en bonus.
tools/build.py vérifie que chaque version simple passe tous les tests (visibles et cachés).
"""

SIMPLE = {}

SIMPLE["p1m8"] = '''
def solution(words, k):
    # 1. Compter chaque mot avec un dict : mot -> nombre
    counts = {}
    for w in words:
        if w in counts:
            counts[w] += 1
        else:
            counts[w] = 1

    # 2. Trier. On range des tuples (-nombre, mot) dans une liste :
    #    Python compare d'abord -nombre (donc le plus fréquent en premier),
    #    puis le mot (ordre alphabétique en cas d'égalité).
    pairs = []
    for w in counts:
        pairs.append((-counts[w], w))
    pairs.sort()

    # 3. Garder les k premiers, au format [mot, nombre]
    result = []
    for i in range(min(k, len(pairs))):
        neg_count, w = pairs[i]
        result.append([w, -neg_count])
    return result
'''

SIMPLE["d12"] = '''
def solution(terms, k):
    # 1. Compter chaque terme
    counts = {}
    for t in terms:
        if t in counts:
            counts[t] += 1
        else:
            counts[t] = 1

    # 2. Trier avec des tuples (-nombre, terme) : le plus fréquent d'abord,
    #    puis l'ordre alphabétique en cas d'égalité
    pairs = []
    for t in counts:
        pairs.append((-counts[t], t))
    pairs.sort()

    # 3. Garder les k premiers termes
    result = []
    for i in range(min(k, len(pairs))):
        result.append(pairs[i][1])
    return result
'''

SIMPLE["d13"] = '''
def solution(columns):
    cols = sorted(columns)
    out = []

    # Backtracking : pour chaque colonne, on la prend, puis on ne la prend pas
    def go(i, cur):
        if i == len(cols):
            out.append(list(cur))      # copie du sous-ensemble courant
            return
        cur.append(cols[i])
        go(i + 1, cur)                 # avec cols[i]
        cur.pop()
        go(i + 1, cur)                 # sans cols[i]

    go(0, [])

    # Trier par taille, puis par ordre alphabétique : tuples (taille, sous-ensemble)
    keyed = []
    for s in out:
        keyed.append((len(s), s))
    keyed.sort()
    result = []
    for size, s in keyed:
        result.append(s)
    return result
'''

SIMPLE["bp03"] = '''
def solution(lines):
    # Largeur = longueur de la plus longue ligne
    width = 0
    for line in lines:
        if len(line) > width:
            width = len(line)

    out = []
    for k in range(width):
        # Dernière ligne qui a encore un caractère en colonne k
        last = 0
        for i in range(len(lines)):
            if len(lines[i]) > k:
                last = i
        # On lit la colonne k de haut en bas ; un espace si la ligne est trop courte
        col = ""
        for i in range(last + 1):
            if len(lines[i]) > k:
                col += lines[i][k]
            else:
                col += " "
        out.append(col)
    return out
'''

SIMPLE["bp04"] = '''
def solution(plaintext):
    # 1. Garder lettres et chiffres, en minuscules
    s = ""
    for ch in plaintext:
        if ch.isalnum():
            s += ch.lower()
    n = len(s)
    if n == 0:
        return ""

    # 2. Plus petit c tel que c * c >= n, puis r = c - 1 si ça suffit
    c = 1
    while c * c < n:
        c += 1
    if c * (c - 1) >= n:
        r = c - 1
    else:
        r = c

    # 3. Compléter avec des espaces pour remplir le rectangle r x c
    while len(s) < r * c:
        s += " "

    # 4. Lire colonne par colonne : la colonne j contient s[j], s[j + c], s[j + 2c]...
    chunks = []
    for j in range(c):
        part = ""
        for i in range(r):
            part += s[i * c + j]
        chunks.append(part)
    return " ".join(chunks)
'''

SIMPLE["bp07"] = '''
def solution(rows):
    # stats[équipe] = [joués, gagnés, nuls, perdus]
    stats = {}

    def add(team, w, d, l):
        if team not in stats:
            stats[team] = [0, 0, 0, 0]
        s = stats[team]
        s[0] += 1
        s[1] += w
        s[2] += d
        s[3] += l

    for row in rows:
        a, b, res = row.split(";")
        if res == "win":
            add(a, 1, 0, 0)
            add(b, 0, 0, 1)
        elif res == "loss":
            add(a, 0, 0, 1)
            add(b, 1, 0, 0)
        else:
            add(a, 0, 1, 0)
            add(b, 0, 1, 0)

    # Trier : tuples (-points, équipe) -> plus de points d'abord, puis ordre alphabétique
    order = []
    for team in stats:
        w = stats[team][1]
        d = stats[team][2]
        order.append((-(3 * w + d), team))
    order.sort()

    fmt = "{:<31}| {:>2} | {:>2} | {:>2} | {:>2} | {:>2}"
    out = [fmt.format("Team", "MP", "W", "D", "L", "P")]
    for neg_points, team in order:
        mp, w, d, l = stats[team]
        out.append(fmt.format(team, mp, w, d, l, 3 * w + d))
    return out
'''

SIMPLE["bp09"] = '''
def solution(pattern, flags, files, contents):
    def match(line):
        a = line
        b = pattern
        if "-i" in flags:              # sans tenir compte des majuscules
            a = line.lower()
            b = pattern.lower()
        if "-x" in flags:              # la ligne entière doit être égale
            ok = (a == b)
        else:                          # le motif doit apparaître dans la ligne
            ok = (b in a)
        if "-v" in flags:              # on inverse : on garde ce qui ne matche pas
            ok = not ok
        return ok

    out = []
    for name in files:
        num = 0
        for line in contents[name]:
            num += 1
            if not match(line):
                continue
            if "-l" in flags:          # seulement le nom du fichier, une fois
                out.append(name)
                break
            prefix = ""
            if len(files) > 1:
                prefix += name + ":"
            if "-n" in flags:
                prefix += str(num) + ":"
            out.append(prefix + line)
    return out
'''

SIMPLE["bp10"] = '''
def solution(message, rails, action):
    n = len(message)
    cycle = 2 * (rails - 1)          # on descend puis on remonte

    # 1. Sur quel rail tombe chaque position ?
    line = []
    for i in range(n):
        p = i % cycle
        if p <= rails - 1:
            line.append(p)           # on descend
        else:
            line.append(cycle - p)   # on remonte

    # 2. Ordre de lecture : rail 0 de gauche à droite, puis rail 1, etc.
    order = []
    for r in range(rails):
        for i in range(n):
            if line[i] == r:
                order.append(i)

    if action == "encode":
        result = ""
        for i in order:
            result += message[i]
        return result

    # Décoder : la k-ième lettre du message va à la position order[k]
    out = [""] * n
    for k in range(n):
        out[order[k]] = message[k]
    return "".join(out)
'''

SIMPLE["e04t4"] = '''
def to_minutes(hhmm):
    return int(hhmm[:2]) * 60 + int(hhmm[3:])


def solution(shifts):
    # 1. Regrouper les créneaux par livreur : id -> liste de (début, fin) en minutes
    by = {}
    for s in shifts:
        cid, span = s.split()
        a, b = span.split("-")
        start = to_minutes(a)
        end = to_minutes(b)
        if end <= start:              # passe minuit
            end += 24 * 60
        if cid not in by:
            by[cid] = []
        by[cid].append((start, end))

    # 2. Pour chaque livreur : trier, fusionner les créneaux qui se chevauchent, additionner
    order = []
    for cid in by:
        iv = by[cid]
        iv.sort()
        total = 0
        cur_s, cur_e = iv[0]
        for s, e in iv[1:]:
            if s <= cur_e:            # chevauchement : on prolonge
                if e > cur_e:
                    cur_e = e
            else:                     # trou : on ferme le bloc courant
                total += cur_e - cur_s
                cur_s, cur_e = s, e
        total += cur_e - cur_s
        order.append((-total, cid))   # plus d'heures d'abord, puis id

    # 3. Trier et formater HH:MM
    order.sort()
    result = []
    for neg_total, cid in order:
        m = -neg_total
        hh = str(m // 60).zfill(2)
        mm = str(m % 60).zfill(2)
        result.append([cid, hh + ":" + mm])
    return result
'''

SIMPLE["e06t4"] = '''
def solution(capacity, operations):
    cache = {}       # clé -> valeur
    order = []       # clés, de la moins récemment utilisée à la plus récente
    out = []
    for op in operations:
        parts = op.split()
        if parts[0] == "GET":
            k = parts[1]
            if k in cache:
                order.remove(k)        # devient la plus récente
                order.append(k)
                out.append(cache[k])
            else:
                out.append("MISS")
        elif parts[0] == "PUT":
            k = parts[1]
            v = parts[2]
            if capacity == 0:
                continue
            if k in cache:
                order.remove(k)
            elif len(cache) >= capacity:
                old = order.pop(0)     # la moins récente part
                del cache[old]
                out.append("EVICT " + old)
            cache[k] = v
            order.append(k)
        elif parts[0] == "DEL":
            k = parts[1]
            if k in cache:
                del cache[k]
                order.remove(k)
    return out
'''

SIMPLE["e07t4"] = '''
PATTERNS = {
    " _ | ||_|": "0", "     |  |": "1", " _  _||_ ": "2", " _  _| _|": "3", "   |_|  |": "4",
    " _ |_  _|": "5", " _ |_ |_|": "6", " _   |  |": "7", " _ |_||_|": "8", " _ |_| _|": "9",
}


def solution(screen):
    out = []
    # Chaque nombre occupe 3 lignes de l'écran
    for r in range(0, len(screen), 3):
        rows = screen[r:r + 3]
        width = len(rows[0])
        s = ""
        # Chaque chiffre occupe 3 colonnes : on recolle ses 3 morceaux de 3 caractères
        for c in range(0, width, 3):
            key = ""
            for line in rows:
                key += line[c:c + 3]
            if key in PATTERNS:
                s += PATTERNS[key]
            else:
                s += "?"
        if "?" in s:
            s += " ILL"
        out.append(s)
    return out
'''

SIMPLE["e09t4"] = '''
def solution(routes, start, goal):
    if start == goal:
        return [start]

    # Voisins dans les deux sens
    adj = {}     # a -> vols au départ de a
    rev = {}     # b -> aéroports qui arrivent à b
    for a, b in routes:
        if a not in adj:
            adj[a] = []
        adj[a].append(b)
        if b not in rev:
            rev[b] = []
        rev[b].append(a)

    # BFS depuis le but, sur le graphe inversé : dist[x] = nombre de vols de x au but
    dist = {goal: 0}
    queue = [goal]
    head = 0                       # file avec un indice (pas besoin de deque)
    while head < len(queue):
        x = queue[head]
        head += 1
        if x in rev:
            for p in rev[x]:
                if p not in dist:
                    dist[p] = dist[x] + 1
                    queue.append(p)

    if start not in dist:
        return []

    # On avance d'un vol à chaque fois, vers le plus petit voisin (ordre alphabétique)
    # qui rapproche du but
    path = [start]
    while path[-1] != goal:
        cur = path[-1]
        best = None
        for nb in adj[cur]:
            if nb in dist and dist[nb] == dist[cur] - 1:
                if best is None or nb < best:
                    best = nb
        path.append(best)
    return path
'''

SIMPLE["e17t4"] = '''
def solution(requests, limit, window):
    seen = {}        # client -> liste des instants acceptés encore dans la fenêtre
    out = []
    for ts, client in requests:
        t = int(ts)
        if client not in seen:
            seen[client] = []
        q = seen[client]
        # Retirer les requêtes trop anciennes (sorties de la fenêtre)
        while len(q) > 0 and q[0] <= t - window:
            q.pop(0)
        if len(q) < limit:
            q.append(t)
            out.append(True)
        else:
            out.append(False)          # refusée : on ne la compte pas
    return out
'''
