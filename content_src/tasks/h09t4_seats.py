from kit import rng

ID = "h09t4"
NAME = "Group Seat Assignment"
LANG = "python"
PARAMS = ["rows", "requests"]
MINUTES = 30
TAGS = ["règles de préférence", "allée", "annulations", "réservation qui échoue", "ordre de recherche"]
IO = [("input", "integer rows"), ("input", "array.string requests"), ("output", "array.string")]
DESC = """
<p>A plane has <code>rows</code> rows numbered from 1. Each row has six seats: <code>A B C</code>, the aisle, then <code>D E F</code>. Seats are written like <code>12C</code>. All seats are free at the start. Process <code>requests</code> in order:</p>
<ul><li><code>"BOOK id k"</code> (<code>k</code> is 1, 2 or 3): a group of <code>k</code> passengers who must sit side by side on the same side of the aisle in the same row. The group gets the first free option in this order: row 1 first, then row 2, and so on; inside a row, the options are tried in this order:
<ul><li><code>k = 1</code>: <code>A</code>, <code>F</code>, <code>C</code>, <code>D</code>, <code>B</code>, <code>E</code> (window, then aisle, then middle);</li>
<li><code>k = 2</code>: <code>AB</code>, <code>EF</code>, <code>BC</code>, <code>DE</code>;</li>
<li><code>k = 3</code>: <code>ABC</code>, <code>DEF</code>.</li></ul>
Return <code>"id:seats"</code> with the seats joined by <code>","</code> in letter order (for example <code>"7:3E,3F"</code>), or <code>"id:FULL"</code> if no option is free (nothing is booked). A booking id that already has seats is refused with <code>"id:DUPLICATE"</code>.</li>
<li><code>"CANCEL id"</code>: frees all the seats of the booking. Return <code>"id:CANCELLED"</code>, or <code>"id:UNKNOWN"</code> if the id has no seats (never booked, refused or already cancelled). A cancelled id can be booked again later.</li></ul>
<p>Your task is to return one string per request.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(rows, requests):
    # write your code here
    return []
"""
SOLUTION = """
def solution(rows, requests):
    options = {
        1: ["A", "F", "C", "D", "B", "E"],
        2: ["AB", "EF", "BC", "DE"],
        3: ["ABC", "DEF"],
    }
    taken = {}        # siège "12C" -> id de la réservation
    booking = {}      # id -> liste de sièges
    out = []
    for req in requests:
        p = req.split()
        if p[0] == "BOOK":
            bid, k = p[1], int(p[2])
            if bid in booking:
                out.append(bid + ":DUPLICATE")
                continue
            found = None
            for row in range(1, rows + 1):
                for letters in options[k]:
                    seats = []
                    for letter in letters:
                        seats.append(str(row) + letter)
                    free = True
                    for s in seats:
                        if s in taken:
                            free = False
                    if free:
                        found = seats
                        break
                if found is not None:
                    break
            if found is None:
                out.append(bid + ":FULL")
            else:
                for s in found:
                    taken[s] = bid
                booking[bid] = found
                out.append(bid + ":" + ",".join(found))
        else:
            bid = p[1]
            if bid not in booking:
                out.append(bid + ":UNKNOWN")
            else:
                for s in booking[bid]:
                    del taken[s]
                del booking[bid]
                out.append(bid + ":CANCELLED")
    return out
"""
MUTANTS = [
    SOLUTION.replace('1: ["A", "F", "C", "D", "B", "E"]', '1: ["A", "B", "C", "D", "E", "F"]'),
    SOLUTION.replace('2: ["AB", "EF", "BC", "DE"]', '2: ["AB", "BC", "DE", "EF"]'),
    SOLUTION.replace('3: ["ABC", "DEF"]', '3: ["ABC", "BCD", "CDE", "DEF"]'),
    SOLUTION.replace("            if bid in booking:\n                out.append(bid + \":DUPLICATE\")\n                continue\n", ""),
    SOLUTION.replace("                del booking[bid]\n", ""),
]


def tests():
    t = [{"rows": 2, "requests": ["BOOK g1 3", "BOOK g2 2", "BOOK g3 1", "BOOK g4 2", "BOOK g5 3", "CANCEL g1", "BOOK g6 2", "BOOK g2 1",
                                  "CANCEL g9", "BOOK g7 1", "BOOK g8 1", "BOOK g9 3"]},
         {"rows": 1, "requests": ["BOOK a 1", "BOOK b 1", "BOOK c 1", "BOOK d 2", "CANCEL a", "CANCEL a", "BOOK a 2", "BOOK e 1", "BOOK f 1"]}]
    r = rng(4094)
    for _ in range(9):
        reqs, ids = [], []
        for i in range(r.randint(5, 70)):
            if ids and r.random() < 0.25:
                reqs.append(f"CANCEL {r.choice(ids + ['zz'])}")
            else:
                bid = r.choice([f"b{i}", f"b{i}", r.choice(ids) if ids else "b0"])
                ids.append(bid)
                reqs.append(f"BOOK {bid} {r.choice([1, 1, 2, 2, 3])}")
        t.append({"rows": r.randint(1, 6), "requests": reqs})
    return t
