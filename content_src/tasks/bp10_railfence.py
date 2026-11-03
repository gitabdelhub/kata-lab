from kit import exercism, rng, EXERCISM

ID = "bp10"
NAME = "Zigzag Rails"
LANG = "python"
PARAMS = ["message", "rails", "action"]
MINUTES = 20
TAGS = ["grille en zigzag", "indices", "encoder et décoder"]
SOURCE = EXERCISM + " · rail-fence-cipher"
IO = [("input", "string message"), ("input", "integer rails"), ("input", "string action"), ("output", "string")]
SUMMARY_FR = "Écrire le message en zigzag sur plusieurs lignes (rails), puis lire ligne par ligne pour encoder. Pour décoder, faire l'inverse."
HINTS = ["Calcule d'abord la ligne de chaque position : 0, 1, ..., rails-1, rails-2, ..., 1, 0, 1, ...",
         "Pour décoder : trie les positions par (ligne, position) ; la k-ième lettre du message codé va à la k-ième position de cet ordre."]
DESC = """
<p>A message is written in a <b>zigzag</b> on <code>rails</code> lines: the first character on line 1, the next one on line 2, and so on down to the last line, then back up to line 1, then down again. For example, with 3 rails, <code>"WEAREDISCOVERED"</code> is written as:</p>
<pre class="exv">W . . . E . . . C . . . R . .
. E . R . D . S . O . E . E .
. . A . . . I . . . V . . . D</pre>
<p>The <b>encoded</b> message is the characters read line by line, from left to right: <code>"WECRERDSOEEAIVD"</code>.</p>
<p>You are given a string <code>message</code>, the number of lines <code>rails</code> (at least 2) and <code>action</code>, which is <code>"encode"</code> or <code>"decode"</code>. Your task is to return the encoded message, or, if <code>action</code> is <code>"decode"</code>, the original message that gives <code>message</code> when it is encoded. All characters, including spaces and punctuation, are kept.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(message, rails, action):
    # write your code here
    return message
"""
SOLUTION = """
def solution(message, rails, action):
    n = len(message)
    cycle = 2 * (rails - 1)
    line = [min(i % cycle, cycle - i % cycle) for i in range(n)]
    order = sorted(range(n), key=lambda i: (line[i], i))
    if action == "encode":
        return "".join(message[i] for i in order)
    out = [""] * n
    for k, i in enumerate(order):
        out[i] = message[k]
    return "".join(out)
"""
ALT = ["""
def solution(message, rails, action):
    def lines(n):
        r, step, res = 0, 1, []
        for _ in range(n):
            res.append(r)
            if r == 0: step = 1
            elif r == rails - 1: step = -1
            r += step
        return res
    ln = lines(len(message))
    if action == "encode":
        return "".join("".join(ch for ch, l in zip(message, ln) if l == k) for k in range(rails))
    counts = [ln.count(k) for k in range(rails)]
    parts, pos = [], 0
    for c in counts:
        parts.append(list(message[pos:pos + c])); pos += c
    return "".join(parts[l].pop(0) for l in ln)
"""]
MUTANTS = [
    """
def solution(message, rails, action):
    order = sorted(range(len(message)), key=lambda i: (i % rails, i))
    if action == "encode":
        return "".join(message[i] for i in order)
    out = [""] * len(message)
    for k, i in enumerate(order):
        out[i] = message[k]
    return "".join(out)
""",
    """
def solution(message, rails, action):
    n = len(message)
    cycle = 2 * (rails - 1)
    line = [min(i % cycle, cycle - i % cycle) for i in range(n)]
    order = sorted(range(n), key=lambda i: (line[i], i))
    return "".join(message[i] for i in order)
""",
]
ENC = exercism("rail-fence-cipher", "encode")
DEC = exercism("rail-fence-cipher", "decode")


def tests():
    t = [{"message": "SEND 40 UNITS", "rails": 3, "action": "encode"}, {"message": "S USED4 NTN0I", "rails": 3, "action": "decode"}]
    t += [{"message": i["msg"], "rails": i["rails"], "action": "encode"} for i, _ in ENC]
    t += [{"message": i["msg"], "rails": i["rails"], "action": "decode"} for i, _ in DEC]
    r = rng(110)
    for _ in range(4):
        t.append({"message": "".join(r.choice("ABCD 12") for _ in range(r.randint(1, 20))), "rails": r.randint(2, 5), "action": r.choice(["encode", "decode"])})
    return t


def expected():
    return [None, None] + [e for _, e in ENC] + [e for _, e in DEC] + [None] * 4
