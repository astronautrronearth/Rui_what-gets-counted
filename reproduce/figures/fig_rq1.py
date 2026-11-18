"""RQ1 figure (2026-11-14): who produces event reports and who draws discussion. Merges the former anatomy
(teaser) and feed-case figures.

    python figures/fig_rq1.py → figures/rq1.pdf

(a) Main sample (human-audited feeds), per topic: posts and cross-user participants (data/teaser.json).
(b) Larger collection: posts that name a ransomware victim, share written by accounts flagged by the feed rule
    and replies plus quotes per post (data/story_checks.json, registry_engagement).
(c) Which of the posting accounts mention each listed Canadian ransomware victim (data/cases.json registry).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent.parent
plt.rcParams.update({"pgf.texsystem": "pdflatex", "pgf.rcfonts": False,
                     "pgf.preamble": r"\usepackage[T1]{fontenc}\usepackage[sfdefault]{biolinum}\usepackage{fontawesome5}",
                     "font.family": "sans-serif", "font.size": 7,
                     "axes.spines.top": False, "axes.spines.right": False})
J = lambda n: json.loads((ROOT / "data" / n).read_text())
T, ST, CS, REG = J("teaser.json"), J("story_checks.json")["registry_engagement"], J("cases.json"), J("registry.json")
INK, SEC, GRID, PALE, MUTED = "#222222", "#666666", "#d9d8d3", "#ecebe7", "#8a8984"
C1, C1L, C2 = "#2a78d6", "#a9c9f0", "#eb6834"
NAME = {"data_breach": "Data breach", "vulnerability_cve": "Vulnerability", "unassigned": "(unassigned)",
        "ransomware": "Ransomware", "gov_advisory": "Gov. advisory", "phishing_scam": "Phishing",
        "malware_infostealer": "Malware", "policy_regulation": "Policy", "critical_infrastructure": "Critical infra.",
        "ddos_outage": "DDoS", "fraud_financial": "Fin. fraud"}
HL = {"ransomware", "vulnerability_cve", "critical_infrastructure"}

fig = plt.figure(figsize=(3.33, 1.3))

# ---------------------------------------------------------------- (b) victim-naming posts
fs, ef, en = ST["feed_share_of_candidate_posts"], ST["edges_per_feed_post"], ST["edges_per_nonfeed_post"]
axc = fig.add_axes([0.1, 0.55, 0.36, 0.25])
axd = fig.add_axes([0.1, 0.1, 0.36, 0.25])
for ax_, vals, lab, fmt in ((axc, (100 * fs, 100 * (1 - fs)), "share of posts", "{:.0f}\\%"),
                            (axd, (ef, en), r"\faReply\ per post", "{:.3f}" if ef < 0.1 else "{:.2f}")):
    ax_.barh([0, 1], vals, color=[C1, C1L], height=0.62, lw=0)
    for k, v in enumerate(vals):
        f = "{:.3f}" if (ax_ is axd and v < 0.1) else ("{:.2f}" if ax_ is axd else fmt)
        ax_.text(v + max(vals) * 0.03, k, f.format(v), va="center", ha="left", fontsize=6.4, color=INK)
    ax_.set_yticks([0, 1], [r"\faBullhorn", r"\faUser"], fontsize=7.5)
    ax_.set_ylim(1.5, -0.5)
    ax_.set_xlim(0, max(vals) * 1.4)
    ax_.set_xticks([])
    ax_.spines["bottom"].set_visible(False)
    ax_.tick_params(axis="y", length=0, colors=INK)
    ax_.text(0, -0.7, lab, fontsize=6.2, color=SEC, va="bottom", ha="left", transform=ax_.get_yaxis_transform())
axc.set_title("(a) Victim-naming posts", loc="left", fontsize=7.0, color=INK, x=-0.2, y=1.32, fontweight="bold")

# ---------------------------------------------------------------- (c) registry coverage by account
d = fig.add_axes([0.66, 0.16, 0.33, 0.64])
reg = CS["registry"]
nacc = REG["accounts"]
order = sorted(range(len(reg)), key=lambda i: (-len(reg[i]["accounts_by_rank"]), i))
for j, i in enumerate(order):
    for k in reg[i]["accounts_by_rank"]:
        d.add_patch(Rectangle((j + 0.08, k + 0.08), 0.84, 0.84, fc=C1 if k < 2 else "#9a9994", ec="none"))
    if not reg[i]["accounts_by_rank"]:
        d.add_patch(Rectangle((j + 0.08, 0.08), 0.84, nacc - 0.16, fc="none", ec=GRID, lw=0.5, ls=(0, (2, 1.5))))
d.set_xlim(0, len(reg))
d.set_ylim(nacc, 0)
d.set_xticks([])
d.set_yticks([0.5, 1.5, nacc - 0.5], ["1st", "2nd", f"{nacc}th"], fontsize=6.2)
d.tick_params(axis="y", length=0, colors=INK)
for sp in ("left", "bottom"):
    d.spines[sp].set_visible(False)
d.set_xlabel(f"{REG['events']} listed victims", color=INK, fontsize=6.4, labelpad=1)
d.set_title("(b) Coverage", loc="left", fontsize=7.0, color=INK, x=-0.25, y=1.06, fontweight="bold")

out = ROOT / "figures/rq1.pdf"
fig.savefig(out, backend="pgf", bbox_inches="tight", pad_inches=0.02)
print("wrote", out)
