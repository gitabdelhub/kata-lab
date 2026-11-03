"""Serveur de correction Kata Lab (tourne dans le Codespace).

Il garde une SparkSession allumée et exécute le code PySpark envoyé par le site
sur les entrées de chaque test. Le site compare ensuite la sortie à l'attendu.

    POST /run   {code, entry, params, tests:[{input}], limit_s}
    GET  /health

Sécurité : chaque appel /run doit porter le jeton GitHub du propriétaire du
Codespace (en-tête X-Kata-Key, ou Authorization: Bearer). Le serveur vérifie le
jeton auprès de l'API GitHub et compare le login à GITHUB_USER.

Économie d'heures : si le site ne donne plus signe de vie pendant 30 minutes,
le serveur éteint lui-même le Codespace (gh codespace stop).
"""
import contextlib
import datetime as dt
import decimal
import hashlib
import io
import json
import math
import os
import shutil
import subprocess
import tempfile
import threading
import time
import traceback
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("KATA_PORT", "8765"))
OWNER = (os.environ.get("GITHUB_USER") or "").lower()
NO_AUTH = os.environ.get("KATA_NO_AUTH") == "1"
ORIGINS = set(
    os.environ.get(
        "KATA_ORIGINS",
        "https://gitabdelhub.github.io,http://localhost:8000,http://127.0.0.1:8000",
    ).split(",")
)

STATE = {"ready": False, "error": None, "spark": None, "version": None, "started": time.time()}
RUN_LOCK = threading.Lock()
GOOD_TOKENS = set()
IDLE_STOP_S = int(os.environ.get("KATA_IDLE_STOP_S", "1800"))
LAST_SEEN = [time.time()]


def boot_spark():
    try:
        from pyspark.sql import SparkSession

        spark = (
            SparkSession.builder.master("local[2]")
            .appName("kata-runner")
            .config("spark.ui.enabled", "false").config("spark.ui.showConsoleProgress", "false")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.driver.memory", "1g")
            .config("spark.sql.session.timeZone", "UTC")
            .getOrCreate()
        )
        spark.sparkContext.setLogLevel("ERROR")
        spark.range(1).count()  # chauffe la JVM
        STATE.update(ready=True, spark=spark, version=spark.version)
    except Exception as exc:  # pragma: no cover
        STATE["error"] = repr(exc)


# ---------- normalisation des sorties (même règle que tools/build.py) ----------
def norm(v):
    from pyspark.sql import Row

    if v is None:
        return None
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        if math.isnan(v):
            return "NaN"
        return v
    if isinstance(v, decimal.Decimal):
        return float(v)
    if isinstance(v, dt.datetime):
        return v.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(v, dt.date):
        return v.isoformat()
    if isinstance(v, Row):
        return {k: norm(x) for k, x in v.asDict().items()}
    if isinstance(v, dict):
        return {str(k): norm(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [norm(x) for x in v]
    return str(v)


def df_to_table(df):
    rows = df.collect()
    return {"columns": list(df.columns), "rows": [[norm(x) for x in r] for r in rows]}


def coerce_rows(schema_ddl, rows):
    """Les tests stockent les dates en texte ISO : on les convertit selon le schéma."""
    from pyspark.sql.types import DateType, DecimalType, DoubleType, FloatType, StructType, TimestampType

    st = StructType.fromDDL(schema_ddl)
    conv = []
    for f in st.fields:
        if isinstance(f.dataType, DateType):
            conv.append(lambda v: dt.date.fromisoformat(v) if isinstance(v, str) else v)
        elif isinstance(f.dataType, TimestampType):
            conv.append(lambda v: dt.datetime.fromisoformat(v) if isinstance(v, str) else v)
        elif isinstance(f.dataType, (DoubleType, FloatType)):
            # le JSON du navigateur écrit 40.0 comme 40
            conv.append(lambda v: float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v)
        elif isinstance(f.dataType, DecimalType):
            conv.append(lambda v: decimal.Decimal(str(v)) if v is not None else v)
        else:
            conv.append(lambda v: v)
    return st, [tuple(c(v) for c, v in zip(conv, r)) for r in rows]


def build_args(spark, params, inp, tmp):
    args = []
    for name in params:
        if name == "spark":
            args.append(spark)
            continue
        val = inp.get(name)
        if isinstance(val, dict) and "__df__" in val:
            st, rows = coerce_rows(val["__df__"]["schema"], val["__df__"]["rows"])
            args.append(spark.createDataFrame(rows, st))
        elif isinstance(val, dict) and "__dir__" in val:
            root = os.path.join(tmp, name)
            for rel, content in val["__dir__"].items():
                path = os.path.join(root, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(content)
            os.makedirs(root, exist_ok=True)
            args.append(root)
        else:
            args.append(val)
    return args


def short_tb(exc):
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    lines = [ln for ln in tb if 'File "<solution>"' in ln or not ln.startswith("  File")]
    text = "".join(lines)
    # les erreurs Spark sont très longues : on garde l'essentiel
    return text[-2500:]


def run_one(code, entry, params, inp, limit_s):
    spark = STATE["spark"]
    out = io.StringIO()
    tmp = tempfile.mkdtemp(prefix="kata_")
    result = {}

    def target():
        try:
            ns = {"__name__": "solution"}
            compiled = compile(code, "<solution>", "exec")
            with contextlib.redirect_stdout(out):
                exec(compiled, ns)
                if entry not in ns:
                    raise NameError(f"La fonction {entry}() est introuvable dans ton code.")
                args = build_args(spark, params, inp, tmp)
                res = ns[entry](*args)
                if res is None:
                    raise TypeError(f"{entry}() a renvoyé None : il manque un return.")
                if hasattr(res, "collect") and hasattr(res, "columns"):
                    result["output"] = df_to_table(res)
                else:
                    result["output"] = {"value": norm(res)}
            result["ok"] = True
        except BaseException as exc:  # noqa: BLE001
            result["ok"] = False
            result["error"] = short_tb(exc)

    t0 = time.time()
    th = threading.Thread(target=target, daemon=True)
    th.start()
    th.join(limit_s)
    ms = int((time.time() - t0) * 1000)
    if th.is_alive():
        try:
            spark.sparkContext.cancelAllJobs()
        except Exception:
            pass
        th.join(5)
        result = {"ok": False, "error": f"Execution time limit exceeded ({limit_s} s)", "tle": True}
    shutil.rmtree(tmp, ignore_errors=True)
    result["stdout"] = out.getvalue()[-4000:]
    result["ms"] = ms
    return result


# ---------- auth ----------
def token_ok(key, header):
    if NO_AUTH:
        return True
    token = (key or "").strip()
    if not token and header and header.lower().startswith("bearer "):
        token = header.split(" ", 1)[1].strip()
    if not token:
        return False
    h = hashlib.sha256(token.encode()).hexdigest()
    if h in GOOD_TOKENS:
        return True
    try:
        req = urllib.request.Request(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "kata-runner"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            login = json.load(resp).get("login", "").lower()
        if login and (not OWNER or login == OWNER):
            GOOD_TOKENS.add(h)
            return True
    except Exception:
        return False
    return False


class Handler(BaseHTTPRequestHandler):
    server_version = "kata-runner/1"

    def log_message(self, *a):  # silence
        pass

    def cors(self):
        origin = self.headers.get("Origin")
        if origin in ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Kata-Key, X-Tunnel-Skip-AntiPhishing-Page")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Max-Age", "600")

    def reply(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors()
        self.end_headers()

    def do_GET(self):
        LAST_SEEN[0] = time.time()
        if self.path.startswith("/health"):
            self.reply(200, {"ok": True, "ready": STATE["ready"], "spark": STATE["version"], "error": STATE["error"],
                             "uptime": int(time.time() - STATE["started"])})
        else:
            self.reply(404, {"error": "not found"})

    def do_POST(self):
        if not self.path.startswith("/run"):
            return self.reply(404, {"error": "not found"})
        LAST_SEEN[0] = time.time()
        if not token_ok(self.headers.get("X-Kata-Key"), self.headers.get("Authorization")):
            return self.reply(401, {"error": "Clé refusée. Vérifie ta clé GitHub dans Connexion."})
        if not STATE["ready"]:
            return self.reply(503, {"error": "Spark démarre encore, réessaie dans quelques secondes."})
        try:
            n = int(self.headers.get("Content-Length", "0"))
            req = json.loads(self.rfile.read(n) or b"{}")
            code, entry = req["code"], req.get("entry", "solve")
            params, tests = req.get("params", ["spark"]), req.get("tests", [])
            limit_s = min(float(req.get("limit_s", 30)), 120)
        except Exception as exc:
            return self.reply(400, {"error": f"Requête invalide : {exc}"})
        with RUN_LOCK:
            results = [run_one(code, entry, params, t.get("input", {}), limit_s) for t in tests]
        self.reply(200, {"results": results})


def watchdog():
    """Éteint le Codespace après IDLE_STOP_S secondes sans appel du site."""
    name = os.environ.get("CODESPACE_NAME")
    while True:
        time.sleep(60)
        if name and time.time() - LAST_SEEN[0] > IDLE_STOP_S:
            print("idle: stopping codespace", flush=True)
            subprocess.run(["gh", "codespace", "stop", "-c", name], check=False)
            LAST_SEEN[0] = time.time()


if __name__ == "__main__":
    threading.Thread(target=boot_spark, daemon=True).start()
    threading.Thread(target=watchdog, daemon=True).start()
    print(f"kata-runner on :{PORT} (owner={OWNER or '?'}, no_auth={NO_AUTH})", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
