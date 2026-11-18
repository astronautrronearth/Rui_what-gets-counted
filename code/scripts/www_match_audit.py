"""Human verification of the exact registry matches that the ranking rules actually retrieved (2026-11-15, review
response). One row per retrieved listing (union over the non-random rules, b = 5): main window from
registry_retrieved.json, fresh window (updated snapshot, original 8 days) from crossover_fresh_mature2.json.

The sheet is blind to the rules: it shows the candidate name, one example post, the registry record and the gap
in days; the rule membership goes to a separate key file.

    python scripts/www_match_audit.py → outputs/www_audit/match_retrieved/{sheet.csv, key.csv}
"""
import csv
import importlib.util
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path[:0] = ["src", "scripts"]
from sensor import db  # noqa: E402

W = Path("outputs/interaction_experiment/www_eval")
OUT = Path("outputs/www_audit/match_retrieved")


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


REG = _mod("reg", "scripts/www_eval_registry.py")


def clusters_from(path):
    cl = defaultdict(list)
    for line in open(path):
        v = json.loads(line)
        for name in sorted({REG.norm(x) for x in v.get("victims") or []}):
            if len(name) >= 3:
                cl[name].append(v["post_id"])
    return cl


def main():
    rows, key = [], []
    for window, res, retr_key, vict in (
            ("main", W / "registry_retrieved.json", None, W / "victims.jsonl"),
            ("fresh", W / "crossover_fresh_mature2.json", "b5", W / "victims_fresh.jsonl")):
        d = json.loads(res.read_text())
        if window == "main":
            sets = {k.split("|")[0]: set(v) for k, v in d["retrieved_exact"].items() if k.endswith("|b5")}
        else:
            sets = {p: set(d["b5"][p]["retrieved_any_order"]) for p in ("posts", "authors", "nofeed", "edges", "responders")}
        union = set().union(*sets.values())
        by_ev = defaultdict(list)
        for k, evs in d["exact_matches_by_candidate"].items():
            for e in evs:
                by_ev[e].append(k)
        cl = clusters_from(vict)
        for e in sorted(union):
            for k in by_ev.get(e, []):
                rows.append({"window": window, "event_id": e, "candidate": k, "first_post": d["first_post_by_candidate"][k],
                             "posts": cl.get(k, [])})
                key.append({"window": window, "event_id": e, "candidate": k,
                            **{f"rule_{p}": int(e in s) for p, s in sorted(sets.items())}})
    with db.connect() as c:
        ev = {r["event_id"]: r for r in c.execute(
            "SELECT event_id, title, country, published_at_utc, url, raw_payload->>'group_name' AS grp FROM external_events "
            "WHERE event_id = ANY(%s)", ([r["event_id"] for r in rows],))}
        pids = sorted({p for r in rows for p in r["posts"]})
        po = {r["post_id"]: r for r in c.execute("SELECT post_id, url AS uri, text, published_at FROM posts WHERE post_id = ANY(%s)", (pids,))}
    random.Random(20261115).shuffle(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    ids = {}
    with open(OUT / "sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "candidate_name_extracted", "example_post_text", "example_post_uri", "n_posts_naming_it",
                    "registry_victim", "registry_country", "registry_group", "registry_listing_date", "first_post_date",
                    "days_listing_minus_first_post", "registry_url",
                    "same_organisation(yes/no/unsure)", "notes"])
        for i, r in enumerate(rows, 1):
            e = ev[r["event_id"]]
            ex = next((po[p] for p in sorted(r["posts"], key=lambda p: po[p]["published_at"] if p in po else 0) if p in po), None)
            iid = f"M{i:03d}"
            ids[(r["window"], r["event_id"], r["candidate"])] = iid
            gap = (e["published_at_utc"].date() - __import__("datetime").date.fromisoformat(r["first_post"])).days
            w.writerow([iid, r["candidate"], (ex["text"] or "").replace("\n", " ")[:400] if ex else "",
                        ex["uri"] if ex else "", len(r["posts"]), e["title"], e["country"], e["grp"] or "",
                        e["published_at_utc"].date(), r["first_post"], gap, e["url"] or "", "", ""])
    with open(OUT / "key.csv", "w", newline="", encoding="utf-8") as f:
        cols = sorted({k for r in key for k in r})
        w = csv.DictWriter(f, fieldnames=["item_id"] + cols)
        w.writeheader()
        for r in key:
            w.writerow({"item_id": ids[(r["window"], r["event_id"], r["candidate"])], **r})
    print(len(rows), "rows", OUT)


if __name__ == "__main__":
    main()
