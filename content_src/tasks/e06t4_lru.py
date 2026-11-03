from kit import rng

ID = "e06t4"
NAME = "Cache Simulator"
LANG = "python"
PARAMS = ["capacity", "operations"]
MINUTES = 22
TAGS = ["LRU", "OrderedDict", "simulation", "lecture de consigne"]
IO = [("input", "integer capacity"), ("input", "array.string operations"), ("output", "array.string")]
DESC = """
<p>An API gateway keeps a small cache of responses. The cache holds at most <code>capacity</code> keys and uses the <b>least recently used</b> policy. You are given a list of <code>operations</code>, each one a string:</p>
<ul><li><code>"GET key"</code>: if the key is in the cache, output its value and mark the key as the most recently used; otherwise output <code>"MISS"</code>;</li><li><code>"PUT key value"</code>: store the value for the key and mark it as the most recently used. If the key was not in the cache and the cache is full, first remove the least recently used key and output <code>"EVICT key"</code> with the removed key. Updating a key that is already in the cache never evicts anything;</li><li><code>"DEL key"</code>: remove the key if it is in the cache (nothing is output).</li></ul>
<p>Keys and values never contain spaces. Your task is to return the list of outputs, in order. If <code>capacity</code> is <code>0</code>, nothing is ever stored and nothing is evicted.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(capacity, operations):
    # write your code here
    return []
"""
SOLUTION = """
from collections import OrderedDict


def solution(capacity, operations):
    cache = OrderedDict()
    out = []
    for op in operations:
        parts = op.split()
        if parts[0] == "GET":
            k = parts[1]
            if k in cache:
                cache.move_to_end(k)
                out.append(cache[k])
            else:
                out.append("MISS")
        elif parts[0] == "PUT":
            k, v = parts[1], parts[2]
            if capacity == 0:
                continue
            if k in cache:
                cache.move_to_end(k)
            elif len(cache) >= capacity:
                old, _ = cache.popitem(last=False)
                out.append("EVICT " + old)
            cache[k] = v
        elif parts[0] == "DEL":
            cache.pop(parts[1], None)
    return out
"""
MUTANTS = [
    """
def solution(capacity, operations):
    cache, order, out = {}, [], []
    for op in operations:
        p = op.split()
        if p[0] == "GET":
            out.append(cache.get(p[1], "MISS"))
        elif p[0] == "PUT":
            if capacity == 0: continue
            if p[1] not in cache:
                if len(cache) >= capacity:
                    old = order.pop(0); del cache[old]; out.append("EVICT " + old)
                order.append(p[1])
            cache[p[1]] = p[2]
        elif p[0] == "DEL" and p[1] in cache:
            del cache[p[1]]; order.remove(p[1])
    return out
""",
    """
from collections import OrderedDict
def solution(capacity, operations):
    cache, out = OrderedDict(), []
    for op in operations:
        p = op.split()
        if p[0] == "GET":
            if p[1] in cache: cache.move_to_end(p[1]); out.append(cache[p[1]])
            else: out.append("MISS")
        elif p[0] == "PUT":
            if capacity == 0: continue
            if len(cache) >= capacity and p[1] not in cache:
                old, _ = cache.popitem(last=False); out.append("EVICT " + old)
            cache[p[1]] = p[2]
        elif p[0] == "DEL":
            cache.pop(p[1], None)
    return out
""",
    """
from collections import OrderedDict
def solution(capacity, operations):
    cache, out = OrderedDict(), []
    for op in operations:
        p = op.split()
        if p[0] == "GET":
            if p[1] in cache: cache.move_to_end(p[1]); out.append(cache[p[1]])
            else: out.append("MISS")
        elif p[0] == "PUT":
            if capacity == 0: continue
            if p[1] in cache: cache.move_to_end(p[1])
            if len(cache) >= capacity:
                old, _ = cache.popitem(last=False); out.append("EVICT " + old)
            cache[p[1]] = p[2]
        elif p[0] == "DEL":
            cache.pop(p[1], None)
    return out
""",
]


def tests():
    t = [{"capacity": 2, "operations": ["PUT a 1", "PUT b 2", "GET a", "PUT c 3", "GET b", "GET c", "PUT a 9", "GET a"]},
         {"capacity": 1, "operations": ["GET x", "PUT x 1", "PUT x 2", "GET x", "DEL x", "PUT y 5", "PUT z 6", "GET y"]},
         {"capacity": 0, "operations": ["PUT a 1", "GET a"]},
         {"capacity": 3, "operations": ["PUT a 1", "PUT b 2", "PUT c 3", "DEL b", "PUT d 4", "PUT e 5", "GET a", "GET c"]}]
    r = rng(604)
    for _ in range(7):
        ops = []
        for _ in range(r.randint(5, 30)):
            k = r.choice("abcdef")
            ops.append(r.choice([f"GET {k}", f"PUT {k} {r.randint(1, 99)}", f"PUT {k} {r.randint(1, 99)}", f"DEL {k}"]))
        t.append({"capacity": r.randint(1, 4), "operations": ops})
    return t
