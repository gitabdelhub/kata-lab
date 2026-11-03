from kit import exercism, rng, EXERCISM

ID = "bp08"
NAME = "Invert the Score Mapping"
LANG = "python"
PARAMS = ["legacy"]
MINUTES = 8
TAGS = ["dict", "inverser une table", "minuscules"]
SOURCE = EXERCISM + " · etl"
IO = [("input", "dictionary legacy"), ("output", "dictionary")]
SUMMARY_FR = "Inverser une table {score: [lettres]} en {lettre en minuscule: score} (le score devient un entier)."
HINTS = ["Deux boucles : pour chaque score, pour chaque lettre, out[lettre.lower()] = int(score)."]
DESC = """
<p>An old scoring system stores its configuration as a dictionary <code>legacy</code> where each key is a score (written as a string) and each value is the list of upper-case letters that are worth this score.</p>
<p>The new system needs the opposite mapping. Your task is to return a dictionary where each key is a letter in <b>lower case</b> and each value is its score as an <b>integer</b>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(legacy):
    # write your code here
    return {}
"""
SOLUTION = """
def solution(legacy):
    out = {}
    for score, letters in legacy.items():
        for letter in letters:
            out[letter.lower()] = int(score)
    return out
"""
ALT = ["""
def solution(legacy):
    return {l.lower(): int(s) for s, ls in legacy.items() for l in ls}
"""]
MUTANTS = [
    """
def solution(legacy):
    return {l.lower(): s for s, ls in legacy.items() for l in ls}
""",
    """
def solution(legacy):
    return {l: int(s) for s, ls in legacy.items() for l in ls}
""",
]
CASES = exercism("etl")


def tests():
    t = [{"legacy": {"1": ["A", "E"], "2": ["D"], "10": ["Q", "Z"]}}, {"legacy": {"4": ["F", "H"], "8": ["J"]}}]
    t += [{"legacy": i["legacy"]} for i, _ in CASES]
    r = rng(108)
    letters = list("ABCDEFGHIJKLMNOP")
    r.shuffle(letters)
    t.append({"legacy": {str(k): letters[2 * k - 2: 2 * k] for k in range(1, 6)}})
    return t


def expected():
    return [None, None] + [e for _, e in CASES] + [None]
