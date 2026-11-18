"""Table 2: each counting rule on both tasks in both windows, plus the fresh-window maturity sensitivity and the
paired difference distinct authors minus zero feed weight (2026-11-15) → tables/dualwin.tex.

Discussion: subsequent responders, three topics a day (main: eval_monitor k3; fresh: eval_contrast cyber k3).
Events: distinct registry-listed claims, five candidates a day, averaged over tie orders (main: eval_registry
exact_b5, engagement and random from story_checks; fresh: crossover_fresh b5 on the 2026-11-15 registry; complete
follow-up: crossover_fresh mature_cand_8d b5; at most three per author in the fresh window: crossover_fresh_capped,
exploratory). Paired differences and 95% intervals: data/paired.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
J = lambda n: json.loads((ROOT / "data" / n).read_text())
EM, ER, ST, SR = J("eval_monitor.json")["primary"]["k3"], J("eval_registry.json")["results"]["exact_b5"], \
    J("story_checks.json")["registry_engagement"], J("story_checks_random.json")["random"]
CD, XFall, XC = J("eval_contrast.json")["cyber"]["monitor"]["k3"], J("crossover_fresh.json"), J("crossover_fresh_capped.json")["b5"]
XF, MT = XFall["b5"], XFall["mature_cand_8d"]["b5"]
PP = J("paired.json")
D = lambda v: f"{v:,.0f}".replace(",", "{,}") if abs(v - round(v)) < 0.05 else f"{v:,.1f}".replace(",", "{,}")
E = lambda v: f"{v:.1f}"
DASH = "---"
rows = [("Posts", EM["P1_posts"]["total"], ER["Q1_posts"]["claims"], CD["P1_posts"]["total"], E(XF["posts"]["claims"]), E(MT["posts"]["claims"])),
        ("$\\le$3 per author", EM["P6_capped"]["total"], ER["Q4_capped"]["claims"], CD["P6_capped"]["total"],
         E(XC["claims"]) + "$^{\\dagger}$", DASH),
        ("Distinct authors", EM["P3_authors"]["total"], ER["Q2_authors"]["claims"], CD["P3_authors"]["total"], E(XF["authors"]["claims"]), E(MT["authors"]["claims"])),
        ("Zero feed weight", EM["P7_nofeed"]["total"], ER["Q5_nofeed"]["claims"], CD["P7_nofeed"]["total"], E(XF["nofeed"]["claims"]), E(MT["nofeed"]["claims"])),
        ("Replies + quotes", EM["P2_edges"]["total"], ST["edges"]["claims_b5"], CD["P2_edges"]["total"], E(XF["edges"]["claims"]), E(MT["edges"]["claims"])),
        ("Distinct responders", EM["P4_responders"]["total"], ST["responders"]["claims_b5"], CD["P4_responders"]["total"],
         E(XF["responders"]["claims"]), E(MT["responders"]["claims"])),
        ("Random order", None, SR["claims_b5"], None, E(XF["random"]["claims"]), E(MT["random"]["claims"]))]
lines = [f"{lab} & {DASH if md is None else D(md)} & {E(me)} & {DASH if fd is None else D(fd)} & {fe} & {mt}\\\\"
         for lab, md, me, fd, fe, mt in rows]
f = lambda v: f"{v:.0f}".replace("-", "$-$")
g = lambda v: f"{v:.1f}".replace("-", "$-$")
lines.append("\\midrule")
lines.append("Authors $-$ zero weight & " + " & ".join([
    f(PP["main_discussion"]["diff"]), g(PP["main_events"]["diff"]), f(PP["fresh_discussion"]["diff"]),
    g(PP["fresh_events"]["diff"]), g(PP["fresh_events_mature"]["diff"])]) + "\\\\")
ci = lambda k, h: f"{h(PP[k]['ci'][0])}, {h(PP[k]['ci'][1])}"
lines.append("\\quad 95\\% interval & " + " & ".join([
    "\\scriptsize " + ci("main_discussion", f), "\\scriptsize " + ci("main_events", g), "\\scriptsize " + ci("fresh_discussion", f),
    "\\scriptsize " + ci("fresh_events", g), "\\scriptsize " + ci("fresh_events_mature", g)]) + "\\\\")
(ROOT / "tables/dualwin.tex").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
