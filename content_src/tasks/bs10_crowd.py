from kit import table, tables, rng, BLSQL

ID = "bs10"
NAME = "Crowded Gate Streaks"
LANG = "sql"
MINUTES = 18
TAGS = ["gaps and islands", "id consécutifs", "COUNT OVER (PARTITION BY groupe)"]
SOURCE = BLSQL + " · Human Traffic of Stadium (LeetCode 601)"
SUMMARY_FR = "Retourner toutes les lignes qui font partie d'une suite d'au moins 3 id consécutifs où la fréquentation est >= 100."
HINTS = ["Garde d'abord les lignes avec people >= 100, puis id - ROW_NUMBER() OVER (ORDER BY id) donne la même valeur dans une suite d'id consécutifs.",
         "COUNT(*) OVER (PARTITION BY grp) donne la taille de la suite ; garde les lignes où elle vaut au moins 3."]
DESC = """
<p>A stadium counts the people passing through a gate every hour. You have the table <b>gate_traffic</b> with the columns <code>id</code> (integer, unique, increases with time), <code>visit_at</code> (timestamp) and <code>people</code> (integer). Some ids can be missing (the sensor was off).</p>
<p>A <b>crowded streak</b> is a series of at least <b>3 rows with consecutive ids</b> (no id missing between them) where every row has <code>people &gt;= 100</code>.</p>
<p>Your task is to return all the rows that belong to a crowded streak, with the columns <code>id</code>, <code>visit_at</code> and <code>people</code>, sorted by <code>id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
SELECT id, visit_at, people FROM gate_traffic WHERE people >= 100 ORDER BY id;
"""
SOLUTION = """
WITH busy AS (
  SELECT id, visit_at, people, id - ROW_NUMBER() OVER (ORDER BY id) AS grp
  FROM gate_traffic
  WHERE people >= 100
),
sized AS (SELECT *, COUNT(*) OVER (PARTITION BY grp) AS len FROM busy)
SELECT id, visit_at, people FROM sized WHERE len >= 3 ORDER BY id;
"""
ALT = ["""
SELECT DISTINCT a.id, a.visit_at, a.people
FROM gate_traffic a, gate_traffic b, gate_traffic c
WHERE a.people >= 100 AND b.people >= 100 AND c.people >= 100
  AND ((a.id + 1 = b.id AND b.id + 1 = c.id) OR (b.id + 1 = a.id AND a.id + 1 = c.id) OR (b.id + 1 = c.id AND c.id + 1 = a.id))
ORDER BY a.id;
"""]
MUTANTS = [
    """
WITH busy AS (SELECT id, visit_at, people, ROW_NUMBER() OVER (ORDER BY id) - ROW_NUMBER() OVER (PARTITION BY people >= 100 ORDER BY id) AS grp FROM gate_traffic),
sized AS (SELECT *, COUNT(*) OVER (PARTITION BY grp) AS len FROM busy WHERE people >= 100)
SELECT id, visit_at, people FROM sized WHERE len >= 3 ORDER BY id;
""",
    """
WITH w AS (SELECT *, LEAD(people) OVER (ORDER BY id) AS n1, LEAD(people, 2) OVER (ORDER BY id) AS n2 FROM gate_traffic)
SELECT id, visit_at, people FROM w WHERE people >= 100 AND n1 >= 100 AND n2 >= 100 ORDER BY id;
""",
]
G = "id INT, visit_at TIMESTAMP, people INT"


def tests():
    t = [tables(gate_traffic=table(G, [[1, "2026-01-01 10:00:00", 10], [2, "2026-01-01 11:00:00", 109], [3, "2026-01-01 12:00:00", 150], [4, "2026-01-01 13:00:00", 99],
                                       [5, "2026-01-01 14:00:00", 145], [6, "2026-01-01 15:00:00", 1455], [7, "2026-01-01 16:00:00", 199], [8, "2026-01-01 17:00:00", 188]])),
         tables(gate_traffic=table(G, [[1, "2026-01-02 10:00:00", 100], [2, "2026-01-02 11:00:00", 300], [4, "2026-01-02 13:00:00", 500], [5, "2026-01-02 14:00:00", 120], [6, "2026-01-02 15:00:00", 101]]))]
    r = rng(210)
    for _ in range(7):
        rows, i = [], 0
        for h in range(r.randint(5, 16)):
            i += r.choice([1, 1, 1, 1, 2])
            rows.append([i, f"2026-01-03 {h:02d}:00:00", r.choice([50, 99, 100, 150, 200, 250, 400, 300, 120, 180])])
        r.shuffle(rows)
        t.append(tables(gate_traffic=table(G, rows)))
    return t
