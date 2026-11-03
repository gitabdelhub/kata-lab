# kata-lab

Carnet d'exercices : https://gitabdelhub.github.io/kata-lab/

- `docs/` : le site (GitHub Pages, branche `main`, dossier `/docs`). SQL (PGlite) et Python (Pyodide) tournent dans la page.
- `runner/` + `.devcontainer/` : le Codespace que le site allume pour le vrai PySpark (`runner/server.py`, port 8765).
- `content_src/` : les exos, leurs tests et leurs solutions de référence ; `course.py` = le parcours.
- `tools/build.py` : recalcule les sorties attendues (vrai Spark, PostgreSQL 16, Python) et vérifie que les erreurs fréquentes échouent.

Reconstruire le contenu : `python tools/build.py` (Spark 4.3 + PostgreSQL 16 locaux).

## Banques d'exercices externes

Certaines tasks sont adaptées de banques sous licence MIT (licences copiées dans `content_src/banks/`) :

- [exercism/problem-specifications](https://github.com/exercism/problem-specifications) : tasks `bp01` à `bp10`. Les réponses officielles de la banque sont vérifiées à chaque build.
- [shawlu95/Beyond-LeetCode-SQL](https://github.com/shawlu95/Beyond-LeetCode-SQL) : tasks `bs01` à `bs10`. Chaque task a une deuxième solution indépendante qui doit donner le même résultat sur tous les tests.
