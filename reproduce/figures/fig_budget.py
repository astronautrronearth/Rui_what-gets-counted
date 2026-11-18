"""Figure 5 (single column, 2026-11-14): event yield against the review budget (1, 5, 10 candidates a day), main
window and fresh window. Listed claims retrieved, averaged over tie orders.

    python figures/fig_budget.py → figures/budget.pdf

Main: eval_registry exact_b{1,5,10} (posts, distinct authors, at most three per author, zero feed weight); the
engagement rank was evaluated at five a day only (story_checks), drawn as a single point. Fresh: crossover_fresh
b{1,5,10}; at most three per author from crossover_fresh_capped (exploratory, dashed).
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
                     "axes.spines.top": False, "axes.spines.right": False})
J = lambda n: json.loads((ROOT / "data" / n).read_text())
ER, ST = J("eval_registry.json")["results"], J("story_checks.json")["registry_engagement"]
XF, XC = J("crossover_fresh.json"), J("crossover_fresh_capped.json")
INK, SEC, GRID = "#222222", "#6f6e69", "#e3e2dd"
B = (1, 5, 10)
STY = {"posts": ("posts", INK), "capped": (r"$\le$3 per author", "#7fbf9a"), "authors": ("distinct authors", "#2f8f5b"),
       "zero": ("zero feed weight", "#eb6834"), "edges": ("replies and quotes", "#2a78d6")}
MAIN = {"posts": [ER[f"exact_b{b}"]["Q1_posts"]["claims"] for b in B],
        "capped": [ER[f"exact_b{b}"]["Q4_capped"]["claims"] for b in B],
        "authors": [ER[f"exact_b{b}"]["Q2_authors"]["claims"] for b in B],
        "zero": [ER[f"exact_b{b}"]["Q5_nofeed"]["claims"] for b in B],
        "edges": [None, ST["edges"]["claims_b5"], None]}
FRESH = {"posts": [XF[f"b{b}"]["posts"]["claims"] for b in B], "capped": [XC[f"b{b}"]["claims"] for b in B],
         "authors": [XF[f"b{b}"]["authors"]["claims"] for b in B], "zero": [XF[f"b{b}"]["nofeed"]["claims"] for b in B],
         "edges": [XF[f"b{b}"]["edges"]["claims"] for b in B]}

fig, axes = plt.subplots(1, 2, figsize=(3.33, 1.42))
fig.subplots_adjust(left=0.1, right=0.985, bottom=0.22, top=0.74, wspace=0.28)
for ax, (title, D) in zip(axes, (("Main window", MAIN), ("Fresh window", FRESH))):
    for key in ("zero", "edges", "capped", "authors", "posts"):
        lab, col = STY[key]
        ys = D[key]
        pts = [(b, y) for b, y in zip(B, ys) if y is not None]
        ls = "--" if (key == "capped" and D is FRESH) else "-"
        if len(pts) > 1:
            ax.plot(*zip(*pts), color=col, lw=1.1 if key != "posts" else 1.3, ls=ls, zorder=3 if key == "posts" else 2)
        ax.scatter(*zip(*pts), s=12, color=col, edgecolors="white", linewidths=0.5, zorder=4)
    ax.set_xticks(B)
    ax.set_xlim(0.3, 10.7)
    ax.set_ylim(0, None)
    ax.grid(axis="y", color=GRID, lw=0.4)
    ax.set_axisbelow(True)
    ax.tick_params(length=2, colors=INK, labelsize=6.2, pad=1)
    ax.set_title(title, fontsize=6.8, color=INK, pad=2, loc="left")
    ax.set_xlabel("candidates a day", fontsize=6.3, color=SEC, labelpad=1)
axes[0].set_ylabel(r"\faFlag\ listed claims", fontsize=6.4, color=INK, labelpad=2)
fig.legend(handles=[Line2D([], [], color=STY[k][1], lw=1.2, marker="o", markersize=3, label=STY[k][0])
                    for k in ("posts", "zero", "capped", "edges", "authors")],
           loc="upper center", bbox_to_anchor=(0.53, 1.03), ncol=3, frameon=False, fontsize=6.2,
           handlelength=1.4, handletextpad=0.3, columnspacing=0.9)
out = ROOT / "figures/budget.pdf"
fig.savefig(out, backend="pgf", bbox_inches="tight", pad_inches=0.02)
print("wrote", out, MAIN, FRESH)
