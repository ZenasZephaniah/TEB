#!/usr/bin/env python3
"""
Create a single-panel binary metal focus plot with automatic label repulsion.

Example:
    python plot_binary_metal_focus.py Sc
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text


ROOT = Path(__file__).resolve().parent
INPUT_CSV = ROOT / "packing_efficiency_results" / "binary" / "tables" / "packing_vs_delta_merged.csv"
OUT_DIR = ROOT / "packing_efficiency_results" / "binary" / "plots"

COLORS = {"O": "#1f77b4", "S": "#d62728"}


def main() -> None:
    metal = sys.argv[1].strip() if len(sys.argv) > 1 else "Sc"

    df = pd.read_csv(INPUT_CSV)
    subset = df[df["chemsys"].astype(str).str.startswith(f"{metal}-")].copy()
    if subset.empty:
        raise SystemExit(f"No binary rows found for metal: {metal}")

    subset["ligand"] = subset["chemsys"].str.split("-").str[1]
    subset = subset.sort_values(["ligand", "packing_fraction", "delta_E"]).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(10, 6.2))
    texts = []

    for ligand in sorted(subset["ligand"].dropna().astype(str).unique()):
        group = subset[subset["ligand"].astype(str) == ligand]
        color = COLORS.get(ligand, "#444444")
        ax.scatter(
            group["packing_fraction"],
            group["delta_E"],
            s=72,
            alpha=0.9,
            label=f"{metal}-{ligand}",
            color=color,
            edgecolors="black",
            linewidths=0.5,
            zorder=3,
        )

        for _, row in group.iterrows():
            text = ax.text(
                row["packing_fraction"],
                row["delta_E"],
                row["source"].replace("_POSCAR", ""),
                fontsize=8,
                color="#222222",
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec=color, alpha=0.92),
                zorder=4,
            )
            texts.append(text)

    adjust_text(
        texts,
        ax=ax,
        expand=(1.15, 1.35),
        force_text=(0.8, 1.2),
        force_static=(0.4, 0.8),
        force_pull=(0.15, 0.15),
        ensure_inside_axes=True,
        only_move={"text": "xy", "static": "xy", "explode": "xy", "pull": "xy"},
        arrowprops=dict(arrowstyle="-", color="#666666", lw=0.8, alpha=0.8),
    )

    x_vals = pd.to_numeric(subset["packing_fraction"], errors="coerce").dropna()
    y_vals = pd.to_numeric(subset["delta_E"], errors="coerce").dropna()
    if not x_vals.empty:
        x_span = max(float(x_vals.max()) - float(x_vals.min()), 1e-6)
        ax.set_xlim(float(x_vals.min()) - 0.06 * x_span, float(x_vals.max()) + 0.10 * x_span)
    if not y_vals.empty:
        y_span = max(float(y_vals.max()) - float(y_vals.min()), 1e-6)
        ax.set_ylim(float(y_vals.min()) - 0.12 * y_span, float(y_vals.max()) + 0.12 * y_span)

    ax.axhline(0.0, color="black", linestyle="--", linewidth=1)
    ax.set_xlabel("Packing fraction (covalent-radius proxy)")
    ax.set_ylabel("delta_E")
    ax.set_title(f"Binary {metal} systems: packing efficiency vs delta_E")
    ax.grid(alpha=0.18)
    ax.legend(title="Chemsys")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{metal.lower()}_metal_packing_vs_delta_adjusted.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
