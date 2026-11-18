"""Method figure (compact, 2026-11-14): collection, labels, day split, and the replay of two separate ranking tasks
with a daily cutoff. Process only, no results. Blue: visible at the decision; orange: measured after the cutoff.
Previous version: fig_method_prev.py.

    python figures/fig_method.py → figures/method.pdf
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

ROOT = Path(__file__).resolve().parent.parent
plt.rcParams.update({"pgf.texsystem": "pdflatex", "pgf.rcfonts": False,
                     "pgf.preamble": r"\usepackage[T1]{fontenc}\usepackage[sfdefault]{biolinum}\usepackage{fontawesome5}",
                     "font.family": "sans-serif", "font.size": 6.5})
INK, MUTED, LINE = "#2b2b33", "#8a8790", "#dcd9d2"
BLUE, BLUE_L, ORANGE, ORANGE_L = "#3b6fd8", "#eef4fe", "#f07b4f", "#fff0e8"
MINT, MINT_L, LAV, LAV_L = "#3e9c6e", "#ddf3e8", "#7b6fd0", "#ebe8fb"

fig = plt.figure(figsize=(3.33, 1.6))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 48)
ax.axis("off")


def arrow(x0, y0, x1, y1, c=MUTED):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=c, lw=0.7, mutation_scale=6, shrinkA=0, shrinkB=0))


def badge(x, y, icon, fc, bg, r=2.9, fs=6.6):
    ax.add_patch(Circle((x, y), r, fc=bg, ec="none", zorder=3))
    ax.text(x, y, icon, fontsize=fs, color=fc, ha="center", va="center", zorder=4)


def chip(x, y, icon, label, fc=LAV, bg=LAV_L):
    badge(x, y, icon, fc, bg, r=3.3, fs=7.2)
    ax.text(x, y - 5.6, label, fontsize=6.2, color=INK, ha="center", va="center")


# row 1: collect, label, split the days
chip(5, 42.5, r"\faSearch", "collect")
arrow(10, 42.5, 15, 42.5)
chip(20, 42.5, r"\faTags", "label", MINT, MINT_L)
arrow(25, 42.5, 30, 42.5)
x, y, h = 31, 38.6, 7.6
for n, lab, fc, tc in ((7, "flag feeds", "#f1efea", INK), (12, "develop", "#f1efea", INK), (12, "evaluate", "#d6e3fa", BLUE)):
    w = 69 * n / 31
    ax.add_patch(FancyBboxPatch((x + 0.5, y), w - 1.0, h, boxstyle=f"round,pad=0,rounding_size={h / 2}", fc=fc, ec="none"))
    ax.text(x + w / 2, y + h / 2 + 1.4, lab, ha="center", va="center", fontsize=6.2, color=tc)
    ax.text(x + w / 2, y + h / 2 - 2.2, f"{n} d", ha="center", va="center", fontsize=5.8, color=MUTED)
    x += w

# row 2: replay of one evaluation day d
CUT = 65
ax.add_patch(FancyBboxPatch((0.5, 0.5), CUT - 0.5, 30, boxstyle="round,pad=0,rounding_size=3", fc=BLUE_L, ec="none"))
ax.add_patch(FancyBboxPatch((CUT, 0.5), 99.5 - CUT, 30, boxstyle="round,pad=0,rounding_size=3", fc=ORANGE_L, ec="none"))
ax.plot([CUT, CUT], [0.5, 32.5], color=INK, lw=0.7, ls=(0, (2, 2)))
ax.text(CUT, 33.6, r"\faClock\ cutoff, end of day $d$", fontsize=6.2, color=INK, ha="center", va="bottom")
ax.text(2.5, 28.0, "visible", fontsize=6.2, color=BLUE, fontweight="bold", va="center")
ax.text(97.5, 28.0, "afterwards", fontsize=6.2, color=ORANGE, fontweight="bold", va="center", ha="right")
# evidence icons -> six rules
badge(5.2, 15.5, r"\faFile*", BLUE, "white")
badge(11.5, 15.5, r"\faReply", BLUE, "white")
badge(17.8, 15.5, r"\faBullhorn", BLUE, "white")
ax.text(11.5, 8.6, "posts, replies,\nflagged accounts", fontsize=5.8, color=MUTED, ha="center", va="center", linespacing=0.9)
arrow(21.5, 15.5, 25.5, 15.5)
ax.add_patch(FancyBboxPatch((26, 10.5), 11, 10, boxstyle="round,pad=0,rounding_size=2.5", fc="white", ec="none"))
ax.text(31.5, 15.5, "6\nrules", fontsize=6.2, color=INK, ha="center", va="center", linespacing=0.9)
# two separate ranking tasks
for yy, icon, lab, win, out_icon, out_lab in ((21.5, r"\faComments", "top 3 topics", "posts of day $d$", r"\faUserPlus", "new responders, 24 h"),
                                         (7.5, r"\faFlag", "top 5 victims", "posts up to $d$", r"\faDatabase", r"registry, $\pm$14 d")):
    arrow(37.5, 15.5, 42, yy)
    ax.add_patch(FancyBboxPatch((42.5, yy - 4.5), 20, 9, boxstyle="round,pad=0,rounding_size=2.5", fc="white", ec="none"))
    badge(45.6, yy, icon, "white", BLUE, r=2.5, fs=5.8)
    ax.text(48.5, yy + 1.5, lab, fontsize=6.2, color=INK, ha="left", va="center")
    ax.text(48.5, yy - 2.0, win, fontsize=5.6, color=MUTED, ha="left", va="center")
    arrow(62.8, yy, 67.6, yy, MUTED)
    ax.add_patch(FancyBboxPatch((68, yy - 4.5), 30, 9, boxstyle="round,pad=0,rounding_size=2.5", fc="white", ec="none"))
    badge(71.4, yy, out_icon, "white", ORANGE, r=2.5, fs=5.8)
    ax.text(74.6, yy, out_lab, fontsize=6.2, color=INK, ha="left", va="center")

out = ROOT / "figures/method.pdf"
fig.savefig(out, backend="pgf", pad_inches=0.0)
print("wrote", out)
