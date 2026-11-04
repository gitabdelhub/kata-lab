from kit import rng

ID = "d08"
NAME = "Evaluate a Metric Formula"
LANG = "python"
PARAMS = ["tokens"]
MINUTES = 12
TAGS = ["DSA", "pile", "notation polonaise inverse", "division entière vers zéro"]
IO = [("input", "array.string tokens"), ("output", "integer")]
SUMMARY_FR = "Évaluer une formule en notation polonaise inverse (+ - * /) avec une pile ; la division est entière et tronque vers zéro."
HINTS = ["Un nombre : empile. Un opérateur : dépile b PUIS a, calcule a op b, empile.", "Attention : -7 // 2 vaut -4 en Python. Tronquer vers zéro : int(a / b)."]
DESC = """
<p>A dashboard stores metric formulas in <b>reverse Polish notation</b>: each operator comes after its two operands, so <code>["3", "4", "+", "2", "*"]</code> means <code>(3 + 4) * 2</code>. Tokens are integers (possibly negative) or one of <code>+</code>, <code>-</code>, <code>*</code>, <code>/</code>.</p>
<p>Your task is to return the value of the formula. Division is integer division that <b>truncates toward zero</b> (<code>-7 / 2</code> gives <code>-3</code>). The formula is always valid and never divides by zero.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(tokens):
    # write your code here
    return 0
"""
SOLUTION = """
def solution(tokens):
    st = []
    for t in tokens:
        if t in "+-*/" and len(t) == 1:
            b = st.pop(); a = st.pop()
            if t == "+": st.append(a + b)
            elif t == "-": st.append(a - b)
            elif t == "*": st.append(a * b)
            else: st.append(abs(a) // abs(b) * (1 if (a >= 0) == (b >= 0) else -1))
        else:
            st.append(int(t))
    return st[-1]
"""
ALT = ["""
def solution(tokens):
    st = []
    for t in tokens:
        if t in ("+", "-", "*", "/"):
            b, a = st.pop(), st.pop()
            st.append({"+": a + b, "-": a - b, "*": a * b, "/": int(a / b) if b else 0}[t])
        else: st.append(int(t))
    return st[-1]
"""]
MUTANTS = ["""
def solution(tokens):
    st = []
    for t in tokens:
        if t in ("+", "-", "*", "/"):
            b, a = st.pop(), st.pop()
            st.append({"+": a + b, "-": a - b, "*": a * b, "/": a // b if b else 0}[t])
        else: st.append(int(t))
    return st[-1]
""", """
def solution(tokens):
    st = []
    for t in tokens:
        if t in ("+", "-", "*", "/"):
            a, b = st.pop(), st.pop()
            st.append({"+": a + b, "-": a - b, "*": a * b, "/": int(a / b) if b else 0}[t])
        else: st.append(int(t))
    return st[-1]
"""]


def tests():
    t = [{"tokens": ["3", "4", "+", "2", "*"]}, {"tokens": ["-7", "2", "/"]}, {"tokens": ["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]}, {"tokens": ["42"]}]
    r = rng(2008)
    for _ in range(8):
        toks, depth = [str(r.randint(-9, 9))], 1
        for _ in range(r.randint(1, 5)):
            toks.append(str(r.choice([v for v in range(-9, 10) if v != 0]))); depth += 1
            toks.append(r.choice("+-*/")); depth -= 1
        t.append({"tokens": toks})
    return t
