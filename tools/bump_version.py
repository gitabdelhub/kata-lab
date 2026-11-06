"""Nouvelle version du site : met à jour docs/version.json et les ?v= de docs/index.html.
A lancer avant chaque commit qui change le site, pour que le favori de Chrome charge la nouvelle version."""
import json, re, time, pathlib
root = pathlib.Path(__file__).resolve().parent.parent / "docs"
v = time.strftime("%Y%m%d%H%M%S")
(root / "version.json").write_text(json.dumps({"v": v}) + "\n")
idx = root / "index.html"
s = idx.read_text()
s = re.sub(r'((?:src|href)="(?:assets|vendor)/[^"?]+\.(?:js|css))(\?v=\w+)?"', lambda m: m.group(1) + "?v=" + v + '"', s)
s = re.sub(r'window\.KATA_V = "\w*"', 'window.KATA_V = "' + v + '"', s)
idx.write_text(s)
print("version", v)
