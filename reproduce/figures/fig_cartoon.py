"""Figure 1 (motivation, soft style, 2026-11-14): post volume and participation diverge. Real numbers from
data/teaser.json (main sample, human-audited feeds). Earlier versions: fig_cartoon_prev.py, fig_cartoon_v3.py.

    python figures/fig_cartoon.py → figures/cartoon.pdf

Each topic: a rounded bar of its posts with one segment per account (the four largest ransomware accounts, all
audited feeds, as dark pills with a robot), and one round avatar per cross-user participant.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

ROOT = Path(__file__).resolve().parent.parent
plt.rcParams.update({"pgf.texsystem": "pdflatex", "pgf.rcfonts": False,
                     "pgf.preamble": r"\usepackage[T1]{fontenc}\usepackage[sfdefault]{biolinum}\usepackage{fontawesome5}",
                     "font.family": "sans-serif", "font.size": 7})
T = json.loads((ROOT / "data/teaser.json").read_text())
INK, MUTED = "#2b2b33", "#8a8790"
BLUE, BLUE_S1, BLUE_S2, BLUE_BG = "#3b6fd8", "#b9d0f6", "#d6e3fa", "#eef4fe"
CORAL, CORAL_BG = "#f07b4f", "#fff0e8"
CARD = "#fbfaf7"

W, H_TOP, H_BOT = 3.33, 1.2, 0.72
H = H_TOP + H_BOT
fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, H_BOT / H, 1, H_TOP / H])
YT = 100 * H_TOP / W
ax.set_xlim(0, 100)
ax.set_ylim(0, YT)
ax.axis("off")

X0, XP = 27.0, 66.0
SCALE = 30.5 / T["ransomware"]["posts"]
BAR = 7.0
ROWS = {"ransomware": (21.2, r"\faLock", "Ransomware"), "critical_infrastructure": (8.0, r"\faIndustry", "Critical infra.")}


def pill(x, y, w, h, fc, ec="none", lw=0, r=None, z=2):
    r = h / 2 if r is None else r
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z)
    ax.add_patch(p)
    return p


# soft cards behind each side
ax.add_patch(FancyBboxPatch((X0 - 1.5, 1.3), XP - X0 - 2.5, YT - 7.3, boxstyle="round,pad=0,rounding_size=2.4",
                            fc=BLUE_BG, ec="none", zorder=0))
ax.add_patch(FancyBboxPatch((XP - 1.5, 1.3), 100 - XP + 0.8, YT - 7.3, boxstyle="round,pad=0,rounding_size=2.4",
                            fc=CORAL_BG, ec="none", zorder=0))
ax.text(X0 + 0.5, YT - 3.0, r"\faFile*\ \ posts, one shade per account", fontsize=6.3, color=BLUE, va="center")
ax.text(XP + 0.5, YT - 3.0, r"\faReply\ \ other accounts replying", fontsize=6.3, color=CORAL, va="center")

for t, (y, icon, name) in ROWS.items():
    d = T[t]
    # topic badge
    ax.add_patch(Circle((3.6, y), 2.6, fc=CARD, ec="#dcd9d2", lw=0.6, zorder=2))
    ax.text(3.6, y, icon, fontsize=6.2, color=INK, ha="center", va="center", zorder=3)
    ax.text(7.4, y, name, fontsize=7.0, fontweight="bold", color=INK, va="center")
    # posts bar: rounded container, segments clipped to it
    total = d["posts"] * SCALE
    clip = pill(X0, y - BAR / 2, total, BAR, fc="none", z=1)
    x = X0
    for k, n in enumerate(d["by_rank"]):
        w = n * SCALE
        big = k < 4 and t == "ransomware"
        seg = Rectangle((x, y - BAR / 2), w, BAR, fc=BLUE if big else (BLUE_S1 if k % 2 else BLUE_S2),
                        ec=BLUE_BG if big else "none", lw=0.9 if big else 0, zorder=2)
        ax.add_patch(seg)
        seg.set_clip_path(clip)
        if big:
            ax.text(x + w / 2, y, r"\faRobot", fontsize=5.4, color="white", ha="center", va="center", zorder=3)
        x += w
    ax.text(x + 1.3, y, f"{d['posts']}", fontsize=7.6, fontweight="bold", color=BLUE, va="center")
    # participants: round avatars
    n, per, pitch = d["cross_participants"], 12, 2.2
    nrow = (n + per - 1) // per
    for i in range(n):
        r_, c = divmod(i, per)
        cx, cy = XP + 1.6 + c * pitch, y + (nrow - 1) * 1.6 - r_ * 3.2
        ax.add_patch(Circle((cx, cy), 1.05, fc=CORAL, ec="white", lw=0.4, zorder=3))
        ax.text(cx, cy - 0.05, r"\faUser", fontsize=3.4, color="white", ha="center", va="center", zorder=4)
    xe = XP + 1.6 + (min(n, per) - 1) * pitch
    ax.text(xe + 2.1, y, f"{n}", fontsize=7.6, fontweight="bold", color=CORAL, va="center")

# ---------------------------------------------------------------- bottom band: how each count weights one feed
bx = fig.add_axes([0, 0, 1, H_BOT / H])
YB = 100 * H_BOT / W
bx.set_xlim(0, 100)
bx.set_ylim(0, YB)
bx.axis("off")
GREY, GREY_BG = "#b9b5ae", "#f1efea"
bx.add_patch(FancyBboxPatch((1.3, 1.0), 97.4, YB - 2.2, boxstyle="round,pad=0,rounding_size=2.4", fc=CARD,
                            ec="#e6e3dc", lw=0.6, zorder=0))
# one flagged account with n = 5 posts about a ranked unit
cy = YB / 2 - 0.3
bx.add_patch(Circle((7.6, cy + 1.2), 3.4, fc=BLUE, ec="none", zorder=2))
bx.text(7.6, cy + 1.2, r"\faBullhorn", fontsize=7.4, color="white", ha="center", va="center", zorder=3)
for k in range(5):
    bx.text(13.0 + k * 0.9, cy + 2.6 - k * 0.9, r"\faFile*", fontsize=6.4, color=BLUE_S1 if k < 4 else BLUE,
            ha="center", va="center", zorder=3 + k)
bx.text(10.6, cy - 5.6, "flagged, 5 posts", fontsize=6.0, color=MUTED, ha="center", va="center")
COUNTS = [(r"\faFile*", "posts", "5", BLUE, BLUE_BG),
          (r"\faUser", "authors", "1", "#3e9c6e", "#ddf3e8"),
          (r"\faBan", "no feeds", "0", GREY, GREY_BG),
          (r"\faReply", "replies", r"$\approx$0", CORAL, CORAL_BG)]
x0, wc, gap = 25.5, 16.9, 1.6
for i, (ic, lab, val, col, bg) in enumerate(COUNTS):
    x = x0 + i * (wc + gap)
    bx.annotate("", xy=(x - 0.2, cy + 0.6), xytext=(19.5, cy + 0.6),
                arrowprops=dict(arrowstyle="-", color="#dcd9d2", lw=0.5, connectionstyle="arc3,rad=0"), zorder=1) if i == 0 else None
    bx.add_patch(FancyBboxPatch((x, 3.2), wc, YB - 6.4, boxstyle="round,pad=0,rounding_size=2.2", fc=bg, ec="none", zorder=2))
    bx.text(x + 3.0, YB - 5.6, ic, fontsize=6.0, color=col, ha="center", va="center", zorder=3)
    bx.text(x + 5.6, YB - 5.6, lab, fontsize=6.0, color=INK, ha="left", va="center", zorder=3)
    bx.text(x + wc / 2, 7.3, val, fontsize=9.5, fontweight="bold", color=col, ha="center", va="center", zorder=3)
bx.annotate("", xy=(x0 - 0.6, cy + 0.6), xytext=(19.6, cy + 0.6),
            arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.6, mutation_scale=5), zorder=1)

out = ROOT / "figures/cartoon.pdf"
fig.savefig(out, backend="pgf", pad_inches=0.0)
print("wrote", out)
