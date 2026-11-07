"""Banque kursad-can/data-engineering-interview-practice (MIT) : données et échantillons de test.

Les données réelles de la banque sont dans content_src/banks/kursad/*.json (lues avec Spark, mêmes types que
le notebook d'origine). Chaque task reçoit 2 petits échantillons visibles, 3 échantillons cachés plus grands,
et le jeu de données complet. Les échantillons gardent les liens entre tables (clients -> commandes -> lignes ->
produits) et gardent les lignes « sales » (nulls, orphelins, doublons) qui sont le cœur des exos.
"""
import json
import os
import random

from kit import df

SRC = "kursad-can/data-engineering-interview-practice (MIT)"
_D = os.path.join(os.path.dirname(__file__), "banks", "kursad")
_cache = {}


def _t(name):
    if name not in _cache:
        _cache[name] = json.load(open(os.path.join(_D, name + ".json"), encoding="utf-8"))
    return _cache[name]


def _col(name, col):
    cols = [c.split()[0].strip("`") for c in _split(_t(name)["schema"])]
    return cols.index(col)


def _split(ddl):
    out, depth, cur = [], 0, ""
    for ch in ddl:
        depth += ch == "<"
        depth -= ch == ">"
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return out + [cur.strip()]


def _sample(names, r, k):
    rows = {n: _t(n)["rows"] for n in ["customers", "orders", "order_items", "products", "transactions",
                                        "cdc_changes", "events", "pipeline_logs", "malformed_events"]}
    ci = _col("customers", "customer_id")
    all_ids = sorted({x[ci] for x in rows["customers"] if x[ci] is not None})
    keys = set(r.sample(all_ids, min(k, len(all_ids)))) | {None}
    # chaque échantillon garde quelques cas « sales » (le cœur des exos qualité)
    units = _dirty()
    for u in [u for u in units if len(u) > 1] + r.sample(units, min(max(3, k // 2), len(units))):
        keys |= u
    out = {}
    cust = [x for x in rows["customers"] if x[ci] in keys]
    out["customers"] = cust
    oc = _col("orders", "customer_id")
    orders = [x for x in rows["orders"] if x[oc] in keys]
    orphans = [x for x in rows["orders"] if x[oc] is not None and x[oc] not in all_ids]
    orders += r.sample(orphans, min(2, len(orphans)))
    nulls = [x for x in orders if x[oc] is None]
    if len(nulls) > 3:
        orders = [x for x in orders if x[oc] is not None] + r.sample(nulls, 3)
    out["orders"] = sorted(orders, key=lambda x: x[0])
    oids = {x[0] for x in out["orders"]}
    io_ = _col("order_items", "order_id")
    items = [x for x in rows["order_items"] if x[io_] in oids]
    items += r.sample([x for x in rows["order_items"] if x[io_] not in oids], 2)
    out["order_items"] = sorted(items, key=lambda x: x[0])
    ip = _col("order_items", "product_id")
    pids = {x[ip] for x in out["order_items"]}
    prods = [x for x in rows["products"] if x[0] in pids]
    prods += r.sample([x for x in rows["products"] if x[0] not in pids], 2)
    out["products"] = sorted(prods, key=lambda x: x[0])
    for n in ["transactions", "cdc_changes"]:
        c = _col(n, "customer_id")
        out[n] = [x for x in rows[n] if x[c] in keys]
    es = _col("events", "session_id")
    sess = sorted({x[es] for x in rows["events"] if x[es] is not None})
    pick = set(r.sample(sess, min(max(2, k // 2), len(sess)))) | {None}
    out["events"] = [x for x in rows["events"] if x[es] in pick]
    out["pipeline_logs"] = sorted(r.sample(rows["pipeline_logs"], min(3 * k, len(rows["pipeline_logs"]))), key=lambda x: x[0])
    mc = _col("malformed_events", "_corrupt_record")
    bad = [x for x in rows["malformed_events"] if x[mc] is not None]
    good = [x for x in rows["malformed_events"] if x[mc] is None]
    out["malformed_events"] = r.sample(good, min(k, len(good))) + r.sample(bad, min(max(2, k // 3), len(bad)))
    return {n: df(_t(n)["schema"], out[n]) for n in names}


_dirty_cache = []


def _dirty():
    """Groupes de clients liés à une anomalie : email vide ou en double, montant invalide, commande qui ne
    correspond pas à ses lignes, montant de commande nul ou négatif."""
    if _dirty_cache:
        return _dirty_cache
    units = []
    cu = _t("customers")["rows"]
    ci, ce = _col("customers", "customer_id"), _col("customers", "email")
    groups = {}
    for x in cu:
        e = x[ce]
        if e is None or e.strip() == "":
            units.append({x[ci]})
        else:
            groups.setdefault(e.strip().lower(), set()).add(x[ci])
    units += [g for g in groups.values() if len(g) > 1]
    tr = _t("transactions")["rows"]
    tc, ta = _col("transactions", "customer_id"), _col("transactions", "amount")
    units += [{x[tc]} for x in tr if x[ta] is None or x[ta] <= 0]
    od = _t("orders")["rows"]
    oc, oa = _col("orders", "customer_id"), _col("orders", "amount")
    it = _t("order_items")["rows"]
    io_, iq, iu = _col("order_items", "order_id"), _col("order_items", "quantity"), _col("order_items", "unit_price")
    tot = {}
    for x in it:
        if x[iq] is not None and x[iu] is not None:
            tot[x[io_]] = tot.get(x[io_], 0) + x[iq] * x[iu]
    for x in od:
        if x[oa] is None or x[oa] < 0 or abs(x[oa] - tot.get(x[0], 0)) > 0.01:
            units.append({x[oc]})
    _dirty_cache.extend(u for u in units if u - {None})
    return _dirty_cache


def inputs(names, seed):
    """Tests d'une task : 2 visibles (petits), 3 cachés (moyens), puis le jeu complet de la banque."""
    r = random.Random("kursad-" + seed)
    t = [_sample(names, r, k) for k in (4, 5, 10, 16, 25)]
    t.append({n: df(_t(n)["schema"], _t(n)["rows"]) for n in names})
    return t
