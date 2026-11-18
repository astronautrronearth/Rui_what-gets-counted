"""Direct paired comparison of distinct authors and zero feed weight (2026-11-14, answers the review request).

Difference distinct authors minus non-feed posts, with a 95% percentile bootstrap over days (2,000 resamples of the
daily differences of one replay, as in the original analyses; seed 20261114). Events: daily listed claims by
listing publication day (main: eval_registry exact_b5 per_pubday; fresh: crossover_fresh b5 per_pubday).
Discussion: per evaluation day (main: eval_monitor k3 per_day; fresh: contrast_perday.json if present).

    python tables/gen_paired.py → data/paired.json
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
J = lambda n: json.loads((ROOT / "data" / n).read_text())
rng = np.random.default_rng(20261114)


def boot(diff):
    diff = np.asarray(diff, float)
    bs = diff[rng.integers(0, len(diff), (100000, len(diff)))].sum(1)   # 100,000 resamples: stable near zero
    return {"diff": round(float(diff.sum()), 2), "ci": [round(float(np.percentile(bs, 2.5)), 2), round(float(np.percentile(bs, 97.5)), 2)],
            "n_days": int(len(diff)), "days_positive": int((diff > 0).sum()), "days_negative": int((diff < 0).sum())}


def by_day(a, b):
    days = sorted(set(a) | set(b))
    return [a.get(d, 0) - b.get(d, 0) for d in days]


out = {}
ER = J("eval_registry.json")["results"]["exact_b5"]
out["main_events"] = boot(by_day(ER["Q2_authors"]["per_pubday"], ER["Q5_nofeed"]["per_pubday"]))
XF = J("crossover_fresh.json")["b5"]
out["fresh_events"] = boot(by_day(XF["authors"]["per_pubday"], XF["nofeed"]["per_pubday"]))
_MC = J("crossover_fresh.json").get("mature_cand_8d", {}).get("b5")
if _MC:   # candidates with full +-14-day follow-up (first post <= 2026-10-31), original 8 evaluation days
    out["fresh_events_mature"] = boot(by_day(_MC["authors"]["per_pubday"], _MC["nofeed"]["per_pubday"]))
EM = J("eval_monitor.json")["primary"]["k3"]
out["main_discussion"] = boot(np.array(EM["P3_authors"]["per_day"]) - np.array(EM["P7_nofeed"]["per_day"]))
pd = ROOT / "data/contrast_perday.json"
if pd.exists():
    C = json.loads(pd.read_text())["cyber"]["monitor"]["k3"]
    out["fresh_discussion"] = boot(np.array(C["P3_authors"]["per_day"]) - np.array(C["P7_nofeed"]["per_day"]))
(ROOT / "data/paired.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
