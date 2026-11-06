from kit import rng

ID = "h08t4"
NAME = "Limit Order Book"
LANG = "python"
PARAMS = ["orders"]
MINUTES = 35
TAGS = ["carnet d'ordres", "priorité prix puis temps", "exécutions partielles", "annulations", "tas (heapq) pour la vitesse"]
IO = [("input", "array.string orders"), ("output", "array.string")]
DESC = """
<p>Implement the matching engine of a small marketplace. <code>orders</code> is a list of strings processed in order:</p>
<ul><li><code>"BUY id price qty"</code> and <code>"SELL id price qty"</code>: a new limit order (integers; ids are unique).</li>
<li><code>"CANCEL id"</code>: removes what is left of a resting order. Cancelling an order that is not resting (unknown, fully executed or already cancelled) does nothing.</li></ul>
<p>A new BUY order is matched against the resting SELL orders whose price is <b>lower than or equal to</b> its price: the lowest price first, and among equal prices the oldest order first. Each match is a trade at the price of the <b>resting</b> order, for the largest possible quantity. Matching continues until the new order is fully executed or no resting SELL order is cheap enough; what is left of the new order then rests in the book. A new SELL order works the same way against resting BUY orders whose price is <b>higher than or equal to</b> its price, the highest price first.</p>
<p>Your task is to return the list of trades in the order they happen, each as <code>"buy_id,sell_id,price,qty"</code>, followed by two last strings describing the book at the end: <code>"BID price qty"</code> (the highest resting buy price and the total quantity resting at that price) and <code>"ASK price qty"</code> (the lowest resting sell price and its total quantity). Write <code>"BID none"</code> or <code>"ASK none"</code> when that side is empty.</p>
<p>There can be up to 20 000 orders: an approach that re-sorts the whole book at every order may be too slow.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(orders):
    # write your code here
    return []
"""
SOLUTION = """
import heapq


def solution(orders):
    # Deux tas : les ventes par (prix, arrivée) ; les achats par (-prix, arrivée) pour avoir le prix le plus haut en premier.
    # Une annulation ne retire rien du tas : on met la quantité restante à 0 et on saute l'ordre quand il arrive en tête.
    sells, buys = [], []
    left = {}            # id -> quantité restante (0 = plus dans le carnet)
    side = {}            # id -> "BUY" ou "SELL"
    price_of = {}
    trades = []
    for seq in range(len(orders)):
        p = orders[seq].split()
        if p[0] == "CANCEL":
            oid = int(p[1])
            if oid in left:
                left[oid] = 0
            continue
        oid, price, qty = int(p[1]), int(p[2]), int(p[3])
        side[oid] = p[0]
        price_of[oid] = price
        if p[0] == "BUY":
            book = sells
        else:
            book = buys
        while qty > 0 and len(book) > 0:
            top_key, top_seq, top_id = book[0]
            if left[top_id] == 0:            # ordre annulé ou déjà exécuté
                heapq.heappop(book)
                continue
            top_price = price_of[top_id]
            if p[0] == "BUY" and top_price > price:
                break
            if p[0] == "SELL" and top_price < price:
                break
            q = min(qty, left[top_id])
            if p[0] == "BUY":
                trades.append(str(oid) + "," + str(top_id) + "," + str(top_price) + "," + str(q))
            else:
                trades.append(str(top_id) + "," + str(oid) + "," + str(top_price) + "," + str(q))
            qty -= q
            left[top_id] -= q
        left[oid] = qty
        if qty > 0:
            if p[0] == "BUY":
                heapq.heappush(buys, (-price, seq, oid))
            else:
                heapq.heappush(sells, (price, seq, oid))

    def best(book, name):
        best_price = None
        total = 0
        for key, s, oid in book:
            if left[oid] == 0:
                continue
            pr = price_of[oid]
            if best_price is None or (name == "BID" and pr > best_price) or (name == "ASK" and pr < best_price):
                best_price = pr
                total = 0
            if pr == best_price:
                total += left[oid]
        if best_price is None:
            return name + " none"
        return name + " " + str(best_price) + " " + str(total)

    trades.append(best(buys, "BID"))
    trades.append(best(sells, "ASK"))
    return trades
"""
MUTANTS = [
    SOLUTION.replace("heapq.heappush(buys, (-price, seq, oid))", "heapq.heappush(buys, (price, seq, oid))"),
    SOLUTION.replace("trades.append(str(oid) + \",\" + str(top_id) + \",\" + str(top_price) + \",\" + str(q))", "trades.append(str(oid) + \",\" + str(top_id) + \",\" + str(price) + \",\" + str(q))"),
    SOLUTION.replace("heapq.heappush(sells, (price, seq, oid))", "heapq.heappush(sells, (price, -seq, oid))"),
    SOLUTION.replace("            if left[oid] == 0:\n                continue\n            pr = price_of[oid]", "            pr = price_of[oid]"),
    SOLUTION.replace("            if oid in left:\n                left[oid] = 0", "            if oid in left and side[oid] == \"BUY\":\n                left[oid] = 0"),
]


def tests():
    t = [{"orders": ["SELL 1 101 5", "SELL 2 100 3", "SELL 3 100 4", "BUY 4 100 5", "BUY 5 99 10", "CANCEL 3", "SELL 6 98 12", "BUY 7 105 1",
                     "CANCEL 42"]},
         {"orders": ["BUY 1 50 2", "BUY 2 50 3", "SELL 3 40 4", "CANCEL 2", "CANCEL 2", "SELL 4 50 1"]},
         {"orders": []}, {"orders": ["BUY 1 10 5", "BUY 2 12 1", "SELL 3 20 2", "CANCEL 2", "CANCEL 3", "SELL 4 30 1"]}]
    r = rng(4084)
    for k in range(8):
        ords, ids = [], []
        n = r.randint(5, 50) if k < 6 else 12000
        for i in range(1, n + 1):
            if ids and r.random() < 0.15:
                ords.append(f"CANCEL {r.choice(ids)}")
            else:
                ids.append(i)
                ords.append(f"{r.choice(['BUY', 'SELL'])} {i} {r.randint(95, 105)} {r.randint(1, 10)}")
        t.append({"orders": ords})
    return t
