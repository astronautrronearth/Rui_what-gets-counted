"""Figure 4 (single column, 2026-11-14): change of each counting rule relative to post volume, on the discussion
task (left) and the event task (right), main window (filled) and fresh window (open).

    python figures/fig_forest.py → figures/forest.pdf

Discussion: subsequent responders, three topics a day; relative difference to posts with 95% day-block bootstrap
interval (main: eval_monitor k3; fresh: eval_contrast cyber k3). Events: listed claims, five candidates a day;
difference to posts divided by posts' claims, 95% day-block interval (main: eval_registry exact_b5; fresh:
crossover_fresh b5); main-window engagement on events was computed post hoc and has a tie-order range only
(story_checks), drawn dotted. Fresh-window capped events: exploratory (crossover_fresh_capped), drawn dashed.
Intervals beyond the axis end in an arrowhead.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent.parent
plt.rcParams.update({"pgf.texsystem": "pdflatex", "pgf.rcfonts": False,
                     "pgf.preamble": r"\usepackage[T1]{fontenc}\usepackage[sfdefault]{biolinum}\usepackage{fontawesome5}",
                     "font.family": "sans-serif", "font.size": 7,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False})
J = lambda n: json.loads((ROOT / "data" / n).read_text())
EM, ER = J("eval_monitor.json")["primary"]["k3"], J("eval_registry.json")["results"]["exact_b5"]
ST = J("story_checks.json")["registry_engagement"]
CD, XF, XC = J("eval_contrast.json")["cyber"]["monitor"]["k3"], J("crossover_fresh.json")["b5"], J("crossover_fresh_capped.json")["b5"]
INK, SEC, GRID, BAND = "#222222", "#6f6e69", "#d9d8d3", "#f4f3ef"
RULES = [("capped", r"$\le$3 per author", "#7fbf9a", "P6_capped", "Q4_capped", None),
         ("authors", "distinct authors", "#2f8f5b", "P3_authors", "Q2_authors", "authors"),
         ("zero", "zero feed weight", "#eb6834", "P7_nofeed", "Q5_nofeed", "nofeed"),
         ("edges", "replies and quotes", "#2a78d6", "P2_edges", None, "edges")]
e0, f0 = ER["Q1_posts"]["claims"], XF["posts"]["claims"]


def disc(win, p):
    v = (EM if win == "main" else CD)[p]
    return 100 * v["vs_posts_rel"], [100 * c for c in v["vs_posts_rel_ci"]], "-"


def event(win, key, q, xf):
    if win == "main":
        if key == "edges":
            return 100 * (ST["edges"]["claims_b5"] - e0) / e0, [100 * (t - e0) / e0 for t in ST["edges"]["claims_95_ties"]], ":"
        v = ER[q]
        return 100 * v["vs_Q1"] / e0, [100 * c / e0 for c in v["vs_Q1_ci"]], "-"
    v = XC if key == "capped" else XF[xf]
    return 100 * v["vs_posts"] / f0, [100 * c / f0 for c in v["vs_posts_ci"]], "--" if key == "capped" else "-"


fig, axes = plt.subplots(1, 2, figsize=(3.33, 1.62), sharey=True)
fig.subplots_adjust(left=0.265, right=0.985, bottom=0.2, top=0.8, wspace=0.2)
LIM = {0: (-20, 100), 1: (-100, 40)}
for j, ax in enumerate(axes):
    lo, hi = LIM[j]
    for i in range(len(RULES)):
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color=BAND, lw=0, zorder=0)
    ax.axvline(0, color=INK, lw=0.6, zorder=1)
    for i, (key, lab, col, p, q, xf) in enumerate(RULES):
        for win, dy in (("main", -0.16), ("fresh", 0.16)):
            x, ci, ls = disc(win, p) if j == 0 else event(win, key, q, xf)
            y = i + dy
            a, b = max(ci[0], lo), min(ci[1], hi)
            ax.plot([a, b], [y, y], color=col, lw=1.0, ls=ls, alpha=0.75, zorder=2, solid_capstyle="butt")
            if ci[1] > hi:
                ax.scatter([hi], [y], marker=">", s=9, color=col, lw=0, zorder=3, clip_on=False)
            if ci[0] < lo:
                ax.scatter([lo], [y], marker="<", s=9, color=col, lw=0, zorder=3, clip_on=False)
            ax.scatter([x], [y], s=17, marker="o", zorder=4, linewidths=0.9,
                       facecolors=col if win == "main" else "white", edgecolors=col)
    ax.set_xlim(lo, hi)
    ax.set_ylim(len(RULES) - 0.5, -0.5)
    ax.tick_params(axis="y", length=0, colors=INK)
    ax.tick_params(axis="x", length=2, colors=INK, labelsize=6.2, pad=1)
    ax.grid(axis="x", color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)
axes[0].set_xticks([0, 50, 100], ["0", "+50", "+100"])
axes[1].set_xticks([-100, -50, 0], ["$-$100", "$-$50", "0"])
axes[0].set_yticks(range(len(RULES)), [r[1] for r in RULES], fontsize=6.6)
axes[0].set_title(r"\faComments\ discussion yield", fontsize=6.8, color=INK, pad=2)
axes[1].set_title(r"\faFlag\ event yield", fontsize=6.8, color=INK, pad=2)
fig.text(0.625, 0.03, "change relative to post volume (\\%)", ha="center", fontsize=6.4, color=SEC)
fig.legend(handles=[Line2D([], [], marker="o", ls="", markersize=4, color=INK, label="main window"),
                    Line2D([], [], marker="o", ls="", markersize=4, markerfacecolor="white", markeredgecolor=INK,
                           label="fresh window")],
           loc="upper center", bbox_to_anchor=(0.625, 1.02), ncol=2, frameon=False, fontsize=6.4,
           handletextpad=0.2, columnspacing=1.2)
out = ROOT / "figures/forest.pdf"
fig.savefig(out, backend="pgf", bbox_inches="tight", pad_inches=0.02)
for j in (0, 1):
    for key, lab, col, p, q, xf in RULES:
        print(j, key, [round(v, 1) if not isinstance(v, (list, str)) else v for v in
                       (disc("main", p) if j == 0 else event("main", key, q, xf))][:2],
              [(disc("fresh", p) if j == 0 else event("fresh", key, q, xf))[0]])
