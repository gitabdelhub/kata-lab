from kit import rng

ID = "d04"
NAME = "Clean Palindrome Check"
LANG = "python"
PARAMS = ["text"]
MINUTES = 10
TAGS = ["DSA", "deux pointeurs", "isalnum", "O(1) mémoire"]
IO = [("input", "string text"), ("output", "boolean")]
SUMMARY_FR = "Dire si le texte est un palindrome en ne gardant que lettres et chiffres et en ignorant la casse, avec deux pointeurs (sans créer de copie nettoyée)."
HINTS = ["Un pointeur à gauche, un à droite ; saute ce qui n'est pas isalnum().", "Compare en lower(). Un texte sans lettre ni chiffre est un palindrome."]
DESC = """
<p>Your task is to return <code>true</code> if <code>text</code> reads the same forwards and backwards when you keep only letters and digits and ignore case, <code>false</code> otherwise.</p>
<p>Use two pointers that move towards each other and skip the other characters. A text without any letter or digit is a palindrome.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(text):
    # write your code here
    return False
"""
SOLUTION = """
def solution(text):
    i, j = 0, len(text) - 1
    while i < j:
        if not text[i].isalnum():
            i += 1
        elif not text[j].isalnum():
            j -= 1
        elif text[i].lower() != text[j].lower():
            return False
        else:
            i += 1; j -= 1
    return True
"""
ALT = ["""
def solution(text):
    s = [c.lower() for c in text if c.isalnum()]
    return s == s[::-1]
"""]
MUTANTS = ["""
def solution(text):
    return text.lower() == text.lower()[::-1]
""", """
def solution(text):
    s = [c for c in text if c.isalnum()]
    return s == s[::-1]
"""]


def tests():
    t = [{"text": "A man, a plan, a canal: Panama"}, {"text": "race a car"}, {"text": " ,;"}, {"text": "0P"}, {"text": "Ab1 1bA"}]
    r = rng(2004)
    for _ in range(7):
        half = "".join(r.choice("aAbB1 ,.") for _ in range(r.randint(0, 5)))
        s = half + r.choice(["", "x", " "]) + half[::-1]
        if r.random() < 0.4:
            s += r.choice("cd")
        t.append({"text": s})
    return t
