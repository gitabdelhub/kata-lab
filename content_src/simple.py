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

SIMPLE["e03t4"] = '''
def solution(requests, rooms):
    # 1. Ranger les demandes par heure d'arrivée, puis par id
    order = []
    for r in requests:
        order.append((r[1], r[0], r[2]))      # (arrivée, id, durée)
    order.sort()

    # 2. free_at[salle] = heure où la salle se libère (None = jamais utilisée)
    free_at = []
    for room in range(rooms):
        free_at.append(None)

    out = []
    for arrival, pid, duration in order:
        # 3. La plus petite salle libre à l'arrivée
        chosen = -1
        for room in range(rooms):
            if free_at[room] is None or free_at[room] <= arrival:
                chosen = room
                break
        if chosen != -1:
            start = arrival
        else:
            # 4. Aucune : la salle qui se libère le plus tôt (plus petit numéro si égalité)
            chosen = 0
            for room in range(1, rooms):
                if free_at[room] < free_at[chosen]:
                    chosen = room
            start = free_at[chosen]
        free_at[chosen] = start + duration
        out.append([pid, chosen, start, start + duration])
    out.sort()
    return out
'''

SIMPLE["e18t4"] = '''
def solution(meetings, rooms):
    # 1. Ordre de traitement : par heure de début, puis par position d'origine
    order = []
    for i in range(len(meetings)):
        order.append((meetings[i][0], i))
    order.sort()

    # 2. free_at[salle] = heure où la salle se libère (None = jamais utilisée)
    free_at = []
    for room in range(rooms):
        free_at.append(None)

    out = []
    for i in range(len(meetings)):
        out.append(None)

    for start, idx in order:
        end = meetings[idx][1]
        # 3. La plus petite salle libre au début de la réunion
        chosen = -1
        for room in range(rooms):
            if free_at[room] is None or free_at[room] <= start:
                chosen = room
                break
        if chosen != -1:
            free_at[chosen] = end
        else:
            # 4. Aucune : on attend la salle qui se libère le plus tôt, la réunion est décalée
            chosen = 0
            for room in range(1, rooms):
                if free_at[room] < free_at[chosen]:
                    chosen = room
            free_at[chosen] = free_at[chosen] + (end - start)
        out[idx] = chosen
    return out
'''

SIMPLE["e08t4"] = '''
def solution(jobs):
    # 1. deps[job] = ensemble de ses prérequis (chaque job cité existe)
    deps = {}
    for line in jobs:
        name, _, rest = line.partition(":")
        name = name.strip()
        if name not in deps:
            deps[name] = set()
        for d in rest.split(","):
            d = d.strip()
            if d:
                deps[name].add(d)
                if d not in deps:
                    deps[d] = set()

    # 2. users[d] = jobs qui attendent d ; left[job] = prérequis pas encore faits
    users = {}
    left = {}
    for job in deps:
        left[job] = len(deps[job])
        for d in deps[job]:
            if d not in users:
                users[d] = []
            users[d].append(job)

    # 3. Jobs prêts tout de suite
    ready = []
    for job in left:
        if left[job] == 0:
            ready.append(job)

    # 4. Toujours prendre le prêt le plus petit dans l'ordre alphabétique
    order = []
    while ready:
        ready.sort()
        j = ready.pop(0)
        order.append(j)
        if j in users:
            for u in users[j]:
                left[u] -= 1
                if left[u] == 0:
                    ready.append(u)

    # 5. Des jobs jamais prêts = un cycle
    if len(order) == len(deps):
        return order
    return ["CYCLE"]
'''

SIMPLE["e10t4"] = '''
import json


def clean_str(value):
    # Chaîne nettoyée, ou None si absente, null, pas une str, ou vide après strip
    if not isinstance(value, str):
        return None
    value = value.strip()
    if value == "":
        return None
    return value


def ingest_users(fetch_page):
    rows = []
    cursor = None
    while True:
        page = json.loads(fetch_page(cursor))          # le corps est une str JSON
        data = page.get("data")
        if data is None:
            data = []
        for rec in data:
            if rec.get("id") is None:                  # id absent ou null : ignoré (id 0 gardé)
                continue
            profile = rec.get("profile") or {}         # absent ou null : dict vide
            address = rec.get("address") or {}
            geo = address.get("geo") or {}

            email = clean_str(rec.get("email"))
            if email is not None:
                email = email.lower()

            parts = []
            for key in ["first_name", "last_name"]:
                p = clean_str(profile.get(key))
                if p:
                    parts.append(p)
            full_name = None
            if parts:
                full_name = " ".join(parts)

            country = clean_str(address.get("country_code"))
            if country is not None:
                country = country.upper()

            lat = geo.get("lat")
            if lat is not None:
                lat = float(lat)                       # 0.0 reste 0.0
            lng = geo.get("lng")
            if lng is not None:
                lng = float(lng)

            tags = rec.get("tags")
            if tags is None:
                tags = []

            rows.append({
                "user_id": str(rec["id"]),
                "email": email,
                "full_name": full_name,
                "city": address.get("city"),
                "country": country,
                "lat": lat,
                "lng": lng,
                "n_tags": len(tags),
            })
        if not page.get("has_more"):                   # on s'arrête sur has_more, pas sur next_cursor
            break
        cursor = page["next_cursor"]
    return rows
'''

SIMPLE["e12t4"] = '''
import json


def is_int_text(s):
    # "12", "-3" : oui ; "1.5", "", "abc" : non
    s = s.strip()
    if s.startswith("-"):
        s = s[1:]
    return s != "" and s.isdigit()


def convert(field, v):
    # Renvoie (ok, valeur convertie)
    if field == "id":
        if isinstance(v, bool):                 # bool est une sous-classe de int en Python
            return False, None
        if isinstance(v, int):
            return True, v
        if isinstance(v, str) and is_int_text(v):
            return True, int(v.strip())
        return False, None
    if field == "event":
        if isinstance(v, str) and v.strip():
            return True, v.strip()
        return False, None
    # field == "value"
    if v is None:
        return True, None
    if isinstance(v, bool):
        return False, None
    if isinstance(v, int) or isinstance(v, float):
        return True, float(v)
    if isinstance(v, str):
        try:
            return True, float(v.strip())
        except ValueError:
            return False, None
    return False, None


def parse_events(ndjson_text):
    records = []
    errors = []
    line_no = 0
    for line in ndjson_text.split("\\n"):
        line_no += 1                              # numéro de ligne physique
        if not line.strip():
            continue                              # ligne vide : ni record ni erreur
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            errors.append({"line": line_no, "reason": "invalid_json"})
            continue
        if not isinstance(obj, dict):
            errors.append({"line": line_no, "reason": "not_an_object"})
            continue

        missing = None
        for f in ["id", "event"]:
            if obj.get(f) is None:
                missing = f
                break
        if missing:
            errors.append({"line": line_no, "reason": "missing_field:" + missing})
            continue

        out = {}
        bad = None
        for field in ["id", "event", "value"]:
            ok, value = convert(field, obj.get(field))
            if not ok:
                bad = field
                break
            out[field] = value
        if bad:
            errors.append({"line": line_no, "reason": "invalid_field:" + bad})
        else:
            records.append(out)
    return records, errors
'''

SIMPLE["e13t4"] = '''
def load_invoices(fetch_page, page_size, max_pages):
    seen = set()
    totals = {}
    invoice_count = 0
    duplicates_skipped = 0
    pages_fetched = 0
    complete = False

    page = 1
    while page <= max_pages:                      # jamais plus de max_pages appels
        try:
            response = fetch_page(page, page_size)
        except Exception:                         # API en erreur : on garde ce qui est déjà chargé
            complete = False
            break
        pages_fetched += 1
        results = response.get("results")
        if results is None:
            results = []

        for record in results:
            invoice_id = record["invoice_id"]
            if invoice_id in seen:                # recouvrement entre pages
                duplicates_skipped += 1
                continue
            seen.add(invoice_id)
            status = record.get("status")
            if status is None:
                status = ""
            if str(status).strip().lower() == "void":
                continue
            currency = str(record["currency"]).strip().upper()
            if currency not in totals:
                totals[currency] = 0.0
            totals[currency] += float(record["amount"])
            invoice_count += 1

        if len(results) < page_size:              # page vide ou partielle = dernière page
            complete = True
            break
        page += 1

    rounded = {}
    for cur in totals:
        rounded[cur] = round(totals[cur], 2)

    return {
        "pages_fetched": pages_fetched,
        "complete": complete,
        "invoice_count": invoice_count,
        "duplicates_skipped": duplicates_skipped,
        "totals": rounded,
    }
'''

SIMPLE["h12t4"] = '''
def solution(changes, queries):
    # 1. Dernière valeur pour chaque (produit, heure)
    last = {}
    for line in changes:
        product, time, price = line.split(",")
        last[(product, int(time))] = int(price)

    # 2. Pour chaque produit : heures triées et prix dans le même ordre
    keys = list(last.keys())
    keys.sort()
    times = {}
    prices = {}
    for product, time in keys:
        if product not in times:
            times[product] = []
            prices[product] = []
        times[product].append(time)
        prices[product].append(last[(product, time)])

    out = []
    for q in queries:
        p = q.split()
        product = p[1]
        ts = times.get(product, [])
        ps = prices.get(product, [])
        if p[0] == "PRICE":
            t = int(p[2])
            # dernier changement à l'heure t ou avant
            i = -1
            for k in range(len(ts)):
                if ts[k] <= t:
                    i = k
            if i >= 0:
                out.append(str(ps[i]))
            else:
                out.append("-1")
        elif p[0] == "MIN":
            t1 = int(p[2])
            t2 = int(p[3])
            # le prix en vigueur à t1 compte, puis tous les changements jusqu'à t2
            i = -1
            for k in range(len(ts)):
                if ts[k] <= t1:
                    i = k
            if i < 0:
                i = 0
            best = None
            while i < len(ts) and ts[i] <= t2:
                if best is None or ps[i] < best:
                    best = ps[i]
                i += 1
            if best is not None:
                out.append(str(best))
            else:
                out.append("-1")
        else:
            t1 = int(p[2])
            t2 = int(p[3])
            # premier changement à t1 ou après
            i = 0
            while i < len(ts) and ts[i] < t1:
                i += 1
            count = 0
            while i < len(ts) and ts[i] <= t2:
                if i == 0 or ps[i] != ps[i - 1]:
                    count += 1
                i += 1
            out.append(str(count))
    return out
'''
