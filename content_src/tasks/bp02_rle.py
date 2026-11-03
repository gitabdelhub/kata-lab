from kit import exercism, rng, EXERCISM

ID = "bp02"
NAME = "Run-Length Encoding"
LANG = "python"
PARAMS = ["text"]
MINUTES = 12
TAGS = ["parcours de chaîne", "compteur", "dernier groupe"]
SOURCE = EXERCISM + " · run-length-encoding"
IO = [("input", "string text"), ("output", "string")]
SUMMARY_FR = "Compresser une chaîne : chaque suite de caractères identiques devient le nombre de répétitions suivi du caractère, sans écrire 1 quand le caractère est seul."
HINTS = ["Garde le caractère courant et son compteur ; quand le caractère change, écris le groupe et repars à 1.",
         "N'oublie pas d'écrire le dernier groupe après la boucle, et les compteurs à 2 chiffres ou plus."]
DESC = """
<p>A telemetry device compresses its status strings before sending them. You are given a string <code>text</code> made of letters and spaces.</p>
<p>Every maximal run of consecutive identical characters is replaced by the length of the run followed by the character. When a run has length <code>1</code>, the number is omitted. For example <code>"WWWB"</code> becomes <code>"3WB"</code>. Runs can be longer than 9 characters.</p>
<p>Your task is to return the encoded string. The empty string is encoded as the empty string.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(text):
    # write your code here
    return text
"""
SOLUTION = """
def solution(text):
    out = []
    i = 0
    while i < len(text):
        j = i
        while j < len(text) and text[j] == text[i]:
            j += 1
        n = j - i
        out.append((str(n) if n > 1 else "") + text[i])
        i = j
    return "".join(out)
"""
ALT = ["""
from itertools import groupby
def solution(text):
    return "".join((str(len(g)) if len(g) > 1 else "") + k for k, g in ((k, list(g)) for k, g in groupby(text)))
"""]
MUTANTS = [
    """
def solution(text):
    out, prev, n = [], None, 0
    for ch in text:
        if ch == prev:
            n += 1
        else:
            if prev is not None:
                out.append((str(n) if n > 1 else "") + prev)
            prev, n = ch, 1
    return "".join(out)
""",
    """
def solution(text):
    out, prev, n = [], None, 0
    for ch in text + "\\0":
        if ch == prev:
            n += 1
        else:
            if prev is not None:
                out.append(str(n) + prev)
            prev, n = ch, 1
    return "".join(out)
""",
]
CASES = exercism("run-length-encoding", "encode")


def tests():
    t = [{"text": "AABCCCCCCCCCCCCD"}, {"text": "  ok  "}]
    t += [{"text": i["string"]} for i, _ in CASES]
    r = rng(102)
    for _ in range(3):
        t.append({"text": "".join(r.choice("AB ") * r.randint(1, 13) for _ in range(r.randint(2, 6)))})
    return t


def expected():
    return [None, None] + [e for _, e in CASES] + [None] * 3
