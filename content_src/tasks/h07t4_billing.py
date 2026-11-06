from kit import rng

ID = "h07t4"
NAME = "Time-of-Use Electricity Bills"
LANG = "python"
PARAMS = ["prices", "readings"]
MINUTES = 30
TAGS = ["tranches horaires", "palier mensuel coupé au milieu d'une lecture", "doublons corrigés", "arrondi entier", "tri chronologique"]
IO = [("input", "dictionary prices"), ("input", "array.string readings"), ("output", "array.string")]
DESC = """
<p>Our smart meters send one reading per hour: <code>readings</code> is a list of strings <code>"meter,YYYY-MM-DD HH,kwh"</code>, where <code>HH</code> is the hour the consumption started (00 to 23) and <code>kwh</code> a non-negative integer. The list is <b>not sorted</b>. When the same meter sends the same hour several times, the reading that appears <b>last</b> in the list is a correction and replaces the others.</p>
<p><code>prices</code> gives the price in cents per kWh of three bands: <code>"night"</code> for the hours 23 to 06, <code>"peak"</code> for the hours 18 to 21, and <code>"day"</code> for every other hour (07 to 17 and 22).</p>
<p>A meter is billed per calendar month. The first 300 kWh of a month are charged at the band price; every kWh beyond 300 in that month costs 1.5 times the band price. The 300 kWh are counted in chronological order of the hours, so one hourly reading can be split: part at the normal price, part at the higher price. Each month with at least one reading also has a fixed charge of 100 cents.</p>
<p>The bill of a month is rounded to the nearest whole cent at the end (a half cent is rounded up). Your task is to return one string <code>"meter,YYYY-MM,cents"</code> per meter and month with at least one reading, sorted by meter, then month.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """
def solution(prices, readings):
    # write your code here
    return []
"""
SOLUTION = """
def solution(prices, readings):
    # 1. Garder la dernière lecture pour chaque (compteur, heure)
    last = {}
    for line in readings:
        meter, hour, kwh = line.split(",")
        last[(meter, hour)] = int(kwh)

    # 2. Parcourir les heures dans l'ordre chronologique, compteur par compteur
    keys = sorted(last)          # tri par compteur, puis par "YYYY-MM-DD HH"
    half_cents = {}              # (compteur, mois) -> montant en demi-centimes (évite les 0,5)
    used = {}                    # (compteur, mois) -> kWh déjà consommés dans le mois
    for meter, hour in keys:
        kwh = last[(meter, hour)]
        month = hour[:7]
        h = int(hour[11:13])
        if h >= 23 or h <= 6:
            price = prices["night"]
        elif 18 <= h <= 21:
            price = prices["peak"]
        else:
            price = prices["day"]
        k = (meter, month)
        if k not in used:
            used[k] = 0
            half_cents[k] = 2 * 100          # frais fixe : 100 centimes
        normal = min(kwh, max(0, 300 - used[k]))
        extra = kwh - normal
        half_cents[k] += 2 * normal * price + 3 * extra * price
        used[k] += kwh

    out = []
    for meter, month in sorted(half_cents):
        cents = (half_cents[(meter, month)] + 1) // 2      # arrondi au centime, 0,5 vers le haut
        out.append(meter + "," + month + "," + str(cents))
    return out
"""
MUTANTS = [
    SOLUTION.replace("        last[(meter, hour)] = int(kwh)", "        last[(meter, hour)] = last.get((meter, hour), 0) + int(kwh)"),
    SOLUTION.replace("        normal = min(kwh, max(0, 300 - used[k]))", "        normal = kwh if used[k] + kwh <= 300 else 0"),
    SOLUTION.replace("elif 18 <= h <= 21:", "elif 18 <= h <= 22:"),
    SOLUTION.replace("    keys = sorted(last)          # tri par compteur, puis par \"YYYY-MM-DD HH\"", "    keys = list(last)"),
    SOLUTION.replace("cents = (half_cents[(meter, month)] + 1) // 2", "cents = half_cents[(meter, month)] // 2"),
]


def tests():
    p = {"night": 11, "day": 17, "peak": 29}
    t = [{"prices": p, "readings": ["m1,2026-03-01 18,100", "m1,2026-03-01 07,150", "m1,2026-03-01 23,60", "m1,2026-03-01 07,120",
                                     "m1,2026-04-02 22,5", "m2,2026-03-31 06,1"]},
         {"prices": {"night": 3, "day": 7, "peak": 9}, "readings": ["a,2026-01-01 00,299", "a,2026-01-01 21,3", "a,2026-01-31 23,1",
                                                                       "b,2026-01-01 12,0"]}]
    r = rng(4074)
    for k in range(9):
        rows = []
        for _ in range(r.randint(5, 60) if k < 8 else 3000):
            m = r.choice(["m1", "m2", "m10"])
            rows.append(f"{m},2026-{r.choice(['01', '02', '02'])}-{r.randint(1, 28):02d} {r.randint(0, 23):02d},{r.choice([0, 1, 7, 25, 40, 90, 150])}")
            if r.random() < 0.1:
                rows.append(rows[-1].rsplit(",", 1)[0] + "," + str(r.randint(0, 60)))
        t.append({"prices": {"night": r.randint(5, 15), "day": r.randint(10, 25), "peak": r.randint(20, 41)}, "readings": rows})
    return t
