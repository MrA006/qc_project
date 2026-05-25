"""
findings_results.py
===================
QKD Protocol Comparison: Findings and Results
Compares BB84, E91, and MDI-QKD under identical realistic channel conditions
(10 km optical fibre, 0.2 dB/km attenuation, depolarisation noise 0.8%).

Generates four publication-quality figures saved to plots/findings/:
  Fig 1 – Box-plot distributions (30 runs × 8 metrics × 3 protocols)
  Fig 2 – Distance analysis (1–50 km line plots with CI bands)
  Fig 3 – Radar / spider chart (normalised performance)
  Fig 4 – Key-metric dashboard (bar charts with SD error bars)

Usage (inside the QKD_Simulation venv):
  python findings_results.py
"""

import sys, os, io, re, warnings, math
import contextlib
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
import seaborn as sns

warnings.filterwarnings("ignore")
matplotlib.rcParams.update({
    "font.family":       "DejaVu Sans",
    "font.size":         10,
    "axes.titlesize":    11,
    "axes.labelsize":    10,
    "legend.fontsize":   9,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "figure.dpi":        150,
    "savefig.dpi":       300,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.alpha":        0.35,
    "grid.linestyle":    "--",
})

# ── Path setup ─────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASIC_DIR  = os.path.join(SCRIPT_DIR, "Basic Protocol Set")
OUT_DIR    = os.path.join(SCRIPT_DIR, "Advanced Protocol Set", "plots", "findings")
sys.path.insert(0, BASIC_DIR)

from bb84 import BB84Simulation
from e91  import E91Simulation
from mdi  import MDIQKDSimulation

os.makedirs(OUT_DIR, exist_ok=True)

# ── Visual constants ───────────────────────────────────────────────────────────
PROTOCOLS = ["BB84", "E91", "MDI-QKD"]
COLORS = {"BB84": "#1976D2", "E91": "#F57C00", "MDI-QKD": "#388E3C"}
LIGHT  = {"BB84": "#BBDEFB", "E91": "#FFE0B2", "MDI-QKD": "#C8E6C9"}

METRICS = [
    "Raw Key Rate",
    "QBER",
    "Latency",
    "Channel Loss Rate",
    "Throughput",
    "Communication Overhead",
    "Synchronization Time",
    "Computation Time/Round",
]
UNITS = {
    "Raw Key Rate":           "bits",
    "QBER":                   "%",
    "Latency":                "ms",
    "Channel Loss Rate":      "%",
    "Throughput":             "bits/s",
    "Communication Overhead": "messages",
    "Synchronization Time":   "ms",
    "Computation Time/Round": "ns",
}
SHORT = {
    "Raw Key Rate":           "Raw Key\nRate",
    "QBER":                   "QBER",
    "Latency":                "Latency",
    "Channel Loss Rate":      "Channel\nLoss Rate",
    "Throughput":             "Throughput",
    "Communication Overhead": "Comm.\nOverhead",
    "Synchronization Time":   "Sync\nTime",
    "Computation Time/Round": "Comp.\nTime/Round",
}

PATTERNS = {
    "Raw Key Rate":           r"Raw Key Rate[:\s]+([\d.]+)",
    "QBER":                   r"QBER[:\s]+([\d.]+)%",
    "Latency":                r"Latency[:\s]+([\d.]+)",
    "Channel Loss Rate":      r"Channel Loss Rate[:\s]+([\d.]+)%",
    "Throughput":             r"Throughput[:\s]+([\d.]+)",
    "Communication Overhead": r"Communication Overhead[:\s]+([\d.]+)",
    "Synchronization Time":   r"Synchronization Time[:\s]+([\d.]+)",
    "Computation Time/Round": r"Computation Time/Round[:\s]+([\d.]+)",
}

# ── Simulation helpers ─────────────────────────────────────────────────────────

def _run_silent(cls, **kwargs) -> dict:
    """Run a simulation silently; parse printed metrics."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        sim = cls(**kwargs)
        sim.run_simulation()
    out = buf.getvalue()
    res = {}
    for key, pat in PATTERNS.items():
        m = re.search(pat, out)
        res[key] = float(m.group(1)) if m else np.nan
    return res


def _kwargs(name, distance_km, n_bits=1000):
    if name == "E91":
        return dict(distance_km=distance_km, initial_pairs=n_bits)
    return dict(distance_km=distance_km, initial_bits=n_bits)


CLS_MAP = {"BB84": BB84Simulation, "E91": E91Simulation, "MDI-QKD": MDIQKDSimulation}


def run_batch(n_runs: int = 30, distance_km: float = 10.0) -> dict:
    """
    Run all three protocols n_runs times at a fixed distance.
    Returns {protocol: {metric: [values]}}
    """
    data = {p: {m: [] for m in METRICS} for p in PROTOCOLS}
    for name in PROTOCOLS:
        cls = CLS_MAP[name]
        kw  = _kwargs(name, distance_km)
        print(f"  [{name:8s}]", end="", flush=True)
        for i in range(n_runs):
            res = _run_silent(cls, **kw)
            for m in METRICS:
                data[name][m].append(res[m])
            if (i + 1) % 5 == 0:
                print(f" {i+1}", end="", flush=True)
        print()
    return data


def run_distance_sweep(distances: list, n_runs: int = 8) -> dict:
    """
    Run all protocols across multiple distances.
    Returns {protocol: {metric: [mean_per_distance]}}
    """
    dist_data = {p: {m: {"mean": [], "std": []} for m in METRICS} for p in PROTOCOLS}
    for d in distances:
        print(f"  {d:4.0f} km ", end="", flush=True)
        for name in PROTOCOLS:
            cls = CLS_MAP[name]
            kw  = _kwargs(name, d)
            vals = {m: [] for m in METRICS}
            for _ in range(n_runs):
                res = _run_silent(cls, **kw)
                for m in METRICS:
                    vals[m].append(res[m])
            for m in METRICS:
                arr = np.array(vals[m])
                dist_data[name][m]["mean"].append(np.nanmean(arr))
                dist_data[name][m]["std"].append(np.nanstd(arr))
            print(f"[{name}]", end=" ", flush=True)
        print()
    return dist_data


# ── Figure 1 – Box plots ───────────────────────────────────────────────────────

def fig1_boxplots(data: dict, save=True):
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle(
        "Fig 1 – Performance Metric Distributions Across 30 Runs  (10 km fibre)",
        fontsize=13, fontweight="bold", y=1.01,
    )
    axes = axes.flatten()

    for ax, metric in zip(axes, METRICS):
        positions = [1, 2, 3]
        box_data  = [data[p][metric] for p in PROTOCOLS]

        bp = ax.boxplot(
            box_data,
            positions=positions,
            widths=0.5,
            patch_artist=True,
            medianprops=dict(color="black", linewidth=2),
            whiskerprops=dict(linewidth=1.2),
            capprops=dict(linewidth=1.2),
            flierprops=dict(marker="o", markersize=3, alpha=0.5),
            notch=False,
        )
        for patch, name in zip(bp["boxes"], PROTOCOLS):
            patch.set_facecolor(LIGHT[name])
            patch.set_edgecolor(COLORS[name])
            patch.set_linewidth(1.5)
        for flier, name in zip(bp["fliers"], PROTOCOLS):
            flier.set_markerfacecolor(COLORS[name])
            flier.set_markeredgecolor(COLORS[name])

        ax.set_title(f"{metric}\n({UNITS[metric]})", fontweight="bold")
        ax.set_xticks(positions)
        ax.set_xticklabels(PROTOCOLS, rotation=15, ha="right")
        ax.set_ylabel(UNITS[metric])
        ax.yaxis.set_major_locator(MaxNLocator(5))

    # Legend
    handles = [mpatches.Patch(facecolor=LIGHT[p], edgecolor=COLORS[p],
                               linewidth=1.5, label=p) for p in PROTOCOLS]
    fig.legend(handles=handles, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.03), frameon=True, framealpha=0.9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "Fig1_BoxPlots.png")
    if save:
        fig.savefig(path, bbox_inches="tight")
        print(f"  Saved → {path}")
    return fig


# ── Figure 2 – Distance analysis ──────────────────────────────────────────────

def fig2_distance(dist_data: dict, distances: list, save=True):
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle(
        "Fig 2 – Performance vs. Transmission Distance",
        fontsize=13, fontweight="bold", y=1.01,
    )
    axes = axes.flatten()

    for ax, metric in zip(axes, METRICS):
        for name in PROTOCOLS:
            means = np.array(dist_data[name][metric]["mean"])
            stds  = np.array(dist_data[name][metric]["std"])
            ax.plot(distances, means, marker="o", color=COLORS[name],
                    linewidth=2, markersize=5, label=name)
            ax.fill_between(distances, means - stds, means + stds,
                            color=COLORS[name], alpha=0.15)

        ax.set_title(f"{metric}\n({UNITS[metric]})", fontweight="bold")
        ax.set_xlabel("Distance (km)")
        ax.set_ylabel(UNITS[metric])
        ax.set_xticks(distances)
        ax.yaxis.set_major_locator(MaxNLocator(5))

    # Legend
    handles = [mpatches.Patch(facecolor=COLORS[p], label=p) for p in PROTOCOLS]
    fig.legend(handles=handles, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.03), frameon=True, framealpha=0.9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "Fig2_Distance_Analysis.png")
    if save:
        fig.savefig(path, bbox_inches="tight")
        print(f"  Saved → {path}")
    return fig


# ── Figure 3 – Radar chart ────────────────────────────────────────────────────

def fig3_radar(data: dict, save=True):
    """Normalised spider/radar chart — higher is always better after inversion."""

    # Metrics where lower = better (we invert so "out" = good)
    INVERT = {"QBER", "Channel Loss Rate", "Communication Overhead",
               "Latency", "Synchronization Time", "Computation Time/Round"}

    means = {p: {m: np.nanmean(data[p][m]) for m in METRICS} for p in PROTOCOLS}

    # Build min/max across all protocols for normalisation
    lo = {m: min(means[p][m] for p in PROTOCOLS) for m in METRICS}
    hi = {m: max(means[p][m] for p in PROTOCOLS) for m in METRICS}

    def normalise(val, metric):
        span = hi[metric] - lo[metric]
        if span == 0:
            return 0.5
        norm = (val - lo[metric]) / span          # 0..1 where 1 = worst
        return (1 - norm) if metric in INVERT else norm  # flip: 1 = best

    labels  = [SHORT[m] for m in METRICS]
    N       = len(METRICS)
    angles  = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]                           # close the polygon

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.50, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.50", "0.75", "1.0"], size=8, color="grey")
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)

    for name in PROTOCOLS:
        values  = [normalise(means[name][m], m) for m in METRICS]
        values += values[:1]
        ax.plot(angles, values, color=COLORS[name], linewidth=2.5, label=name)
        ax.fill(angles, values, color=COLORS[name], alpha=0.12)

    ax.set_title(
        "Fig 3 – Normalised Performance Radar\n"
        "(radially outward = better on each dimension)",
        size=12, fontweight="bold", pad=20,
    )
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.15), frameon=True)

    path = os.path.join(OUT_DIR, "Fig3_Radar_Chart.png")
    if save:
        fig.savefig(path, bbox_inches="tight")
        print(f"  Saved → {path}")
    return fig


# ── Figure 4 – Key-metric dashboard ──────────────────────────────────────────

def fig4_dashboard(data: dict, save=True):
    """
    2×2 spotlight on the four most decision-relevant metrics:
      Raw Key Rate, QBER, Throughput, Channel Loss Rate
    Each panel shows grouped bars with SD error bars + individual run dots.
    """
    SPOTLIGHT = ["Raw Key Rate", "QBER", "Throughput", "Channel Loss Rate"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle(
        "Fig 4 – Key Protocol Metrics: Grouped Comparison  (10 km fibre, 30 runs)",
        fontsize=13, fontweight="bold",
    )
    axes = axes.flatten()

    x    = np.arange(len(PROTOCOLS))
    w    = 0.55

    for ax, metric in zip(axes, SPOTLIGHT):
        means = [np.nanmean(data[p][metric]) for p in PROTOCOLS]
        stds  = [np.nanstd(data[p][metric])  for p in PROTOCOLS]

        bars = ax.bar(
            x, means, width=w,
            color=[COLORS[p] for p in PROTOCOLS],
            edgecolor="white", linewidth=0.8,
            yerr=stds, capsize=6, error_kw=dict(elinewidth=1.5, ecolor="black"),
            zorder=3,
        )

        # Scatter individual run values on top
        for i, name in enumerate(PROTOCOLS):
            ys = np.array(data[name][metric])
            xs = np.random.normal(i, 0.06, size=len(ys))
            ax.scatter(xs, ys, color=COLORS[name], s=12, alpha=0.45,
                       edgecolors="white", linewidth=0.4, zorder=4)

        # Value labels on bars
        for bar, mean, std in zip(bars, means, stds):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                mean + std + (max(means) * 0.015),
                f"{mean:.1f}", ha="center", va="bottom", fontsize=8.5,
                fontweight="bold",
            )

        ax.set_title(f"{metric}  ({UNITS[metric]})", fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(PROTOCOLS)
        ax.set_ylabel(UNITS[metric])
        ax.yaxis.set_major_locator(MaxNLocator(6))
        ax.set_xlim(-0.5, len(PROTOCOLS) - 0.5)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "Fig4_Dashboard.png")
    if save:
        fig.savefig(path, bbox_inches="tight")
        print(f"  Saved → {path}")
    return fig


# ── Figure 5 – Overhead breakdown ─────────────────────────────────────────────

def fig5_overhead_security(data: dict, save=True):
    """
    Side-by-side analysis of security overhead vs. performance trade-off.
    Left:  Stacked bar — Latency breakdown proxy
    Right: Scatter — Throughput vs QBER (the key security-performance trade-off)
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    fig.suptitle(
        "Fig 5 – Security–Performance Trade-off Analysis",
        fontsize=13, fontweight="bold",
    )

    # ── Left: Communication overhead vs raw key rate ────────────────
    overhead_means = [np.nanmean(data[p]["Communication Overhead"]) for p in PROTOCOLS]
    keyrate_means  = [np.nanmean(data[p]["Raw Key Rate"])           for p in PROTOCOLS]
    x = np.arange(len(PROTOCOLS))
    w = 0.35

    bars1 = ax1.bar(x - w/2, overhead_means, w, label="Comm. Overhead (messages)",
                    color=[COLORS[p] for p in PROTOCOLS], alpha=0.85, edgecolor="white")
    ax1b  = ax1.twinx()
    bars2 = ax1b.bar(x + w/2, keyrate_means, w, label="Raw Key Rate (bits)",
                     color=[LIGHT[p] for p in PROTOCOLS], edgecolor=[COLORS[p] for p in PROTOCOLS],
                     linewidth=1.5)

    ax1.set_xticks(x)
    ax1.set_xticklabels(PROTOCOLS)
    ax1.set_ylabel("Communication Overhead (messages)", color="black")
    ax1b.set_ylabel("Raw Key Rate (bits)", color="grey")
    ax1.set_title("Communication Cost vs. Key Generation", fontweight="bold")
    ax1.yaxis.set_major_locator(MaxNLocator(6))

    # Combined legend
    h1 = mpatches.Patch(color="grey",  alpha=0.85, label="Comm. Overhead")
    h2 = mpatches.Patch(color="white", edgecolor="grey", linewidth=1.5, label="Raw Key Rate")
    ax1.legend(handles=[h1, h2], loc="upper left", fontsize=8)

    # ── Right: Throughput vs QBER scatter (run-level) ────────────────
    for name in PROTOCOLS:
        thr = np.array(data[name]["Throughput"])
        qbr = np.array(data[name]["QBER"])
        ax2.scatter(qbr, thr, color=COLORS[name], s=55, alpha=0.65,
                    edgecolors="white", linewidth=0.5, label=name, zorder=4)
        # Centroid marker
        ax2.scatter(np.nanmean(qbr), np.nanmean(thr),
                    color=COLORS[name], s=200, marker="D",
                    edgecolors="black", linewidth=1, zorder=5)

    ax2.set_xlabel("QBER (%)  ← lower is more secure")
    ax2.set_ylabel("Throughput (bits/s)  ← higher is faster")
    ax2.set_title("Security vs. Throughput Trade-off\n(diamonds = per-protocol mean)",
                  fontweight="bold")
    ax2.legend(frameon=True, framealpha=0.9)

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "Fig5_Security_Performance.png")
    if save:
        fig.savefig(path, bbox_inches="tight")
        print(f"  Saved → {path}")
    return fig


# ── Figure 6 – Summary heatmap ────────────────────────────────────────────────

def fig6_heatmap(data: dict, save=True):
    """
    Heatmap: rows = protocols, cols = normalised metrics (colour = relative rank).
    Includes absolute mean values as cell annotations.
    """
    INVERT = {"QBER", "Channel Loss Rate", "Communication Overhead",
               "Latency", "Synchronization Time", "Computation Time/Round"}

    # Build matrix of normalised scores (0..1, 1 = best)
    means = {p: {m: np.nanmean(data[p][m]) for m in METRICS} for p in PROTOCOLS}
    lo    = {m: min(means[p][m] for p in PROTOCOLS) for m in METRICS}
    hi    = {m: max(means[p][m] for p in PROTOCOLS) for m in METRICS}

    matrix = []
    annots = []
    for name in PROTOCOLS:
        row, ann = [], []
        for m in METRICS:
            span = hi[m] - lo[m]
            norm = (means[name][m] - lo[m]) / span if span > 0 else 0.5
            score = (1 - norm) if m in INVERT else norm
            row.append(score)
            val = means[name][m]
            ann.append(f"{val:.1f}" if val < 1000 else f"{val:.0f}")
        matrix.append(row)
        annots.append(ann)

    matrix = np.array(matrix)

    fig, ax = plt.subplots(figsize=(14, 4))
    cmap = sns.color_palette("RdYlGn", as_cmap=True)
    sns.heatmap(
        matrix,
        ax=ax,
        annot=np.array(annots),
        fmt="",
        cmap=cmap,
        vmin=0, vmax=1,
        linewidths=1,
        linecolor="white",
        cbar_kws={"label": "Normalised Score  (green = better)", "shrink": 0.8},
        yticklabels=PROTOCOLS,
        xticklabels=[SHORT[m].replace("\n", " ") for m in METRICS],
    )
    ax.set_title(
        "Fig 6 – Protocol Performance Heatmap  "
        "(cell values = absolute means; colour = relative rank)",
        fontweight="bold", pad=12,
    )
    ax.set_yticklabels(PROTOCOLS, rotation=0)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right")

    fig.tight_layout()
    path = os.path.join(OUT_DIR, "Fig6_Heatmap.png")
    if save:
        fig.savefig(path, bbox_inches="tight")
        print(f"  Saved → {path}")
    return fig


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    N_RUNS      = 30          # runs per protocol at 10 km
    N_DIST_RUNS = 8           # runs per protocol per distance
    DISTANCES   = [1, 5, 10, 20, 30, 50]   # km

    print("=" * 60)
    print(" QKD Protocol Comparison — Findings & Results Generator")
    print("=" * 60)

    # ── Batch runs at 10 km ──────────────────────────────────────────
    print(f"\n[1/2] Running {N_RUNS} simulations per protocol at 10 km …")
    batch_data = run_batch(n_runs=N_RUNS, distance_km=10)

    print("\n  Generating Fig 1 – Box plots …")
    fig1_boxplots(batch_data)

    print("  Generating Fig 3 – Radar chart …")
    fig3_radar(batch_data)

    print("  Generating Fig 4 – Key-metric dashboard …")
    fig4_dashboard(batch_data)

    print("  Generating Fig 5 – Security-performance trade-off …")
    fig5_overhead_security(batch_data)

    print("  Generating Fig 6 – Heatmap …")
    fig6_heatmap(batch_data)

    # ── Distance sweep ───────────────────────────────────────────────
    print(f"\n[2/2] Distance sweep {DISTANCES} km "
          f"({N_DIST_RUNS} runs each) …")
    dist_data = run_distance_sweep(DISTANCES, n_runs=N_DIST_RUNS)

    print("\n  Generating Fig 2 – Distance analysis …")
    fig2_distance(dist_data, DISTANCES)

    # ── Console summary ──────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(" RESULTS SUMMARY  (mean ± SD, 30 runs @ 10 km)")
    print("=" * 60)
    header = f"{'Metric':<28}" + "".join(f"{p:>18}" for p in PROTOCOLS)
    print(header)
    print("-" * len(header))
    for m in METRICS:
        row = f"{m:<28}"
        for p in PROTOCOLS:
            arr = np.array(batch_data[p][m])
            row += f"{np.nanmean(arr):>10.2f}±{np.nanstd(arr):<6.2f}"
        print(row)
    print("=" * 60)
    print(f"\nAll figures saved to: {OUT_DIR}")
    print("Done.\n")


if __name__ == "__main__":
    main()
