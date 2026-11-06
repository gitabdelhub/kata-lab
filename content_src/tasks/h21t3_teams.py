from kit import table, tables, rng

ID = "h21t3"
NAME = "Team Size at Every Level"
LANG = "sql"
MINUTES = 25
TAGS = ["CTE récursive", "hiérarchie", "profondeur", "managers sans chef", "agrégats sur toute la descendance"]
DESC = """
<p>The table <b>employees</b> has the columns <code>emp_id</code>, <code>name</code>, <code>manager_id</code> (<code>NULL</code> for the top of the company) and <code>salary</code>. There is no cycle. A <code>manager_id</code> that does not exist in the table is treated like <code>NULL</code>.</p>
<p>The <b>team</b> of an employee is everybody below them, at any level: their direct reports, the reports of their reports, and so on (the employee is not in their own team).</p>
<p>Your task is to return, for every employee with at least one direct report, the columns <code>emp_id</code>, <code>name</code>, <code>level</code> (1 for an employee with no manager, 2 for their direct reports, and so on), <code>team_size</code>, <code>team_salary</code> (total salary of the team) and <code>depth</code> (the number of levels below them: 1 when nobody in their team has reports), sorted by <code>team_salary</code> from the highest, then <code>emp_id</code>.</p>
<h4>Example</h4>{{EXAMPLE}}
"""
STARTER = """/* Write your PostgreSQL query here */
"""
SOLUTION = """
WITH RECURSIVE e AS (
  SELECT x.emp_id, x.name, x.salary,
         CASE WHEN m.emp_id IS NULL THEN NULL ELSE x.manager_id END AS manager_id
  FROM employees x LEFT JOIN employees m ON m.emp_id = x.manager_id
), lvl AS (
  SELECT emp_id, 1 AS level FROM e WHERE manager_id IS NULL
  UNION ALL
  SELECT e.emp_id, lvl.level + 1 FROM e JOIN lvl ON e.manager_id = lvl.emp_id
), below AS (
  SELECT manager_id AS boss, emp_id, 1 AS dist FROM e WHERE manager_id IS NOT NULL
  UNION ALL
  SELECT below.boss, e.emp_id, below.dist + 1 FROM below JOIN e ON e.manager_id = below.emp_id
)
SELECT e.emp_id, e.name, lvl.level, COUNT(*) AS team_size, SUM(t.salary) AS team_salary, MAX(b.dist) AS depth
FROM below b
JOIN e ON e.emp_id = b.boss
JOIN e t ON t.emp_id = b.emp_id
JOIN lvl ON lvl.emp_id = e.emp_id
GROUP BY e.emp_id, e.name, lvl.level
ORDER BY team_salary DESC, e.emp_id;
"""
MUTANTS = [
    SOLUTION.replace("CASE WHEN m.emp_id IS NULL THEN NULL ELSE x.manager_id END AS manager_id", "x.manager_id"),
    SOLUTION.replace("  SELECT manager_id AS boss, emp_id, 1 AS dist FROM e WHERE manager_id IS NOT NULL\n  UNION ALL\n  SELECT below.boss, e.emp_id, below.dist + 1 FROM below JOIN e ON e.manager_id = below.emp_id",
                     "  SELECT manager_id AS boss, emp_id, 1 AS dist FROM e WHERE manager_id IS NOT NULL"),
    SOLUTION.replace("MAX(b.dist) AS depth", "MAX(b.dist) - 1 AS depth"),
    SOLUTION.replace("SUM(t.salary) AS team_salary", "SUM(t.salary) + MAX(e.salary) AS team_salary"),
]
T = "emp_id INT, name TEXT, manager_id INT, salary INT"


def tests():
    t = [tables(employees=table(T, [[1, "Nadia", None, 9000], [2, "Yao", 1, 6000], [3, "Lina", 1, 6500], [4, "Omar", 2, 4000], [5, "Awa", 2, 4200],
                                    [6, "Kofi", 4, 3000], [7, "Sami", 3, 3900], [8, "Ines", 99, 5000], [9, "Theo", 8, 3100]])),
         tables(employees=table(T, [[10, "A", None, 1], [11, "B", 10, 1], [12, "C", 11, 1], [13, "D", 12, 1], [20, "E", None, 5], [21, "F", 20, 3]]))]
    r = rng(4213)
    for _ in range(8):
        n = r.randint(4, 25)
        rows = []
        for i in range(1, n + 1):
            mgr = None if i == 1 or r.random() < 0.08 else r.randint(1, i - 1)
            if mgr is not None and r.random() < 0.05:
                mgr = 500
            rows.append([i, f"e{i}", mgr, r.choice([2500, 3000, 4500, 6000, 9000])])
        t.append(tables(employees=table(T, rows)))
    return t
