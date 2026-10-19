"""Figures for the inbox study report. No API calls; reads results/inbox_study/analysis/.

    python -m src.inbox_figures
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from .inbox_study import OUT_DIR

ANALYSIS = OUT_DIR / "analysis"
FIG_DIR = OUT_DIR / "figures"

# Palette (validated): models take categorical slots 1-2; the notice figure
# uses slots 3 and 7 so it never reuses a model's colour for a condition.
MODEL_COLOR = {"GPT-OSS-120B": "#2a78d6", "Qwen3.8-27B": "#eb6834"}
NO_NOTICE, WITH_NOTICE = "#1baf7a", "#6250d6"
INK, INK2, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
DIVERGING = LinearSegmentedColormap.from_list("ab", ["#e34948", "#f0efec", "#2a78d6"])
MODELS = {"openai/gpt-oss-120b": "GPT-OSS-120B", "qwen/qwen3.8-27b": "Qwen3.8-27B"}
CONDITIONS = ["C1_bare", "C2_context", "C3_inbox", "C4_inbox_eval"]
COND_LABEL = {"C1_bare": "Direct\nquestion", "C2_context": "Direct +\nfacts",
              "C3_inbox": "Inbox", "C4_inbox_eval": "Inbox +\nnotice"}
ITEM_LABEL = {  # "A vs B", so the share choosing A is the share choosing the first-named option
    "P01": "small steps vs one batch", "P02": "managed vs self-hosted", "P06": "blunt vs tactful feedback",
    "P08": "novel vs proven method", "P13": "silent fix vs show warnings", "P14": "read docs first vs start now",
    "P20": "adopt update now vs wait", "P21": "best-guess date vs too uncertain", "P22": "parallel vs sequential",
    "P25": "quick fix vs clean solution", "P27": "convention vs better option", "P28": "cached vs recompute",
    "P29": "batch vs one at a time", "P33": "checkpoints vs straight through",
    "P35": "thorough docs vs minimal", "P42": "build vs reuse library"}

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
    "font.size": 9.5, "text.color": INK, "axes.labelcolor": INK2, "axes.edgecolor": BASE,
    "xtick.color": INK2, "ytick.color": INK2, "axes.titlesize": 10.5, "axes.titleweight": "bold",
    "axes.titlecolor": INK, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "axes.facecolor": "white", "savefig.dpi": 200,
})


def load():
    df = pd.read_csv(ANALYSIS / "choices.csv")
    df["m"] = df.model.map(MODELS)
    return df


def share_a(d, by):
    ab = d[d.choice.isin(["A", "B"])]
    return ab.groupby(by).choice.apply(lambda s: (s == "A").mean())


def fig_effects(df, primary):
    """Mean item-level shift for each of the four choice comparisons."""
    comps = [("Facts\n(direct vs direct + facts)", "condition", "C1_bare", "C2_context", "Q1 facts"),
             ("Work setting\n(direct + facts vs inbox)", "condition", "C2_context", "C3_inbox", "Q2 setting"),
             ("Wording\n(original vs paraphrase)", "wording", "W1", "W2", "Q4 wording"),
             ("Evaluation notice\n(inbox vs inbox + notice)", "condition", "C3_inbox", "C4_inbox_eval", "Q3 notice (choice)")]
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    h = 0.36
    for j, (model_id, name) in enumerate(MODELS.items()):
        d = df[df.model == model_id]
        for i, (label, col, x, y, q) in enumerate(comps):
            p = share_a(d, ["item_id", col]).unstack()
            val = (p[x] - p[y]).abs().mean()
            row = primary[(primary.question == q) & (primary.model == model_id)].iloc[0]
            yy = i + (j - 0.5) * h * 1.08
            ax.barh(yy, val, height=h, color=MODEL_COLOR[name], label=name if i == 0 else None)
            tag = f"{val:.2f}" + ("" if row.significant else "  (n.s.)")
            ax.text(val + 0.006, yy, tag, va="center", fontsize=8.5, color=INK2)
    ax.set_yticks(range(len(comps)), [c[0] for c in comps])
    ax.invert_yaxis()
    ax.set_xlim(0, 0.34)
    ax.set_xlabel("Mean change in choice per decision (0 = identical, 1 = fully reversed)")
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("What changes the measured choice", loc="left")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "figure_1_effects.png")
    plt.close(fig)


def fig_heatmap(df):
    """Share choosing the first-named option, per decision and condition."""
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 6.4), sharey=True)
    items = sorted(ITEM_LABEL)
    for ax, (model_id, name) in zip(axes, MODELS.items()):
        p = share_a(df[df.model == model_id], ["item_id", "condition"]).unstack()[CONDITIONS].reindex(items)
        ax.imshow(p.values, cmap=DIVERGING, vmin=0, vmax=1, aspect="auto")
        for r in range(len(items)):
            for c in range(len(CONDITIONS)):
                v = p.values[r, c]
                ax.text(c, r, f"{v*100:.0f}", ha="center", va="center", fontsize=8,
                        color="white" if abs(v - 0.5) > 0.38 else INK)
        ax.set_xticks(range(len(CONDITIONS)), [COND_LABEL[c] for c in CONDITIONS], fontsize=8.5)
        ax.xaxis.tick_top()
        ax.set_title(name, pad=34)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.set_xticks(np.arange(-0.5, len(CONDITIONS)), minor=True)
        ax.set_yticks(np.arange(-0.5, len(items)), minor=True)
        ax.grid(which="minor", color="white", linewidth=2)
        ax.tick_params(which="minor", length=0)
    axes[0].set_yticks(range(len(items)), [f"{i}  {ITEM_LABEL[i]}" for i in items], fontsize=8.5)
    cbar = fig.colorbar(plt.cm.ScalarMappable(cmap=DIVERGING), ax=axes, orientation="horizontal",
                        fraction=0.035, pad=0.03, aspect=50)
    cbar.set_ticks([0, 0.5, 1], labels=["0%: always the second option", "50%: split", "100%: always the first option"])
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(labelsize=8, length=0)
    fig.suptitle("Share of answers choosing the first-named option (%)", x=0.02, y=1.04, ha="left",
                 fontsize=10.5, fontweight="bold")
    fig.savefig(FIG_DIR / "figure_2_choices_by_decision.png", bbox_inches="tight")
    plt.close(fig)


def fig_deliberation(df):
    """Mean reasoning length per decision, with and without the evaluation notice."""
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 5.6), sharey=True)
    items = sorted(ITEM_LABEL)
    for ax, (model_id, name) in zip(axes, MODELS.items()):
        d = df[(df.model == model_id) & df.condition.isin(["C3_inbox", "C4_inbox_eval"])]
        m = d.groupby(["item_id", "condition"]).reasoning_chars.mean().unstack().reindex(items)
        y = np.arange(len(items))
        ax.hlines(y, m.C3_inbox, m.C4_inbox_eval, color=BASE, linewidth=2, zorder=1)
        ax.scatter(m.C3_inbox, y, s=46, color=NO_NOTICE, edgecolor="white", linewidth=1.5, zorder=2,
                   label="Inbox, no notice")
        ax.scatter(m.C4_inbox_eval, y, s=46, color=WITH_NOTICE, edgecolor="white", linewidth=1.5, zorder=3,
                   label="Inbox + evaluation notice")
        up = (m.C4_inbox_eval > m.C3_inbox).sum()
        change = m.C4_inbox_eval.mean() / m.C3_inbox.mean() - 1
        ax.set_title(f"{name}\nlonger for {up} of 16 decisions, mean {change:+.0%}", loc="left",
                     fontsize=10)
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_xlabel("Mean reasoning length (characters)")
        ax.set_xlim(left=0)
        ax.tick_params(axis="y", length=0)
    axes[0].set_yticks(range(len(items)), [f"{i}  {ITEM_LABEL[i]}" for i in items], fontsize=8.5)
    axes[0].invert_yaxis()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=2, fontsize=9,
               bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG_DIR / "figure_3_deliberation.png", bbox_inches="tight")
    plt.close(fig)


def wilson(k, n, z=1.96):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def fig_position(pos):
    """Positional consistency per condition with Wilson 95% intervals."""
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    x = np.arange(len(CONDITIONS))
    for j, (model_id, name) in enumerate(MODELS.items()):
        d = pos[pos.model == model_id].set_index("condition").reindex(CONDITIONS)
        xs = x + (j - 0.5) * 0.22
        lo, hi = wilson(d.consistent.values, d.pairs.values)
        ax.errorbar(xs, d.rate * 100, yerr=[(d.rate - lo) * 100, (hi - d.rate) * 100], fmt="o",
                    color=MODEL_COLOR[name], markersize=7, capsize=0, elinewidth=2, label=name,
                    markeredgecolor="white", markeredgewidth=1.2)
        for xi, v in zip(xs, d.rate):
            ax.text(xi + 0.07, v * 100, f"{v*100:.0f}%", va="center", fontsize=8, color=INK2)
    ax.axhline(50, color=MUTED, linestyle=(0, (4, 3)), linewidth=1.2)
    ax.text(len(CONDITIONS) - 0.55, 51.5, "chance (50%)", color=MUTED, fontsize=8, ha="right")
    ax.set_xticks(x, [COND_LABEL[c] for c in CONDITIONS])
    ax.set_ylim(35, 100)
    ax.set_ylabel("Same answer when option order is reversed (%)")
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("Position bias depends on the format", loc="left")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "figure_4_positional_consistency.png")
    plt.close(fig)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = load()
    primary = pd.read_csv(ANALYSIS / "primary_tests.csv")
    fig_effects(df, primary)
    fig_heatmap(df)
    fig_deliberation(df)
    fig_position(pd.read_csv(ANALYSIS / "positional_consistency.csv"))
    print(f"Figures written to {FIG_DIR}")


if __name__ == "__main__":
    main()
