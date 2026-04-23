import pandas as pd
from pathlib import Path

ROOT = Path(".")
OUTFILE = ROOT / "artifact_summary_report.txt"

BINARY_COMBINED = ROOT / "all_d_metals/mp_pipeline_results/delta_analysis/all_deltaE_combined.csv"
BINARY_CHEMSYS = ROOT / "all_d_metals/mp_pipeline_results/comparison_plots_top_bottom_binary/tables/chemsys_summary.csv"
BINARY_TOP = ROOT / "all_d_metals/mp_pipeline_results/comparison_plots_top_bottom_binary/tables/top_configurations.csv"
BINARY_BOTTOM = ROOT / "all_d_metals/mp_pipeline_results/comparison_plots_top_bottom_binary/tables/bottom_configurations.csv"

TERNARY_COMBINED = ROOT / "all_3_metals/mp_pipeline_results/delta_analysis_ternary/all_ternary_deltaE_combined.csv"
TERNARY_CHEMSYS = ROOT / "all_3_metals/mp_pipeline_results/comparison_plots_top_bottom_ternary/tables/chemsys_summary.csv"
TERNARY_PAIRS = ROOT / "all_3_metals/mp_pipeline_results/comparison_plots_top_bottom_ternary/tables/pair_summary.csv"
TERNARY_TOP = ROOT / "all_3_metals/mp_pipeline_results/comparison_plots_top_bottom_ternary/tables/top_configurations.csv"
TERNARY_BOTTOM = ROOT / "all_3_metals/mp_pipeline_results/comparison_plots_top_bottom_ternary/tables/bottom_configurations.csv"
TERNARY_STRONG_CHEMSYS = ROOT / "all_3_metals/mp_pipeline_results/comparison_plots_top_bottom_ternary/tables/strongest_chemsys.csv"
TERNARY_WEAK_CHEMSYS = ROOT / "all_3_metals/mp_pipeline_results/comparison_plots_top_bottom_ternary/tables/weakest_chemsys.csv"
TERNARY_STRONG_PAIRS = ROOT / "all_3_metals/mp_pipeline_results/comparison_plots_top_bottom_ternary/tables/strongest_pairs.csv"
TERNARY_WEAK_PAIRS = ROOT / "all_3_metals/mp_pipeline_results/comparison_plots_top_bottom_ternary/tables/weakest_pairs.csv"

CLOSE_TO_ZERO_THRESHOLD = -0.01

def fmt(x, digits=6):
    if pd.isna(x):
        return "NA"
    return f"{float(x):.{digits}f}"

def write_header(f, title):
    f.write("\n" + "=" * 100 + "\n")
    f.write(title + "\n")
    f.write("=" * 100 + "\n")

def require(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

def corr(df, xcol, ycol):
    x = pd.to_numeric(df[xcol], errors="coerce")
    y = pd.to_numeric(df[ycol], errors="coerce")
    ok = x.notna() & y.notna()
    if ok.sum() < 2:
        return float("nan")
    return x[ok].corr(y[ok])

for path in [
    BINARY_COMBINED, BINARY_CHEMSYS, BINARY_TOP, BINARY_BOTTOM,
    TERNARY_COMBINED, TERNARY_CHEMSYS, TERNARY_PAIRS, TERNARY_TOP, TERNARY_BOTTOM,
    TERNARY_STRONG_CHEMSYS, TERNARY_WEAK_CHEMSYS, TERNARY_STRONG_PAIRS, TERNARY_WEAK_PAIRS
]:
    require(path)

binary_df = pd.read_csv(BINARY_COMBINED)
binary_chemsys = pd.read_csv(BINARY_CHEMSYS)
binary_top = pd.read_csv(BINARY_TOP)
binary_bottom = pd.read_csv(BINARY_BOTTOM)

ternary_df = pd.read_csv(TERNARY_COMBINED)
ternary_chemsys = pd.read_csv(TERNARY_CHEMSYS)
ternary_pairs = pd.read_csv(TERNARY_PAIRS)
ternary_top = pd.read_csv(TERNARY_TOP)
ternary_bottom = pd.read_csv(TERNARY_BOTTOM)
ternary_strong_chemsys = pd.read_csv(TERNARY_STRONG_CHEMSYS)
ternary_weak_chemsys = pd.read_csv(TERNARY_WEAK_CHEMSYS)
ternary_strong_pairs = pd.read_csv(TERNARY_STRONG_PAIRS)
ternary_weak_pairs = pd.read_csv(TERNARY_WEAK_PAIRS)

with open(OUTFILE, "w", encoding="utf-8") as f:
    f.write("ARTIFACT SUMMARY REPORT\n")
    f.write("This report uses exact rows from the generated CSV files.\n")

    write_header(f, "BINARY M-L OVERALL")
    f.write(f"rows: {len(binary_df)}\n")
    f.write(f"unique chemsys: {binary_df['chemsys'].nunique()}\n")
    f.write(f"delta_E min: {fmt(binary_df['delta_E'].min())}\n")
    f.write(f"delta_E max: {fmt(binary_df['delta_E'].max())}\n")
    f.write(f"delta_E mean: {fmt(binary_df['delta_E'].mean())}\n")
    f.write(f"dip_cell_length mean: {fmt(binary_df['dip_cell_length'].mean())}\n")

    write_header(f, "BINARY TOP CONFIGURATIONS")
    for i, row in enumerate(binary_top.itertuples(index=False), 1):
        f.write(
            f"{i:2d}. {row.chemsys} | {row.source} | "
            f"delta_E={fmt(row.delta_E)} | dip_cell_length={fmt(row.dip_cell_length)} | "
            f"dip_method={row.dip_method}\n"
        )

    write_header(f, "BINARY BOTTOM CONFIGURATIONS")
    for i, row in enumerate(binary_bottom.itertuples(index=False), 1):
        f.write(
            f"{i:2d}. {row.chemsys} | {row.source} | "
            f"delta_E={fmt(row.delta_E)} | dip_cell_length={fmt(row.dip_cell_length)} | "
            f"dip_method={row.dip_method}\n"
        )

    close_zero_binary = (
        binary_df[binary_df["delta_E"] >= CLOSE_TO_ZERO_THRESHOLD]
        .sort_values(["delta_E", "chemsys"], ascending=[False, True])
        .copy()
    )
    write_header(f, f"ALL BINARY EXAMPLES CLOSE TO ZERO (delta_E >= {CLOSE_TO_ZERO_THRESHOLD})")
    f.write(f"count: {len(close_zero_binary)}\n")
    for row in close_zero_binary.itertuples(index=False):
        f.write(
            f"- {row.chemsys} | {row.source} | "
            f"delta_E={fmt(row.delta_E)} | dip_cell_length={fmt(row.dip_cell_length)} | "
            f"baseline_slope={fmt(row.baseline_slope)}\n"
        )

    write_header(f, "BINARY CHEMSYS THAT APPEAR IN THE CLOSE-TO-ZERO SET")
    if len(close_zero_binary):
        close_zero_binary_chemsys = (
            close_zero_binary.groupby("chemsys", as_index=False)
            .agg(
                count=("delta_E", "size"),
                closest_to_zero=("delta_E", "max"),
                strongest_in_same_chemsys=("delta_E", "min"),
                mean_close_to_zero=("delta_E", "mean"),
            )
            .sort_values(["closest_to_zero", "count"], ascending=[False, False])
        )
        for row in close_zero_binary_chemsys.itertuples(index=False):
            f.write(
                f"- {row.chemsys} | count={int(row.count)} | "
                f"closest_to_zero={fmt(row.closest_to_zero)} | "
                f"strongest_in_same_chemsys={fmt(row.strongest_in_same_chemsys)} | "
                f"mean_close_to_zero={fmt(row.mean_close_to_zero)}\n"
            )

    write_header(f, "BINARY STRONGEST CHEMSYS")
    for i, row in enumerate(binary_chemsys.sort_values("best_delta_E", ascending=True).itertuples(index=False), 1):
        f.write(
            f"{i:2d}. {row.chemsys} | n={int(row.n)} | "
            f"best_delta_E={fmt(row.best_delta_E)} | worst_delta_E={fmt(row.worst_delta_E)} | "
            f"mean_delta_E={fmt(row.mean_delta_E)} | median_delta_E={fmt(row.median_delta_E)}\n"
        )

    write_header(f, "TERNARY M1-M2-L OVERALL")
    f.write(f"rows: {len(ternary_df)}\n")
    f.write(f"unique chemsys: {ternary_df['chemsys'].nunique()}\n")
    f.write(f"unique pairs: {ternary_df[['metal_1','metal_2']].drop_duplicates().shape[0]}\n")
    f.write(f"delta_E min: {fmt(ternary_df['delta_E'].min())}\n")
    f.write(f"delta_E max: {fmt(ternary_df['delta_E'].max())}\n")
    f.write(f"delta_E mean: {fmt(ternary_df['delta_E'].mean())}\n")
    f.write(f"dip_cell_length mean: {fmt(ternary_df['dip_cell_length'].mean())}\n")

    write_header(f, "TERNARY TOP CONFIGURATIONS")
    for i, row in enumerate(ternary_top.itertuples(index=False), 1):
        f.write(
            f"{i:2d}. {row.chemsys} | {row.source} | pair={row.pair} | ligand={row.ligand} | "
            f"delta_E={fmt(row.delta_E)} | dip_cell_length={fmt(row.dip_cell_length)} | "
            f"IE_avg={fmt(row.IE_avg, 2)} | IE_diff={fmt(row.IE_diff, 2)}\n"
        )

    write_header(f, "TERNARY BOTTOM CONFIGURATIONS")
    for i, row in enumerate(ternary_bottom.itertuples(index=False), 1):
        f.write(
            f"{i:2d}. {row.chemsys} | {row.source} | pair={row.pair} | ligand={row.ligand} | "
            f"delta_E={fmt(row.delta_E)} | dip_cell_length={fmt(row.dip_cell_length)} | "
            f"IE_avg={fmt(row.IE_avg, 2)} | IE_diff={fmt(row.IE_diff, 2)}\n"
        )

    close_zero_ternary = (
        ternary_df[ternary_df["delta_E"] >= CLOSE_TO_ZERO_THRESHOLD]
        .sort_values(["delta_E", "chemsys"], ascending=[False, True])
        .copy()
    )
    write_header(f, f"ALL TERNARY EXAMPLES CLOSE TO ZERO (delta_E >= {CLOSE_TO_ZERO_THRESHOLD})")
    f.write(f"count: {len(close_zero_ternary)}\n")
    for row in close_zero_ternary.itertuples(index=False):
        pair = "-".join(sorted([str(row.metal_1), str(row.metal_2)], key=lambda x: x.upper()))
        f.write(
            f"- {row.chemsys} | {row.source} | pair={pair} | ligand={row.ligand} | "
            f"delta_E={fmt(row.delta_E)} | dip_cell_length={fmt(row.dip_cell_length)} | "
            f"baseline_slope={fmt(row.baseline_slope)}\n"
        )

    write_header(f, "TERNARY STRONGEST CHEMSYS")
    for i, row in enumerate(ternary_strong_chemsys.itertuples(index=False), 1):
        f.write(
            f"{i:2d}. {row.chemsys} | ligands={row.ligand_examples} | n_total={int(row.n_total)} | "
            f"best_overall_delta_E={fmt(row.best_overall_delta_E)} | "
            f"worst_overall_delta_E={fmt(row.worst_overall_delta_E)} | "
            f"mean_overall_delta_E={fmt(row.mean_overall_delta_E)}\n"
        )

    write_header(f, "TERNARY WEAKEST CHEMSYS")
    for i, row in enumerate(ternary_weak_chemsys.itertuples(index=False), 1):
        f.write(
            f"{i:2d}. {row.chemsys} | ligands={row.ligand_examples} | n_total={int(row.n_total)} | "
            f"best_overall_delta_E={fmt(row.best_overall_delta_E)} | "
            f"worst_overall_delta_E={fmt(row.worst_overall_delta_E)} | "
            f"mean_overall_delta_E={fmt(row.mean_overall_delta_E)}\n"
        )

    write_header(f, "TERNARY STRONGEST PAIRS")
    for i, row in enumerate(ternary_strong_pairs.itertuples(index=False), 1):
        f.write(
            f"{i:2d}. {row.pair} | ligands={row.ligand_examples} | n_total={int(row.n_total)} | "
            f"best_overall_delta_E={fmt(row.best_overall_delta_E)} | "
            f"worst_overall_delta_E={fmt(row.worst_overall_delta_E)} | "
            f"mean_overall_delta_E={fmt(row.mean_overall_delta_E)}\n"
        )

    write_header(f, "TERNARY WEAKEST PAIRS")
    for i, row in enumerate(ternary_weak_pairs.itertuples(index=False), 1):
        f.write(
            f"{i:2d}. {row.pair} | ligands={row.ligand_examples} | n_total={int(row.n_total)} | "
            f"best_overall_delta_E={fmt(row.best_overall_delta_E)} | "
            f"worst_overall_delta_E={fmt(row.worst_overall_delta_E)} | "
            f"mean_overall_delta_E={fmt(row.mean_overall_delta_E)}\n"
        )

    write_header(f, "TERNARY IONIZATION-ENERGY CHECKS")
    f.write(f"corr(delta_E, IE_avg) in ternary top set: {fmt(corr(ternary_top, 'IE_avg', 'delta_E'), 4)}\n")
    f.write(f"corr(delta_E, IE_diff) in ternary top set: {fmt(corr(ternary_top, 'IE_diff', 'delta_E'), 4)}\n")
    f.write("\nLowest IE_avg examples in ternary top set:\n")
    for row in ternary_top.sort_values("IE_avg", ascending=True).head(10).itertuples(index=False):
        f.write(
            f"- {row.chemsys} | delta_E={fmt(row.delta_E)} | IE_avg={fmt(row.IE_avg, 2)} | IE_diff={fmt(row.IE_diff, 2)}\n"
        )
    f.write("\nHighest IE_avg examples in ternary top set:\n")
    for row in ternary_top.sort_values("IE_avg", ascending=False).head(10).itertuples(index=False):
        f.write(
            f"- {row.chemsys} | delta_E={fmt(row.delta_E)} | IE_avg={fmt(row.IE_avg, 2)} | IE_diff={fmt(row.IE_diff, 2)}\n"
        )
    f.write("\nLowest IE_diff examples in ternary top set:\n")
    for row in ternary_top.sort_values("IE_diff", ascending=True).head(10).itertuples(index=False):
        f.write(
            f"- {row.chemsys} | delta_E={fmt(row.delta_E)} | IE_avg={fmt(row.IE_avg, 2)} | IE_diff={fmt(row.IE_diff, 2)}\n"
        )
    f.write("\nHighest IE_diff examples in ternary top set:\n")
    for row in ternary_top.sort_values("IE_diff", ascending=False).head(10).itertuples(index=False):
        f.write(
            f"- {row.chemsys} | delta_E={fmt(row.delta_E)} | IE_avg={fmt(row.IE_avg, 2)} | IE_diff={fmt(row.IE_diff, 2)}\n"
        )

print(f"Wrote: {OUTFILE.resolve()}")
