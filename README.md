# kata-lab



- `docs/` : le site (GitHub Pages, branche `main`, dossier `/docs`). SQL (PGlite) et Python (Pyodide) tournent dans la page.
- `runner/` + `.devcontainer/` : le Codespace que le site allume pour le vrai PySpark (`runner/server.py`, port 8765).
- `content_src/` : les exos, leurs tests et leurs solutions de référence ; `course.py` = le parcours.
- `tools/build.py` : recalcule les sorties attendues (vrai Spark, PostgreSQL 16, Python) et vérifie que les erreurs fréquentes échouent.

Reconstruire le contenu : `python tools/build.py` (Spark 4.3 + PostgreSQL 16 locaux).


