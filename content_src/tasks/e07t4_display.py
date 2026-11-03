from kit import rng

ID = "e07t4"
NAME = "Meter Display Reader"
LANG = "python"
PARAMS = ["screen"]
MINUTES = 22
TAGS = ["grille 3x3", "découper en blocs", "dictionnaire de motifs", "consigne longue"]
IO = [("input", "array.string screen"), ("output", "array.string")]
DIGITS = {
    "0": [" _ ", "| |", "|_|"], "1": ["   ", "  |", "  |"], "2": [" _ ", " _|", "|_ "], "3": [" _ ", " _|", " _|"], "4": ["   ", "|_|", "  |"],
    "5": [" _ ", "|_ ", " _|"], "6": [" _ ", "|_ ", "|_|"], "7": [" _ ", "  |", "  |"], "8": [" _ ", "|_|", "|_|"], "9": [" _ ", "|_|", " _|"],
}
DESC = """
<p>Old electricity meters show their value on a seven-segment display. A camera takes a picture of the display and turns it into text. You are given <code>screen</code>, a list of strings: every group of <b>3 lines</b> is one row of the display, and inside a row every group of <b>3 characters</b> is one digit, drawn with <code>_</code>, <code>|</code> and spaces:</p>
<pre class="exv"> _     _  _     _  _  _  _  _ 
| |  | _| _||_||_ |_   ||_||_|
|_|  ||_  _|  | _||_|  ||_| _|</pre>
<p>These are the digits <code>0</code> to <code>9</code>. All lines have the same length, which is a multiple of 3, and the number of lines is a multiple of 3.</p>
<p>Your task is to return one string per row of the display: the digits of the row, from left to right. A group of 3x3 characters that is not one of the ten digits is written <code>"?"</code>. If a row contains at least one <code>"?"</code>, add <code>" ILL"</code> at the end of its string.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(screen):
    # write your code here
    return []
"""
SOLUTION = """
PATTERNS = {
    " _ | ||_|": "0", "     |  |": "1", " _  _||_ ": "2", " _  _| _|": "3", "   |_|  |": "4",
    " _ |_  _|": "5", " _ |_ |_|": "6", " _   |  |": "7", " _ |_||_|": "8", " _ |_| _|": "9",
}


def solution(screen):
    out = []
    for r in range(0, len(screen), 3):
        rows = screen[r:r + 3]
        width = len(rows[0])
        s = ""
        for c in range(0, width, 3):
            key = "".join(line[c:c + 3] for line in rows)
            s += PATTERNS.get(key, "?")
        out.append(s + (" ILL" if "?" in s else ""))
    return out
"""
MUTANTS = [
    """
P = {" _ | ||_|": "0", "     |  |": "1", " _  _||_ ": "2", " _  _| _|": "3", "   |_|  |": "4", " _ |_  _|": "5", " _ |_ |_|": "6", " _   |  |": "7", " _ |_||_|": "8", " _ |_| _|": "9"}
def solution(screen):
    out = []
    for r in range(0, len(screen), 3):
        rows = screen[r:r + 3]
        s = "".join(P.get("".join(l[c:c + 3] for l in rows), "?") for c in range(0, len(rows[0]), 3))
        out.append(s)
    return out
""",
    """
P = {" _ | ||_|": "0", "     |  |": "1", " _  _||_ ": "2", " _  _| _|": "3", "   |_|  |": "4", " _ |_  _|": "5", " _ |_ |_|": "6", " _   |  |": "7", " _ |_||_|": "8", " _ |_| _|": "9"}
def solution(screen):
    rows = screen[0:3]
    s = "".join(P.get("".join(l[c:c + 3] for l in rows), "?") for c in range(0, len(rows[0]), 3))
    return [s + (" ILL" if "?" in s else "")]
""",
    """
P = {" _ | ||_|": "0", "     |  |": "1", " _  _||_ ": "2", " _  _| _|": "3", "   |_|  |": "4", " _ |_  _|": "5", " _ |_ |_|": "6", " _   |  |": "7", " _ |_||_|": "8", " _ |_| _|": "9"}
def solution(screen):
    out = []
    for r in range(0, len(screen), 3):
        rows = screen[r:r + 3]
        s = "".join(P.get("".join(l[c:c + 3] for l in rows).strip(), "?") for c in range(0, len(rows[0]), 3))
        out.append(s + (" ILL" if "?" in s else ""))
    return out
""",
]


def draw(rows):
    lines = []
    for row in rows:
        for k in range(3):
            lines.append("".join(DIGITS[d][k] if d in DIGITS else ["_|_", " | ", "|_ "][k] for d in row))
    return lines


def tests():
    t = [{"screen": draw(["0123456789"])}, {"screen": draw(["42", "4x"])}, {"screen": draw(["1", "7", "11"[:1]])}, {"screen": draw(["000", "808"])}]
    r = rng(704)
    for _ in range(7):
        rows = ["".join(r.choice("0123456789" * 3 + "x") for _ in range(r.randint(1, 6)))]
        rows *= 1
        w = len(rows[0])
        rows += ["".join(r.choice("0123456789x") for _ in range(w)) for _ in range(r.randint(0, 2))]
        t.append({"screen": draw(rows)})
    return t
