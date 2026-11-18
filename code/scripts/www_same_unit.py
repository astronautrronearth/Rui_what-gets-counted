"""Same-unit control (2026-11-15, review response): rank the event task's victim candidates with the event task's
rules, budget and review-once protocol, but score each reviewed candidate by the discussion objective instead of
registry listings. Only the objective changes: unit, content (ransomware posts), cumulative window and budget are
those of the event task.

Discussion objective for candidate k reviewed on day d: accounts other than the post's author that reply to or
quote any of k's posts published up to d within 24 hours after the cutoff (end of day d), excluding accounts that
had replied to or quoted those posts before the cutoff. Results are averaged over random tie orders; intervals are
95% percentile bootstrap intervals over evaluation days of the summed daily difference to post volume.

Called from www_same_unit_main.py / www_same_unit_fresh.py, which load the data exactly as the event replays do.
"""
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import numpy as np

POLS = ("posts", "capped", "authors", "nofeed", "edges", "responders", "random")


def cut(d):
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc) + timedelta(days=1)


def run(clusters, info, edges, feeds, review_days, eval_days, budgets=(5,), reps=50, seed=20261115):
    eb = defaultdict(list)
    for e in edges:
        if e["edge_type"] in ("reply", "quote") and e["event_created_at"] is not None and e["seed_post_id"] in info:
            eb[e["seed_post_id"]].append(e)
    first = {k: min(info[s]["published_at"].date() for s in L) for k, L in clusters.items() if L}
    upto = {}

    def posts(k, d):
        key = (k, d)
        if key not in upto:
            upto[key] = [s for s in clusters[k] if info[s]["published_at"].date() <= d]
        return upto[key]

    def score(k, d, pol):
        L = posts(k, d)
        c = cut(d)
        if pol == "posts":
            return len(L)
        if pol == "authors":
            return len({info[s]["author_id"] for s in L})
        if pol == "capped":
            return sum(min(v, 3) for v in Counter(info[s]["author_id"] for s in L).values())
        if pol == "nofeed":
            return sum(info[s]["author_id"] not in feeds for s in L)
        if pol == "edges":
            return sum(e["event_created_at"] < c for s in L for e in eb[s])
        if pol == "responders":
            return len({e["source_actor_id"] for s in L for e in eb[s]
                        if e["event_created_at"] < c and e["source_actor_id"] != info[s]["author_id"]})
        return 0

    target = {}

    def tgt(k, d):
        if (k, d) not in target:
            L, c = posts(k, d), cut(d)
            c2 = c + timedelta(hours=24)
            before = {e["source_actor_id"] for s in L for e in eb[s]
                      if e["event_created_at"] < c and e["source_actor_id"] != info[s]["author_id"]}
            after = {e["source_actor_id"] for s in L for e in eb[s]
                     if c <= e["event_created_at"] < c2 and e["source_actor_id"] != info[s]["author_id"]}
            target[(k, d)] = len(after - before)
        return target[(k, d)]

    out = {"n_candidates": len(first), "eval_days": [str(d) for d in sorted(eval_days)],
           "candidates_with_any_target": None}
    rng_bs = np.random.default_rng(seed)
    for b in budgets:
        R = {}
        for pol in POLS:
            r = np.random.default_rng([seed, POLS.index(pol), b])
            per_day, tot = Counter(), []
            for _ in range(reps):
                reviewed, got = set(), 0
                for d in review_days:
                    pool = sorted(k for k in first if first[k] <= d and k not in reviewed)
                    jit = r.random(len(pool)) * 1e-6
                    sc = {k: score(k, d, pol) + jit[i] for i, k in enumerate(pool)}
                    for k in sorted(pool, key=lambda k: -sc[k])[:b]:
                        reviewed.add(k)
                        if d in eval_days:
                            v = tgt(k, d)
                            got += v
                            per_day[d] += v / reps
                tot.append(got)
            R[pol] = {"total": round(float(np.mean(tot)), 2), "ties_95": [float(np.percentile(tot, 2.5)), float(np.percentile(tot, 97.5))],
                      "per_day": {str(d): round(per_day[d], 3) for d in sorted(eval_days)}}
        days = sorted(eval_days)
        for pol in POLS[1:]:
            diff = np.array([R[pol]["per_day"][str(d)] - R["posts"]["per_day"][str(d)] for d in days])
            bs = [diff[rng_bs.integers(0, len(diff), len(diff))].sum() for _ in range(2000)]
            R[pol]["vs_posts"] = round(float(diff.sum()), 2)
            R[pol]["vs_posts_ci"] = [round(float(np.percentile(bs, 2.5)), 2), round(float(np.percentile(bs, 97.5)), 2)]
        diff = np.array([R["authors"]["per_day"][str(d)] - R["nofeed"]["per_day"][str(d)] for d in days])
        bs = [diff[rng_bs.integers(0, len(diff), len(diff))].sum() for _ in range(2000)]
        R["authors_minus_nofeed"] = {"diff": round(float(diff.sum()), 2),
                                     "ci": [round(float(np.percentile(bs, 2.5)), 2), round(float(np.percentile(bs, 97.5)), 2)]}
        out[f"b{b}"] = R
        print("same-unit b", b, {p: (R[p]["total"], R[p].get("vs_posts"), R[p].get("vs_posts_ci")) for p in POLS}, flush=True)
    ks = [k for k in first]
    out["candidates_with_any_target"] = round(sum(any(tgt(k, d) for d in eval_days if first[k] <= d) for k in ks) / max(1, len(ks)), 3)
    return out
