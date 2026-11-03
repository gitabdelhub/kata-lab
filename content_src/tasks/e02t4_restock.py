from kit import rng

ID = "e02t4"
NAME = "Backorder Simulator"
LANG = "python"
PARAMS = ["events"]
MINUTES = 25
TAGS = ["simulation", "file FIFO", "deque", "parsing"]
IO = [("input", "array.string events"), ("output", "array.array")]
DESC = """
<p>A warehouse wants to replay one day of activity to understand which orders waited for stock. You are given a list of events <code>events</code>, in the order they happened. Each event is a string in one of these formats:</p>
<ul><li><code>"restock &lt;sku&gt; &lt;qty&gt;"</code> - <code>qty</code> units of <code>sku</code> arrive;</li><li><code>"order &lt;order_id&gt; &lt;sku&gt; &lt;qty&gt;"</code> - a customer orders <code>qty</code> units of <code>sku</code>;</li><li><code>"cancel &lt;order_id&gt;"</code> - the customer cancels an order.</li></ul>
<p>The stock of every SKU starts at <code>0</code>. Events are processed one by one, and the event index starts at <code>0</code>:</p>
<ol><li>an order is <b>filled</b> immediately if no earlier order for the same SKU is waiting and the stock is enough; the stock decreases by <code>qty</code>. Otherwise the order <b>waits</b> at the end of the queue of its SKU;</li><li>after a restock, the queue of that SKU is served in order: while the first waiting order can be filled, it is filled (at the index of the restock event) and removed from the queue. An order that cannot be filled blocks the orders behind it;</li><li>a cancel removes a waiting order from its queue, and it becomes <b>cancelled</b> at the index of the cancel event. After a cancel, the queue of that SKU is served again as in rule 2, at the same index. Cancelling an order that is already filled or cancelled, or that does not exist, does nothing.</li></ol>
<p>Return one entry per order, in the order the orders appear in <code>events</code>: <code>[order_id, status, index]</code>, where <code>status</code> is <code>"filled"</code>, <code>"cancelled"</code> or <code>"waiting"</code> (still waiting at the end of the day), and <code>index</code> is the index of the event that filled or cancelled it, or <code>-1</code> if it is still waiting.</p>
<h4>Example</h4>{{EXAMPLE}}
<p><code>o2</code> waits because only 1 unit of <code>A</code> is left. <code>o3</code> waits behind <code>o2</code> even if 1 unit would be enough. The restock at index 4 fills <code>o2</code> and then <code>o3</code>.</p>
"""
STARTER = """
def solution(events):
    # write your code here
    return []
"""
SOLUTION = """
from collections import deque


def solution(events):
    stock = {}
    queues = {}
    orders = {}
    order_list = []

    def serve(sku, idx):
        q = queues.setdefault(sku, deque())
        while q and stock.get(sku, 0) >= orders[q[0]]["qty"]:
            oid = q.popleft()
            stock[sku] -= orders[oid]["qty"]
            orders[oid].update(status="filled", index=idx)

    for i, ev in enumerate(events):
        parts = ev.split()
        if parts[0] == "restock":
            sku, qty = parts[1], int(parts[2])
            stock[sku] = stock.get(sku, 0) + qty
            serve(sku, i)
        elif parts[0] == "order":
            oid, sku, qty = parts[1], parts[2], int(parts[3])
            orders[oid] = {"sku": sku, "qty": qty, "status": "waiting", "index": -1}
            order_list.append(oid)
            q = queues.setdefault(sku, deque())
            if not q and stock.get(sku, 0) >= qty:
                stock[sku] -= qty
                orders[oid].update(status="filled", index=i)
            else:
                q.append(oid)
        elif parts[0] == "cancel":
            oid = parts[1]
            o = orders.get(oid)
            if o and o["status"] == "waiting":
                queues[o["sku"]].remove(oid)
                o.update(status="cancelled", index=i)
                serve(o["sku"], i)
    return [[oid, orders[oid]["status"], orders[oid]["index"]] for oid in order_list]
"""
MUTANTS = [
    """
def solution(events):
    stock, waiting, orders, order_list = {}, [], {}, []
    for i, ev in enumerate(events):
        p = ev.split()
        if p[0] == "restock":
            stock[p[1]] = stock.get(p[1], 0) + int(p[2])
            for oid in list(waiting):
                o = orders[oid]
                if o["sku"] == p[1] and stock[p[1]] >= o["qty"]:
                    stock[p[1]] -= o["qty"]; o.update(status="filled", index=i); waiting.remove(oid)
        elif p[0] == "order":
            orders[p[1]] = {"sku": p[2], "qty": int(p[3]), "status": "waiting", "index": -1}; order_list.append(p[1])
            if stock.get(p[2], 0) >= int(p[3]):
                stock[p[2]] -= int(p[3]); orders[p[1]].update(status="filled", index=i)
            else:
                waiting.append(p[1])
        else:
            o = orders.get(p[1])
            if o and o["status"] == "waiting":
                waiting.remove(p[1]); o.update(status="cancelled", index=i)
    return [[k, orders[k]["status"], orders[k]["index"]] for k in order_list]
""",
    """
from collections import deque
def solution(events):
    stock, queues, orders, order_list = {}, {}, {}, []
    def serve(sku, idx):
        q = queues.setdefault(sku, deque())
        while q and stock.get(sku, 0) >= orders[q[0]]["qty"]:
            oid = q.popleft(); stock[sku] -= orders[oid]["qty"]; orders[oid].update(status="filled", index=idx)
    for i, ev in enumerate(events):
        p = ev.split()
        if p[0] == "restock":
            stock[p[1]] = stock.get(p[1], 0) + int(p[2]); serve(p[1], i)
        elif p[0] == "order":
            orders[p[1]] = {"sku": p[2], "qty": int(p[3]), "status": "waiting", "index": -1}; order_list.append(p[1])
            q = queues.setdefault(p[2], deque())
            if not q and stock.get(p[2], 0) >= int(p[3]):
                stock[p[2]] -= int(p[3]); orders[p[1]].update(status="filled", index=i)
            else:
                q.append(p[1])
        else:
            o = orders.get(p[1])
            if o and o["status"] == "waiting":
                queues[o["sku"]].remove(p[1]); o.update(status="cancelled", index=i)
    return [[k, orders[k]["status"], orders[k]["index"]] for k in order_list]
""",
]


def tests():
    t = [{"events": ["restock A 5", "order o1 A 4", "order o2 A 3", "order o3 A 1", "restock A 4", "order o4 B 1"]},
         {"events": ["restock A 1", "order x A 5", "order y A 1", "cancel x", "cancel x", "cancel zz"]},
         {"events": ["restock A 2", "order a A 5", "order b A 2", "order c B 1", "cancel a", "restock B 1"]}]
    r = rng(43)
    t.append({"events": []})
    for k in range(8):
        ev, n = [], 0
        for _ in range(8 + 3 * k):
            c = r.random()
            if c < 0.4:
                n += 1
                ev.append(f"order o{n} {r.choice('ABC')} {r.randint(1, 6)}")
            elif c < 0.8:
                ev.append(f"restock {r.choice('ABC')} {r.randint(1, 8)}")
            else:
                ev.append(f"cancel o{r.randint(1, max(1, n + 1))}")
        t.append({"events": ev})
    return t
