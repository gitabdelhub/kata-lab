from kit import exercism, rng, EXERCISM

ID = "bp01"
NAME = "Balanced Brackets"
LANG = "python"
PARAMS = ["text"]
MINUTES = 12
TAGS = ["pile (stack)", "dict", "cas limites"]
SOURCE = EXERCISM + " · matching-brackets"
IO = [("input", "string text"), ("output", "boolean")]
SUMMARY_FR = "Dire si les crochets [], accolades {} et parenthèses () du texte sont bien appariés et bien imbriqués. Les autres caractères sont ignorés."
HINTS = ["Une pile : on empile chaque ouvrant, et chaque fermant doit correspondre au sommet de la pile.",
         "À la fin, la pile doit être vide (sinon un ouvrant n'a jamais été fermé)."]
DESC = """
<p>A configuration parser must check the brackets of an expression before evaluating it. You are given a string <code>text</code> that can contain any characters.</p>
<p>The brackets are <code>[]</code>, <code>{}</code> and <code>()</code>. All other characters are ignored. The brackets are <b>balanced</b> if every opening bracket is closed by a bracket of the same type, in the correct order: a bracket opened inside another one must be closed before it.</p>
<p>Your task is to return <code>true</code> if the brackets of <code>text</code> are balanced, and <code>false</code> otherwise. A string with no brackets is balanced.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(text):
    # write your code here
    return True
"""
SOLUTION = """
def solution(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
"""
ALT = ["""
def solution(text):
    s = "".join(c for c in text if c in "()[]{}")
    while True:
        t = s.replace("()", "").replace("[]", "").replace("{}", "")
        if t == s:
            return s == ""
        s = t
"""]
MUTANTS = [
    """
def solution(text):
    return all(text.count(a) == text.count(b) for a, b in ["()", "[]", "{}"])
""",
    """
def solution(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return True
""",
]
CASES = exercism("matching-brackets")


def tests():
    t = [{"text": "{ cfg[(a + b) * c] }"}, {"text": "f(x[0)]"}]
    t += [{"text": i["value"]} for i, _ in CASES]
    r = rng(101)
    for _ in range(4):
        t.append({"text": "".join(r.choice("()[]{}ab ") for _ in range(r.randint(4, 14)))})
    return t


def expected():
    return [None, None] + [e for _, e in CASES] + [None] * 4
